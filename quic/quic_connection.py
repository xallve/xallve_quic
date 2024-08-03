from .quic_packet import QuicPacket, INITIAL_PACKET, HANDSHAKE_PACKET, DATA_PACKET
from .quic_state import QuicState, QuicConnectionState
from .quic_encryption import QuicEncryption
from .quic_retransmission import RetransmissionHandler


class QuicConnection:
    def __init__(self, socket, address, encryption_key=None):
        self.state = QuicConnectionState()
        self.streams = {}
        self.encryption = QuicEncryption(encryption_key) if encryption_key else None
        self.retransmission_handler = RetransmissionHandler(socket, address, self.encryption)
        self.socket = socket
        self.address = address

    def handle_packet(self, packet):
        if packet.packet_type == INITIAL_PACKET and self.state.get_state() == QuicState.INITIAL:
            print('Received INITIAL_PACKET from', self.address)
            self.state.set_state(QuicState.HANDSHAKE)
            response = QuicPacket(HANDSHAKE_PACKET, 0, b'Handshake', self.encryption)
            self.retransmission_handler.send_packet(response)

        elif packet.packet_type == DATA_PACKET and self.state.get_state() == QuicState.HANDSHAKE:
            print(f'Received DATA_PACKET on stream {packet.stream_id}:', packet.payload)
            if packet.stream_id not in self.streams:
                self.streams[packet.stream_id] = b''
            self.streams[packet.stream_id] += packet.payload
            response = QuicPacket(DATA_PACKET, packet.stream_id, b'ACK', self.encryption)
            self.retransmission_handler.send_packet(response)
            self.retransmission_handler.acknowledge_packet(packet)

            self.state.set_state(QuicState.ESTABLISHED)

    def send_data(self, stream_id, data):
        if self.state.get_state() == QuicState.ESTABLISHED:
            packet = QuicPacket(DATA_PACKET, stream_id, data, self.encryption)
            self.retransmission_handler.send_packet(packet)