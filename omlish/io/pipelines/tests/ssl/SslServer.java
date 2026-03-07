//usr/bin/true; exec om java run "$0" "$@"
/* @omlish-jdeps [
    "io.netty:netty-all:4.2.9.FINAL"
] */
package com.wrmsr;

import io.netty.bootstrap.ServerBootstrap;
import io.netty.buffer.ByteBuf;
import io.netty.buffer.Unpooled;
import io.netty.channel.*;
import io.netty.channel.nio.NioEventLoopGroup;
import io.netty.channel.socket.SocketChannel;
import io.netty.channel.socket.nio.NioServerSocketChannel;
import io.netty.handler.codec.http.*;
import io.netty.handler.ssl.SslContext;
import io.netty.handler.ssl.SslContextBuilder;
import io.netty.handler.ssl.SslHandler;
import io.netty.util.CharsetUtil;

import javax.net.ssl.SSLSession;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;

import static io.netty.handler.codec.http.HttpHeaderNames.*;
import static io.netty.handler.codec.http.HttpHeaderValues.*;
import static io.netty.handler.codec.http.HttpResponseStatus.*;
import static io.netty.handler.codec.http.HttpVersion.HTTP_1_1;

public class SslServer {
    static final String HOST = "127.0.0.1";
    static final int PORT = 8443;

    public static void main(String[] args) throws Exception {
        Path tmpDir = Files.createTempDirectory("netty-https-hello-");
        Path keyPem = tmpDir.resolve("key.pem");
        Path certPem = tmpDir.resolve("cert.pem");

        ensureOpensslOnPath();
        generateSelfSignedCertWithOpenssl(keyPem, certPem);

        SslContext sslCtx = SslContextBuilder.forServer(certPem.toFile(), keyPem.toFile()).build();

        EventLoopGroup boss = new NioEventLoopGroup(1);
        EventLoopGroup worker = new NioEventLoopGroup();

        try {
            ServerBootstrap b = new ServerBootstrap()
                    .group(boss, worker)
                    .channel(NioServerSocketChannel.class)
                    .childHandler(new ChannelInitializer<SocketChannel>() {
                        @Override
                        protected void initChannel(SocketChannel ch) {
                            ChannelPipeline p = ch.pipeline();
                            // TLS first
                            p.addLast("ssl", sslCtx.newHandler(ch.alloc()));
                            // HTTP
                            p.addLast("httpCodec", new HttpServerCodec());
                            // Keep it simple: aggregate to FullHttpRequest
                            p.addLast("aggregator", new HttpObjectAggregator(1 << 20));
                            // Handler
                            p.addLast("handler", new HelloHandler());
                        }
                    });

            Channel ch = b.bind(HOST, PORT).sync().channel();

            System.err.println("HTTPS hello-world listening on https://" + HOST + ":" + PORT + "/");
            System.err.println("  (self-signed cert generated in: " + tmpDir + ")");
            System.err.println("Try:");
            System.err.println("  curl -k https://" + HOST + ":" + PORT + "/");
            System.err.println();

            ch.closeFuture().sync();
        } finally {
            boss.shutdownGracefully();
            worker.shutdownGracefully();
            // Temp dir cleanup is optional; leaving it can help debugging.
            // deleteRecursive(tmpDir);
        }
    }

    static final class HelloHandler extends SimpleChannelInboundHandler<FullHttpRequest> {
        @Override
        protected void channelRead0(ChannelHandlerContext ctx, FullHttpRequest req) {
            boolean keepAlive = HttpUtil.isKeepAlive(req);

            String method = req.method().name();
            String uri = req.uri();

            String peer = String.valueOf(ctx.channel().remoteAddress());

            // TLS session info
            String tlsInfo = "";
            SslHandler ssl = ctx.pipeline().get(SslHandler.class);
            if (ssl != null) {
                try {
                    SSLSession sess = ssl.engine().getSession();
                    tlsInfo =
                            "tls_protocol: " + sess.getProtocol() + "\n" +
                            "tls_cipher:   " + sess.getCipherSuite() + "\n";
                } catch (Exception ignored) {
                }
            }

            FullHttpResponse resp;
            if ("GET".equals(method) && "/".equals(uri)) {
                String body =
                        "hello world (over TLS)\n\n" +
                        "time:        " + Instant.now() + "\n" +
                        "peer:        " + peer + "\n" +
                        "method:      " + method + "\n" +
                        "path:        " + uri + "\n" +
                        "http:        " + req.protocolVersion().text() + "\n\n" +
                        tlsInfo;

                ByteBuf content = Unpooled.copiedBuffer(body, CharsetUtil.UTF_8);
                resp = new DefaultFullHttpResponse(HTTP_1_1, OK, content);
                resp.headers().set(CONTENT_TYPE, "text/plain; charset=utf-8");
                resp.headers().setInt(CONTENT_LENGTH, content.readableBytes());
            } else {
                ByteBuf content = Unpooled.copiedBuffer("not found\n", CharsetUtil.UTF_8);
                resp = new DefaultFullHttpResponse(HTTP_1_1, NOT_FOUND, content);
                resp.headers().set(CONTENT_TYPE, "text/plain; charset=utf-8");
                resp.headers().setInt(CONTENT_LENGTH, content.readableBytes());
            }

            if (keepAlive) {
                resp.headers().set(CONNECTION, HttpHeaderValues.KEEP_ALIVE);
                ctx.writeAndFlush(resp);
            } else {
                resp.headers().set(CONNECTION, CLOSE);
                ctx.writeAndFlush(resp).addListener(ChannelFutureListener.CLOSE);
            }
        }

        @Override
        public void exceptionCaught(ChannelHandlerContext ctx, Throwable cause) {
            System.err.println("[conn " + ctx.channel().remoteAddress() + "] error: " + cause);
            ctx.close();
        }
    }

    static void ensureOpensslOnPath() throws IOException, InterruptedException {
        Process p = new ProcessBuilder("openssl", "version")
                .redirectErrorStream(true)
                .start();
        String out = readAll(p.getInputStream());
        int rc = p.waitFor();
        if (rc != 0) {
            throw new RuntimeException("openssl not found or not working (rc=" + rc + "):\n" + out);
        }
    }

    static void generateSelfSignedCertWithOpenssl(Path keyPem, Path certPem) throws IOException, InterruptedException {
        // openssl req -x509 -newkey rsa:2048 -nodes -keyout key.pem -out cert.pem -days 365 -subj "/CN=localhost"
        List<String> cmd = new ArrayList<>();
        cmd.add("openssl");
        cmd.add("req");
        cmd.add("-x509");
        cmd.add("-newkey");
        cmd.add("rsa:2048");
        cmd.add("-nodes");
        cmd.add("-keyout");
        cmd.add(keyPem.toString());
        cmd.add("-out");
        cmd.add(certPem.toString());
        cmd.add("-days");
        cmd.add("365");
        cmd.add("-subj");
        cmd.add("/CN=localhost");

        Process p = new ProcessBuilder(cmd)
                .redirectErrorStream(true)
                .start();

        String out = readAll(p.getInputStream());
        int rc = p.waitFor();
        if (rc != 0) {
            throw new RuntimeException("openssl cert generation failed (rc=" + rc + "):\n" + out);
        }
    }

    static String readAll(InputStream is) throws IOException {
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        byte[] buf = new byte[8192];
        int n;
        while ((n = is.read(buf)) != -1) {
            baos.write(buf, 0, n);
        }
        return baos.toString(StandardCharsets.UTF_8);
    }

    // Optional helper if you want to clean up temp files; commented-out above.
    static void deleteRecursive(Path root) throws IOException {
        if (!Files.exists(root)) return;
        Files.walk(root)
                .sorted((a, b) -> b.getNameCount() - a.getNameCount()) // children first
                .forEach(p -> {
                    try { Files.deleteIfExists(p); } catch (IOException ignored) {}
                });
    }
}