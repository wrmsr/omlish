#!/usr/bin/env -S rust-script --cargo-output
//! ```cargo
//! [dependencies]
//! tokio = { version = "1.36", features = ["full"] }
//! anyhow = { version = "1.0" }
//! ```
use std::{net::SocketAddr, time::Duration};
use tokio::{
    io::{AsyncBufReadExt, AsyncWriteExt, BufReader},
    net::{TcpListener, TcpStream},
    time::sleep,
};

#[derive(Clone, Debug)]
struct Config {
    // listen
    addr: SocketAddr,

    // slow producer knobs (server-side)
    delay_ms: u64,
    delay_jitter_ms: u64,

    // response chunking knobs
    lines_per_chunk: usize,

    // safety knobs
    max_line_len: usize,
    max_repeat: usize,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            addr: "127.0.0.1:5003".parse().unwrap(),
            delay_ms: 0,
            delay_jitter_ms: 0,
            lines_per_chunk: 128,
            max_line_len: 64 * 1024,
            max_repeat: 5_000_000,
        }
    }
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
    let (r, mut w) = sock.into_split();
    let mut reader = BufReader::new(r);

    // Application backpressure strategy:
    // - We DO NOT read another request while streaming the current response.
    // - This keeps per-connection memory bounded without needing an explicit queue.
    //
    // Tokio note: `read_line` buffers; we cap with `max_line_len` and clear between reads.

    let mut line = String::new();

    loop {
        // Read count line
        line.clear();
        let nread = read_line_capped(&mut reader, &mut line, cfg.max_line_len).await?;
        if nread == 0 {
            // EOF
            return Ok(());
        }
        let n = parse_count(&line, cfg.max_repeat)
            .map_err(|e| anyhow::anyhow!("bad count line {:?}: {e}", line.trim_end()))?;

        // Read text line
        line.clear();
        let nread = read_line_capped(&mut reader, &mut line, cfg.max_line_len).await?;
        if nread == 0 {
            return Ok(());
        }
        let text = strip_nl(&line);

        // Produce/stream response (this is where transport backpressure happens naturally):
        // - If the client reads slowly, write_all().await will stall.
        // - While stalled, we are NOT reading further requests (app backpressure).
        stream_response(&mut w, text, n, &cfg).await?;

        // Optionally flush; not strictly required with write_all but can help in some setups.
        w.flush().await?;
        if let Some(p) = peer {
            // uncomment if you want per-request debug:
            // eprintln!("[{p}] served n={n} text_len={}", text.len());
            let _ = p;
        }
    }
}

async fn stream_response(
    w: &mut tokio::net::tcp::OwnedWriteHalf,
    text: &str,
    n: usize,
    cfg: &Config,
) -> anyhow::Result<()> {
    // Each "line" is TEXT + "\n".
    // We'll batch multiple lines into a chunk to reduce syscalls, like Netty chunking.
    let mut one_line = Vec::with_capacity(text.len() + 1);
    one_line.extend_from_slice(text.as_bytes());
    one_line.push(b'\n');

    let per = one_line.len();
    let lpc = cfg.lines_per_chunk.max(1);

    // Cap chunk buffer so we don't allocate absurdly large buffers for huge lines_per_chunk.
    // (You can tune this; here we cap at ~1MB.)
    let max_chunk_bytes = 1024 * 1024usize;
    let effective_lpc = std::cmp::max(1, std::cmp::min(lpc, max_chunk_bytes / per.max(1)));

    let mut remaining = n;

    while remaining > 0 {
        let lines = remaining.min(effective_lpc);
        let chunk_bytes = lines * per;

        let mut chunk = Vec::with_capacity(chunk_bytes);
        for _ in 0..lines {
            chunk.extend_from_slice(&one_line);
        }

        // Transport backpressure: this await will slow down if client isn't reading.
        w.write_all(&chunk).await?;

        remaining -= lines;

        // Slow-producer: delay between chunks (simulates upstream slowness).
        maybe_delay(cfg).await;
    }

    // Terminator blank line: "\n"
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
        0
    } else {
        // uniform [-jit, +jit]
        let span = (jit as i64) * 2 + 1;
        let r = (rand_u64() % (span as u64)) as i64 - (jit as i64);
        r
    };

    let d = (base as i64 + jitter).max(0) as u64;
    if d > 0 {
        sleep(Duration::from_millis(d)).await;
    }
}

// Minimal rand without adding deps (not crypto; just for jitter).
fn rand_u64() -> u64 {
    use std::time::{SystemTime, UNIX_EPOCH};
    let now = SystemTime::now().duration_since(UNIX_EPOCH).unwrap();
    // xorshift-ish on nanos
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
    // Note: read_line appends. We clear buf at call sites.
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

// Extremely small CLI parsing: --port, --delay-ms, --delay-jitter-ms, --lines-per-chunk, --max-repeat, --max-line-len
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
            ("--delay-ms", Some(s)) => cfg.delay_ms = s.parse()?,
            ("--delay-jitter-ms", Some(s)) => cfg.delay_jitter_ms = s.parse()?,
            ("--lines-per-chunk", Some(s)) => cfg.lines_per_chunk = s.parse()?,
            ("--max-line-len", Some(s)) => cfg.max_line_len = s.parse()?,
            ("--max-repeat", Some(s)) => cfg.max_repeat = s.parse()?,
            ("--help", _) | ("-h", _) => {
                eprintln!("Usage:");
                eprintln!("  repeat_server [--addr 127.0.0.1:5003] [--port 5003]");
                eprintln!("               [--delay-ms N] [--delay-jitter-ms N]");
                eprintln!("               [--lines-per-chunk N] [--max-line-len N] [--max-repeat N]");
                std::process::exit(2);
            }
            (unknown, _) => return Err(anyhow::anyhow!("unknown arg: {unknown}")),
        }
    }
    Ok(cfg)
}
