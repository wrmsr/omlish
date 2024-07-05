import sys
import xmlrpc.client
import xmlrpc.server


def server():
    def is_even(n):
        return n % 2 == 0

    server = xmlrpc.server.SimpleXMLRPCServer(("localhost", 8000))
    print("Listening on port 8000...")
    server.register_function(is_even, "is_even")
    server.serve_forever()


def client():
    with xmlrpc.client.ServerProxy("http://localhost:8000/") as proxy:
        print("3 is even: %s" % str(proxy.is_even(3)))
        print("100 is even: %s" % str(proxy.is_even(100)))


if __name__ == '__main__':
    match sys.argv[1]:
        case 'server':
            server()
        case 'client':
            client()
