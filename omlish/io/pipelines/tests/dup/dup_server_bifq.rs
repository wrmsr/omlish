#!/usr/bin/env -S rust-script --cargo-output
//! ```cargo
//! [dependencies]
//! tokio = { version = "1.36", features = ["full"] }
//! anyhow = { version = "1.0" }
//! ```
use anyhow::Context as _;
use std::{net::SocketAddr, time::Duration};
use tokio::{
    io::{AsyncBufReadExt, AsyncWriteExt, BufReader},
    net::{TcpListener, TcpStream},
    sync::mpsc,
    time::sleep,
};

#[derive(Clone, Debug)]
struct Config {
    addr: SocketAddr,

    // Bounded in-flight queue capacity (per-connection)
    inflight: usize,

    // Slow-producer knobs (server-side)
    delay_ms: u64,
    delay_jitter_ms: u64,

    // Response chunking knobs
    lines_per_chunk: usize,

    // Safety limits
    max_line_len: usize,
    max_repeat: usize,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            addr: "127.0.0.1:5003".parse().unwrap(),
            inflight: 8,
            delay_ms: 0,
            delay_jitter_ms: 0,
            lines_per_chunk: 128,
            max_line_len: 64 * 1024,
            max_repeat: 5_000_000,
        }
    }
}

#[derive(Debug)]
struct Request {
    n: usize,
    text: String, // without trailing newline
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let cfg = parse_args(std::env::args().skip(1))?;
    eprintln!("listening on {} cfg={:?}", cfg.addr, cfg);

    let listener = TcpListener::bind(cfg.addr).await?;
    loop {
        let (sock, peer) = listener.accept().await?;
        let cfg2 = cfg.clone();
        tokio::spawn(async move {
            if let Err(e) = handle_conn(sock, cfg2).await {
                eprintln!("[{peer}] conn error: {e:#}");
            }
        });
    }
}

async fn handle_conn(sock: TcpStream, cfg: Config) -> anyhow::Result<()> {
    let peer = sock.peer_addr().ok();
    let (r, w) = sock.into_split();

    // The bounded queue is the explicit per-connection backpressure control:
    // - reader pushes parsed requests into it
    // - writer drains and services them
    // When full, tx.send().await backpressures the reader, which stops reading more bytes.
    let (tx, rx) = mpsc::channel::<Request>(cfg.inflight.max(1));

    let reader_task = tokio::spawn(conn_reader(r, tx, cfg.clone()));
    let writer_task = tokio::spawn(conn_writer(w, rx, cfg.clone(), peer));

    // If either side ends, the connection is effectively done.
    // - If reader ends (EOF or error), tx is dropped -> writer drains then exits.
    // - If writer ends (peer closed, error), reader will fail on further reads or on send if writer is gone.
    let (rr, wr) = tokio::join!(reader_task, writer_task);

    // Prefer reporting the "root cause" rather than join errors.
    rr.context("reader task join failed")??;
    wr.context("writer task join failed")??;

    Ok(())
}

async fn conn_reader(
    r: tokio::net::tcp::OwnedReadHalf,
    tx: mpsc::Sender<Request>,
    cfg: Config,
) -> anyhow::Result<()> {
    let mut reader = BufReader::new(r);
    let mut line = String::new();

    loop {
        // Read count line
        line.clear();
        let nread = read_line_capped(&mut reader, &mut line, cfg.max_line_len).await?;
        if nread == 0 {
            // EOF
            break;
        }
        let n = parse_count(&line, cfg.max_repeat)
            .map_err(|e| anyhow::anyhow!("bad count line {:?}: {e}", line.trim_end()))?;

        // Read text line
        line.clear();
        let nread = read_line_capped(&mut reader, &mut line, cfg.max_line_len).await?;
        if nread == 0 {
            break;
        }
        let text = strip_nl(&line).to_string();

        // This is the critical "bounded in-flight queue" backpressure point:
        // If the writer is slow (slow producer or slow client), the queue fills;
        // send().await waits for capacity; while waiting we are not reading more.
        let req = Request { n, text };
        if tx.send(req).await.is_err() {
            // writer is gone
            break;
        }
    }

    Ok(())
}

async fn conn_writer(
    mut w: tokio::net::tcp::OwnedWriteHalf,
    mut rx: mpsc::Receiver<Request>,
    cfg: Config,
    peer: Option<SocketAddr>,
) -> anyhow::Result<()> {
    while let Some(req) = rx.recv().await {
        // Stream the response. Transport backpressure: write_all().await will stall
        // if the client isn't reading quickly enough.
        stream_response(&mut w, &req.text, req.n, &cfg).await?;

        // Not strictly required, but helps make behavior clearer in tcpdump/strace.
        w.flush().await?;

        if let Some(p) = peer {
            let _ = p;
            // Uncomment for per-request logging:
            // eprintln!("[{p}] served n={} text_len={}", req.n, req.text.len());
        }
    }
    Ok(())
}

async fn stream_response(
    w: &mut tokio::net::tcp::OwnedWriteHalf,
    text: &str,
    n: usize,
    cfg: &Config,
) -> anyhow::Result<()> {
    // Each "line" is TEXT + "\n"
    let mut one_line = Vec::with_capacity(text.len() + 1);
    one_line.extend_from_slice(text.as_bytes());
    one_line.push(b'\n');

    let per = one_line.len().max(1);
    let lpc = cfg.lines_per_chunk.max(1);

    // Avoid absurd allocations if lines_per_chunk is huge.
    // (~1MB cap per chunk)
    let max_chunk_bytes = 1024 * 1024usize;
    let effective_lpc = std::cmp::max(1, std::cmp::min(lpc, max_chunk_bytes / per));

    let mut remaining = n;

    while remaining > 0 {
        let lines = remaining.min(effective_lpc);
        let chunk_bytes = lines * per;

        let mut chunk = Vec::with_capacity(chunk_bytes);
        for _ in 0..lines {
            chunk.extend_from_slice(&one_line);
        }

        // Transport backpressure here:
        w.write_all(&chunk).await?;

        remaining -= lines;

        // Slow-producer simulation between chunks:
        maybe_delay(cfg).await;
    }

    // Terminator blank line: "\n" (so the client sees response end as "\n\n")
    w.write_all(b"\n").await?;
    Ok(())
}

async fn maybe_delay(cfg: &Config) {
    let base = cfg.delay_ms;
    let jit = cfg.delay_jitter_ms;
    if base == 0 && jit == 0 {
        return;
    }

    let jitter = if jit == 0 {
        0i64
    } else {
        // uniform in [-jit, +jit]
        let span = (jit as i64) * 2 + 1;
        let r = (rand_u64() % (span as u64)) as i64 - (jit as i64);
        r
    };

    let d = (base as i64 + jitter).max(0) as u64;
    if d > 0 {
        sleep(Duration::from_millis(d)).await;
    }
}

// Minimal non-crypto jitter PRNG without extra deps
fn rand_u64() -> u64 {
    use std::time::{SystemTime, UNIX_EPOCH};
    let now = SystemTime::now().duration_since(UNIX_EPOCH).unwrap();
    let mut x = now.subsec_nanos() as u64 ^ (now.as_secs() << 32);
    x ^= x << 13;
    x ^= x >> 7;
    x ^= x << 17;
    x
}

async fn read_line_capped<R: AsyncBufReadExt + Unpin>(
    reader: &mut R,
    buf: &mut String,
    max_len: usize,
) -> anyhow::Result<usize> {
    let n = reader.read_line(buf).await?;
    if n == 0 {
        return Ok(0);
    }
    if buf.len() > max_len {
        return Err(anyhow::anyhow!("line too long ({} > max {})", buf.len(), max_len));
    }
    Ok(n)
}

fn strip_nl(s: &str) -> &str {
    s.strip_suffix("\n")
        .map(|x| x.strip_suffix("\r").unwrap_or(x))
        .unwrap_or(s)
}

fn parse_count(line: &str, max_repeat: usize) -> Result<usize, &'static str> {
    let t = line.trim();
    if t.is_empty() {
        return Err("empty");
    }
    if t.starts_with('+') || t.starts_with('-') {
        return Err("sign not allowed");
    }
    let n: usize = t.parse().map_err(|_| "not an integer")?;
    if n > max_repeat {
        return Err("too large");
    }
    Ok(n)
}

// Tiny CLI parser: --addr, --port, --inflight, --delay-ms, --delay-jitter-ms, --lines-per-chunk, --max-repeat, --max-line-len
fn parse_args<I: Iterator<Item = String>>(mut it: I) -> anyhow::Result<Config> {
    let mut cfg = Config::default();
    while let Some(k) = it.next() {
        let v = it.next();
        match (k.as_str(), v.as_deref()) {
            ("--addr", Some(s)) => cfg.addr = s.parse()?,
            ("--port", Some(p)) => {
                let mut a = cfg.addr;
                a.set_port(p.parse()?);
                cfg.addr = a;
            }
            ("--inflight", Some(s)) => cfg.inflight = s.parse()?,
            ("--delay-ms", Some(s)) => cfg.delay_ms = s.parse()?,
            ("--delay-jitter-ms", Some(s)) => cfg.delay_jitter_ms = s.parse()?,
            ("--lines-per-chunk", Some(s)) => cfg.lines_per_chunk = s.parse()?,
            ("--max-line-len", Some(s)) => cfg.max_line_len = s.parse()?,
            ("--max-repeat", Some(s)) => cfg.max_repeat = s.parse()?,
            ("--help", _) | ("-h", _) => {
                eprintln!("Usage:");
                eprintln!("  repeat_server [--addr 127.0.0.1:5003] [--port 5003]");
                eprintln!("               [--inflight N]");
                eprintln!("               [--delay-ms N] [--delay-jitter-ms N]");
                eprintln!("               [--lines-per-chunk N]");
                eprintln!("               [--max-line-len N] [--max-repeat N]");
                std::process::exit(2);
            }
            (unknown, _) => return Err(anyhow::anyhow!("unknown arg: {unknown}")),
        }
    }
    if cfg.inflight == 0 {
        return Err(anyhow::anyhow!("--inflight must be >= 1"));
    }
    Ok(cfg)
}
