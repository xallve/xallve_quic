import socket
from quic.quic_packet import QuicPacket
from quic.quic_connection import QuicConnection
import threading

from quic.quic_retransmission import RetransmissionHandler


def run_server(host='localhost', port=4433, encryption_key=None):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    print(f'Server listening on {host}:{port}')

    connections = {}

    def retransmission_thread():
        while True:
            for connection in connections.values():
                connection.retransmission_handler.check_retransmissions()

    threading.Thread(target=retransmission_thread, daemon=True).start()

    while True:
        try:
            data, address = server_socket.recvfrom(4096)
            if address not in connections:
                connections[address] = QuicConnection(server_socket, address, encryption_key)
            packet = QuicPacket.deserialize(data, connections[address].encryption)
            connections[address].handle_packet(packet)
            connections[address].retransmission_handler.acknowledge_packet(packet)

        except ConnectionResetError as e:
            print(f'ConnectionResetError: {e}')
        except Exception as e:
            print(f'Unexpected error: {e}')

if __name__ == "__main__":
    encryption_key = b'0123456789abcdef'  # 16-byte key for AES
    run_server(encryption_key=encryption_key)