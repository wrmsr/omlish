#!/usr/bin/env -S rust-script --cargo-output
//! ```cargo
//! [dependencies]
//! tokio = { version = "1.36", features = ["full"] }
//! anyhow = { version = "1.0" }
//! tokio-native-tls = "0.3"
//! native-tls = "0.2"
//! ```
use anyhow::{anyhow, Context, Result};
use native_tls::{Identity, TlsAcceptor as NativeTlsAcceptor};
use std::path::{Path, PathBuf};
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::{TcpListener, TcpStream};
use tokio::process::Command;
use tokio_native_tls::TlsAcceptor;

const LISTEN_ADDR: &str = "127.0.0.1:8443";
const PKCS12_PASSWORD: &str = "password"; // local-dev only

#[tokio::main]
async fn main() -> Result<()> {
    let dir = make_temp_dir("tokio-https-hello")?;
    let key_pem = dir.join("key.pem");
    let cert_pem = dir.join("cert.pem");
    let pfx = dir.join("identity.pfx");

    if !pfx.exists() {
        generate_self_signed_pfx(&key_pem, &cert_pem, &pfx).await?;
    }

    let identity_bytes = tokio::fs::read(&pfx)
        .await
        .with_context(|| format!("reading {}", pfx.display()))?;
    let identity = Identity::from_pkcs12(&identity_bytes, PKCS12_PASSWORD)
        .context("loading PKCS#12 identity")?;

    let native_acceptor = NativeTlsAcceptor::builder(identity)
        // For local dev. Client certs not requested.
        .build()
        .context("building TLS acceptor")?;
    let tls_acceptor = TlsAcceptor::from(native_acceptor);

    let listener = TcpListener::bind(LISTEN_ADDR)
        .await
        .with_context(|| format!("binding {LISTEN_ADDR}"))?;

    eprintln!("HTTPS hello-world listening on https://{LISTEN_ADDR}/");
    eprintln!("  (self-signed cert generated in: {})", dir.display());
    eprintln!("Try:");
    eprintln!("  curl -k https://{LISTEN_ADDR}/");
    eprintln!();

    loop {
        let (tcp, peer) = listener.accept().await.context("accept")?;
        let tls_acceptor = tls_acceptor.clone();

        tokio::spawn(async move {
            if let Err(e) = handle_conn(tls_acceptor, tcp, peer.to_string()).await {
                eprintln!("[{peer}] error: {e:#}");
            }
        });
    }
}

async fn handle_conn(tls_acceptor: TlsAcceptor, tcp: TcpStream, peer: String) -> Result<()> {
    // TLS handshake
    let mut stream = tls_acceptor
        .accept(tcp)
        .await
        .context("TLS handshake failed")?;

    // Read until end of headers (very small, very minimal HTTP/1.1 parsing)
    let req = read_http_headers(&mut stream).await?;
    let (method, path, version) = parse_request_line(&req)?;

    let (status_line, body) = if method == "GET" && path == "/" {
        let body = format!(
            "hello world (over TLS)\n\
             \n\
             peer: {peer}\n\
             method: {method}\n\
             path: {path}\n\
             version: {version}\n"
        );
        ("HTTP/1.1 200 OK", body)
    } else {
        let body = format!(
            "not found\n\
             \n\
             peer: {peer}\n\
             method: {method}\n\
             path: {path}\n\
             version: {version}\n"
        );
        ("HTTP/1.1 404 Not Found", body)
    };

    let resp = format!(
        "{status_line}\r\n\
         Content-Type: text/plain; charset=utf-8\r\n\
         Content-Length: {}\r\n\
         Connection: close\r\n\
         \r\n\
         {}",
        body.as_bytes().len(),
        body
    );

    stream.write_all(resp.as_bytes()).await.context("write")?;
    let _ = stream.shutdown().await;
    Ok(())
}

async fn read_http_headers<S: AsyncReadExt + Unpin>(s: &mut S) -> Result<Vec<u8>> {
    let mut buf = Vec::with_capacity(1024);
    let mut tmp = [0u8; 512];
    let deadline = tokio::time::Instant::now() + Duration::from_secs(5);

    loop {
        if buf.windows(4).any(|w| w == b"\r\n\r\n") {
            break;
        }
        if buf.len() > 16 * 1024 {
            return Err(anyhow!("request headers too large"));
        }

        let n = tokio::time::timeout_at(deadline, s.read(&mut tmp))
            .await
            .context("timeout while reading request")?
            .context("read failed")?;
        if n == 0 {
            return Err(anyhow!("connection closed before headers complete"));
        }
        buf.extend_from_slice(&tmp[..n]);
    }

    Ok(buf)
}

fn parse_request_line(req: &[u8]) -> Result<(String, String, String)> {
    let s = std::str::from_utf8(req).context("request was not valid utf-8")?;
    let mut lines = s.split("\r\n");
    let first = lines.next().ok_or_else(|| anyhow!("empty request"))?;

    // Very tiny parse: "METHOD SP PATH SP HTTP/1.1"
    let mut parts = first.split_whitespace();
    let method = parts.next().ok_or_else(|| anyhow!("missing method"))?;
    let path = parts.next().ok_or_else(|| anyhow!("missing path"))?;
    let version = parts.next().ok_or_else(|| anyhow!("missing version"))?;

    Ok((method.to_string(), path.to_string(), version.to_string()))
}

async fn generate_self_signed_pfx(key_pem: &Path, cert_pem: &Path, pfx: &Path) -> Result<()> {
    tokio::fs::create_dir_all(
        pfx.parent().ok_or_else(|| anyhow!("pfx has no parent dir"))?,
    )
    .await
    .ok();

    // 1) Generate key + self-signed cert
    // openssl req -x509 -newkey rsa:2048 -nodes -keyout key.pem -out cert.pem -days 365 -subj "/CN=localhost"
    run_openssl(&[
        "req",
        "-x509",
        "-newkey",
        "rsa:2048",
        "-nodes",
        "-keyout",
        key_pem.to_str().unwrap(),
        "-out",
        cert_pem.to_str().unwrap(),
        "-days",
        "365",
        "-subj",
        "/CN=localhost",
    ])
    .await
    .context("generating self-signed cert")?;

    // 2) Package into PKCS#12 for native-tls Identity
    // openssl pkcs12 -export -out identity.pfx -inkey key.pem -in cert.pem -passout pass:password -name localhost
    run_openssl(&[
        "pkcs12",
        "-export",
        "-out",
        pfx.to_str().unwrap(),
        "-inkey",
        key_pem.to_str().unwrap(),
        "-in",
        cert_pem.to_str().unwrap(),
        "-passout",
        &format!("pass:{PKCS12_PASSWORD}"),
        "-name",
        "localhost",
    ])
    .await
    .context("creating PKCS#12 identity")?;

    Ok(())
}

async fn run_openssl(args: &[&str]) -> Result<()> {
    let out = Command::new("openssl")
        .args(args)
        .output()
        .await
        .with_context(|| format!("failed to spawn openssl {:?}", args))?;

    if !out.status.success() {
        return Err(anyhow!(
            "openssl {:?} failed (status: {})\nstdout:\n{}\nstderr:\n{}",
            args,
            out.status,
            String::from_utf8_lossy(&out.stdout),
            String::from_utf8_lossy(&out.stderr),
        ));
    }

    Ok(())
}

fn make_temp_dir(prefix: &str) -> Result<PathBuf> {
    let mut dir = std::env::temp_dir();
    let pid = std::process::id();
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or(Duration::from_secs(0))
        .as_millis();
    dir.push(format!("{prefix}-{pid}-{now}"));
    std::fs::create_dir_all(&dir).with_context(|| format!("creating {}", dir.display()))?;
    Ok(dir)
}
