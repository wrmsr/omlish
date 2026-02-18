/*
 * Netty TCP server with explicit flow control + streaming responses + optional slow-producer delay.
 *
 * Protocol:
 *   Request:  N "\n" TEXT "\n"
 *   Response: (TEXT "\n") repeated N times, then "\n" (blank line terminator)
 *
 * Quick test:
 *   printf '3\nhi\n' | nc localhost 5003
 *
 * Slow producer:
 *   java ... Server --port 5003 --delay-ms 2 --delay-jitter-ms 2 --lines-per-chunk 16
 *
 * Flow control:
 * - AUTO_READ=false and handler calls ctx.read() only when ready.
 * - Reacts to channel writability (watermarks).
 */
package com.wrmsr;

import io.netty.bootstrap.ServerBootstrap;
import io.netty.buffer.ByteBuf;
import io.netty.buffer.ByteBufAllocator;
import io.netty.channel.Channel;
import io.netty.channel.ChannelFuture;
import io.netty.channel.ChannelFutureListener;
import io.netty.channel.ChannelHandlerContext;
import io.netty.channel.ChannelInitializer;
import io.netty.channel.ChannelOption;
import io.netty.channel.ChannelPipeline;
import io.netty.channel.EventLoopGroup;
import io.netty.channel.MultiThreadIoEventLoopGroup;
import io.netty.channel.SimpleChannelInboundHandler;
import io.netty.channel.WriteBufferWaterMark;
import io.netty.channel.nio.NioIoHandler;
import io.netty.channel.socket.SocketChannel;
import io.netty.channel.socket.nio.NioServerSocketChannel;
import io.netty.handler.codec.LineBasedFrameDecoder;
import io.netty.handler.codec.string.StringDecoder;
import io.netty.handler.logging.LogLevel;
import io.netty.handler.logging.LoggingHandler;
import io.netty.handler.stream.ChunkedInput;
import io.netty.handler.stream.ChunkedWriteHandler;
import io.netty.util.CharsetUtil;
import io.netty.util.concurrent.EventExecutor;
import io.netty.util.concurrent.Future;
import io.netty.util.concurrent.Promise;

import java.util.Objects;
import java.util.concurrent.ThreadLocalRandom;
import java.util.concurrent.TimeUnit;

public final class DupServer
{
    static final int DEFAULT_PORT = 5003;

    static final int WRITE_BUFFER_LOW_WATER_MARK = 64 * 1024;
    static final int WRITE_BUFFER_HIGH_WATER_MARK = 256 * 1024;

    static final int MAX_LINE_LENGTH = 64 * 1024;

    public static void main(String[] args)
            throws Exception
    {
        Args a = Args.parse(args);

        EventLoopGroup group = new MultiThreadIoEventLoopGroup(NioIoHandler.newFactory());
        try {
            ServerBootstrap b = new ServerBootstrap();
            b.option(ChannelOption.SO_BACKLOG, 1024);

            b.group(group)
                    .channel(NioServerSocketChannel.class)
                    .handler(new LoggingHandler(LogLevel.INFO))
                    .childOption(ChannelOption.AUTO_READ, false)
                    .childOption(ChannelOption.WRITE_BUFFER_WATER_MARK,
                            new WriteBufferWaterMark(WRITE_BUFFER_LOW_WATER_MARK, WRITE_BUFFER_HIGH_WATER_MARK))
                    .childHandler(new Initializer(a));

            Channel ch = b.bind(a.port).sync().channel();
            System.err.println("Listening on 127.0.0.1:" + a.port +
                    " delayMs=" + a.delayMs + " delayJitterMs=" + a.delayJitterMs +
                    " linesPerChunk=" + a.linesPerChunk);
            ch.closeFuture().sync();
        }
        finally {
            group.shutdownGracefully();
        }
    }

    // --- args parsing (minimal, no deps) ---

    static final class Args
    {
        final int port;
        final int delayMs;
        final int delayJitterMs;
        final int linesPerChunk;

        Args(int port, int delayMs, int delayJitterMs, int linesPerChunk)
        {
            this.port = port;
            this.delayMs = delayMs;
            this.delayJitterMs = delayJitterMs;
            this.linesPerChunk = linesPerChunk;
        }

        static Args parse(String[] args)
        {
            int port = DEFAULT_PORT;
            int delayMs = 0;
            int delayJitterMs = 0;
            int linesPerChunk = 128;

            for (int i = 0; i < args.length; i++) {
                String k = args[i];
                String v = (i + 1 < args.length) ? args[i + 1] : null;

                if ("--port".equals(k) && v != null) {
                    port = Integer.parseInt(v);
                    i++;
                }
                else if ("--delay-ms".equals(k) && v != null) {
                    delayMs = Integer.parseInt(v);
                    i++;
                }
                else if ("--delay-jitter-ms".equals(k) && v != null) {
                    delayJitterMs = Integer.parseInt(v);
                    i++;
                }
                else if ("--lines-per-chunk".equals(k) && v != null) {
                    linesPerChunk = Integer.parseInt(v);
                    i++;
                }
                else if ("--help".equals(k) || "-h".equals(k)) {
                    usageAndExit();
                }
                else {
                    System.err.println("Unknown arg: " + k);
                    usageAndExit();
                }
            }

            if (delayMs < 0 || delayJitterMs < 0) {
                usageAndExit();
            }
            if (linesPerChunk <= 0) {
                usageAndExit();
            }

            return new Args(port, delayMs, delayJitterMs, linesPerChunk);
        }

        static void usageAndExit()
        {
            System.err.println("Usage: Server [--port N] [--delay-ms N] [--delay-jitter-ms N] [--lines-per-chunk N]");
            System.exit(2);
        }
    }

    static final class Initializer
            extends ChannelInitializer<SocketChannel>
    {
        private final Args a;

        Initializer(Args a)
        {
            this.a = a;
        }

        @Override
        protected void initChannel(SocketChannel ch)
        {
            ChannelPipeline p = ch.pipeline();

            p.addLast(new LineBasedFrameDecoder(MAX_LINE_LENGTH, true, true));
            p.addLast(new StringDecoder(CharsetUtil.US_ASCII));

            p.addLast(new ChunkedWriteHandler());
            p.addLast(new FlowControlledRepeatServerHandler(a.delayMs, a.delayJitterMs, a.linesPerChunk));
        }
    }

    /**
     * Application flow control:
     * - Accept exactly one request at a time while streaming response.
     * - AUTO_READ=false; calls ctx.read() only when:
     * idle (no response in flight) AND writable.
     */
    public static final class FlowControlledRepeatServerHandler
            extends SimpleChannelInboundHandler<String>
    {
        private enum State
        {WANT_COUNT, WANT_TEXT}

        private State state = State.WANT_COUNT;
        private int repeatCount;

        private final int delayMs;
        private final int delayJitterMs;
        private final int linesPerChunk;

        private boolean responseInFlight = false;
        private boolean readPending = false;

        FlowControlledRepeatServerHandler(int delayMs, int delayJitterMs, int linesPerChunk)
        {
            this.delayMs = delayMs;
            this.delayJitterMs = delayJitterMs;
            this.linesPerChunk = linesPerChunk;
        }

        @Override
        public void channelActive(ChannelHandlerContext ctx)
        {
            requestReadIfAppropriate(ctx);
        }

        @Override
        protected void channelRead0(ChannelHandlerContext ctx, String line)
        {
            if (responseInFlight) {
                // If this happens, we violated our own contract; close loudly.
                ctx.close();
                return;
            }

            switch (state) {
                case WANT_COUNT -> {
                    int n;
                    try {
                        n = Integer.parseInt(line.trim());
                    }
                    catch (NumberFormatException e) {
                        ctx.close();
                        return;
                    }
                    if (n < 0) {
                        ctx.close();
                        return;
                    }
                    repeatCount = n;
                    state = State.WANT_TEXT;
                }
                case WANT_TEXT -> {
                    final String textLine = line;
                    state = State.WANT_COUNT;

                    responseInFlight = true;

                    ChunkedInput<ByteBuf> out = new RepeatingLineChunkedInput(
                            textLine, repeatCount, linesPerChunk, delayMs, delayJitterMs, ctx.executor());

                    ChannelFuture f = ctx.writeAndFlush(out);
                    f.addListener((ChannelFutureListener) future -> {
                        responseInFlight = false;
                        requestReadIfAppropriate(ctx);
                    });
                }
            }
        }

        @Override
        public void channelWritabilityChanged(ChannelHandlerContext ctx)
        {
            requestReadIfAppropriate(ctx);
            ctx.fireChannelWritabilityChanged();
        }

        private void requestReadIfAppropriate(ChannelHandlerContext ctx)
        {
            if (readPending) {
                return;
            }
            if (responseInFlight) {
                return;
            }
            if (!ctx.channel().isActive()) {
                return;
            }
            if (!ctx.channel().isWritable()) {
                return;
            }

            readPending = true;
            ctx.executor().execute(() -> {
                readPending = false;
                if (!responseInFlight && ctx.channel().isActive() && ctx.channel().isWritable()) {
                    ctx.read();
                }
            });
        }

        @Override
        public void exceptionCaught(ChannelHandlerContext ctx, Throwable cause)
        {
            cause.printStackTrace();
            ctx.close();
        }
    }

    /**
     * ChunkedInput that can optionally delay between chunks (slow producer simulation).
     * <p>
     * Emits:
     * (text + "\n") repeated N times, then "\n" terminator.
     * <p>
     * Delay behavior:
     * - After producing each chunk, schedules a delay before allowing the next chunk.
     * - Implemented via a Promise/timeout on the event loop.
     */
    public static final class RepeatingLineChunkedInput
            implements ChunkedInput<ByteBuf>
    {

        private final byte[] lineBytes;
        private final int repeatTotal;
        private final int linesPerChunk;

        private int repeatsRemaining;
        private boolean terminatorSent = false;

        private final int delayMs;
        private final int delayJitterMs;
        private final EventExecutor executor;

        private Future<?> gate = null;

        public RepeatingLineChunkedInput(
                String line,
                int repeatCount,
                int linesPerChunk,
                int delayMs,
                int delayJitterMs,
                EventExecutor executor)
        {

            Objects.requireNonNull(line, "line");
            Objects.requireNonNull(executor, "executor");
            if (repeatCount < 0) {
                throw new IllegalArgumentException("repeatCount < 0");
            }
            if (linesPerChunk <= 0) {
                throw new IllegalArgumentException("linesPerChunk <= 0");
            }
            if (delayMs < 0 || delayJitterMs < 0) {
                throw new IllegalArgumentException("delay < 0");
            }

            this.lineBytes = (line + "\n").getBytes(CharsetUtil.US_ASCII);
            this.repeatTotal = repeatCount;
            this.repeatsRemaining = repeatCount;
            this.linesPerChunk = linesPerChunk;

            this.delayMs = delayMs;
            this.delayJitterMs = delayJitterMs;
            this.executor = executor;
        }

        @Override
        public boolean isEndOfInput()
        {
            return repeatsRemaining == 0 && terminatorSent;
        }

        @Override
        public void close()
        {
            // nothing
        }

        @Override
        public ByteBuf readChunk(ChannelHandlerContext ctx)
        {
            return readChunk(ctx.alloc());
        }

        @Override
        public ByteBuf readChunk(ByteBufAllocator allocator)
        {
            if (isEndOfInput()) {
                return null;
            }

            // Delay gate: if not ready, return null so ChunkedWriteHandler will try again later.
            if (!gateReady()) {
                return null;
            }

            ByteBuf out;

            if (repeatsRemaining == 0) {
                terminatorSent = true;
                out = allocator.buffer(1);
                out.writeByte((byte) '\n');
            }
            else {
                int lines = Math.min(repeatsRemaining, linesPerChunk);
                int cap = lines * lineBytes.length;
                out = allocator.buffer(cap, cap);
                for (int i = 0; i < lines; i++) {
                    out.writeBytes(lineBytes);
                }
                repeatsRemaining -= lines;
            }

            armDelayGateIfNeeded();
            return out;
        }

        private boolean gateReady()
        {
            if (gate == null) {
                return true;
            }
            return gate.isDone();
        }

        private void armDelayGateIfNeeded()
        {
            int d = computeDelayMillis();
            if (d <= 0) {
                gate = null;
                return;
            }
            Promise<Void> p = executor.newPromise();
            executor.schedule(() -> p.setSuccess(null), d, TimeUnit.MILLISECONDS);
            gate = p;
        }

        private int computeDelayMillis()
        {
            if (delayMs <= 0 && delayJitterMs <= 0) {
                return 0;
            }
            int j = 0;
            if (delayJitterMs > 0) {
                // uniform in [-jitter, +jitter]
                j = ThreadLocalRandom.current().nextInt(-delayJitterMs, delayJitterMs + 1);
            }
            int d = delayMs + j;
            return Math.max(0, d);
        }

        @Override
        public long length()
        {
            return -1;
        }

        @Override
        public long progress()
        {
            return (long) (repeatTotal - repeatsRemaining);
        }
    }
}
