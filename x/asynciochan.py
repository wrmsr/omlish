import asyncio

class BytesChannelTransport(asyncio.Transport):
    def __init__(self, reader):
        self.reader = reader
        self.closed = asyncio.Future()

    def write(self, data):
        """Simulate writing data to the transport."""
        self.reader.feed_data(data)

    def close(self):
        """Close the transport."""
        self.reader.feed_eof()
        if not self.closed.done():
            self.closed.set_result(True)

    def is_closing(self):
        return self.closed.done()


async def create_bytes_channel():
    """
    Create a bytes channel where one side is a StreamReader for reading,
    and the other side is a StreamWriter for writing.

    :return: (reader, writer) tuple.
    """
    loop = asyncio.get_running_loop()

    # Create the reader
    reader = asyncio.StreamReader()

    # Create the writer
    protocol = asyncio.StreamReaderProtocol(reader)
    transport = BytesChannelTransport(reader)
    writer = asyncio.StreamWriter(transport, protocol, reader, loop)

    return reader, writer


# Example Usage
async def producer(writer):
    for i in range(5):
        data = f"Message {i}\n".encode()
        print(f"Producing: {data.decode().strip()}")
        writer.write(data)
        await writer.drain()
        await asyncio.sleep(1)
    writer.close()
    await writer.wait_closed()


async def consumer(reader):
    while not reader.at_eof():
        line = await reader.readline()
        if line:
            print(f"Consuming: {line.decode().strip()}")


async def main():
    reader, writer = await create_bytes_channel()

    # Run producer and consumer
    await asyncio.gather(producer(writer), consumer(reader))

asyncio.run(main())

