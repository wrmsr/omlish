import socket


HOST = '127.0.0.1'
PORT = 8080

if __name__ == '__main__':
    with socket.create_server((HOST, PORT), reuse_port=False) as server:
        while True:
            conn, addr = server.accept()
            with conn:
                _ = conn.recv(65536)  # ignore request
                conn.sendall(
                    b'HTTP/1.1 200 OK\r\n'
                    b'Content-Type: text/plain\r\n'
                    b'Transfer-Encoding: chunked\r\n'
                    b'Connection: close\r\n'
                    b'\r\n',
                )
                for part in [b'hello\n', b'world\n', b'done\n']:
                    conn.sendall(f'{len(part):X}\r\n'.encode('ascii'))
                    conn.sendall(part + b'\r\n')
                conn.sendall(b'0\r\n\r\n')
