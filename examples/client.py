import socket
from quic.quic_packet import QuicPacket, INITIAL_PACKET, DATA_PACKET, HANDSHAKE_PACKET
from quic.quic_encryption import QuicEncryption
import threading
import time

from quic.quic_retransmission import RetransmissionHandler


def run_client(host='localhost', port=4433, encryption_key=None):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.bind((('127.0.0.1', 65312)))
    encryption = QuicEncryption(encryption_key) if encryption_key else None

    def retransmission_thread(retransmission_handler):
        while True:
            retransmission_handler.check_retransmissions()
            if retransmission_handler.stop_event.is_set():
                break

    initial_packet = QuicPacket(INITIAL_PACKET, 0, b'', encryption)
    retransmission_handler = RetransmissionHandler(client_socket, (host, port), encryption)
    a = threading.Thread(target=retransmission_thread, args=(retransmission_handler,), daemon=True)
    a.start()
    retransmission_handler.send_packet(initial_packet)

    while True:
        data, _ = client_socket.recvfrom(4096)
        packet = QuicPacket.deserialize(data, encryption)

        if packet.packet_type == HANDSHAKE_PACKET:
            print('Received HANDSHAKE_PACKET')
            stream_id = 1
            data_packet = QuicPacket(DATA_PACKET, stream_id, b'Hello, QUIC on stream 1!', encryption)
            retransmission_handler.send_packet(data_packet)

        elif packet.packet_type == DATA_PACKET:
            print(f'Received ACK on stream {packet.stream_id}:', packet.payload)
            retransmission_handler.acknowledge_packet(packet)

            if not a.is_alive():
                print('All packets acknowledged. Closing connection.')
                break


if __name__ == "__main__":
    encryption_key = b'0123456789abcdef'  # 16-byte key for AES
    run_client(encryption_key=encryption_key)
