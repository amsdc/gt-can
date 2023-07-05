import functools
import socket
import threading
import logging


logger = logging.getLogger(__name__)


def default_callback(bytes_):
    logger.info("data is = " + bytes_.decode("utf-8"))



class Peer2Peer:
    def __init__(self):
        self.recv_cb = default_callback
        self.connections = []

    def listen(self, port=0):
        recvsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = socket.gethostbyname(socket.gethostname())
        recvsocket.bind((host, port))
        recvsocket.listen(1)
        port=recvsocket.getsockname()[1]
        logger.info(f"Listening for connections on {host}:{port}")

        while True:
            connection, address = recvsocket.accept()
            self.connections.append(connection)
            self.spawn_receive_thread(connection)
            logger.info(f"Accepted connection from {address}")

    def send(self, binary_data):
        for connection in self.connections:
            try:
                connection.sendall(binary_data)
            except socket.error as e:
                logger.error(f"Failed to send data. Error: {e}")

    def connect(self, peer_host, peer_port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((peer_host, peer_port))
            self.connections.append(s)
            self.spawn_receive_thread(s)
            logger.info(f"Connected to {peer_host}:{peer_port}")
        except socket.error as e:
            logger.error(f"Failed to connect to {peer_host}:{peer_port}. Error: {e}")
            raise e

    def observer(self, sok):
        while True:
            d = sok.recv(4096)
            if d:
                self.recv_cb(d)
            else:
                logger.info(f"Connection closed ({sok})")
                break

    def spawn_receive_thread(self, sock):
        thd = threading.Thread(target=functools.partial(self.observer, sock), 
                               daemon=True)
        thd.start()
        return thd

    def start_listener(self):
        listen_thread = threading.Thread(target=self.listen, daemon=True)
        listen_thread.start()

if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)

    c = Peer2Peer()

    while True:
        match input("> "):
            case "1":
                c.start_listener()
            case "2":
                h = input("Connect to HOST: ")
                p = int(input("On PORT: "))
                c.connect(h, p)
            case "3":
                msg = input("Enter Message: ").encode("utf-8")
                c.send(msg)

