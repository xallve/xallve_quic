import struct
import socket

INITIAL_PACKET = 0
HANDSHAKE_PACKET = 1
DATA_PACKET = 2


class QuicPacket:
    def __init__(self, packet_type, stream_id, payload, encryption=None):
        self.packet_type = packet_type
        self.stream_id = stream_id
        self.payload = payload
        self.encryption = encryption

    def serialize(self):
        payload = self.payload
        if self.encryption:
            payload = self.encryption.encrypt(payload)
        return struct.pack('B', self.packet_type) + struct.pack('I', self.stream_id) + payload

    @classmethod
    def deserialize(cls, data, encryption=None):
        packet_type = struct.unpack('B', data[:1])[0]
        stream_id = struct.unpack('I', data[1:5])[0]
        payload = data[5:]
        if encryption:
            payload = encryption.decrypt(payload)
        return cls(packet_type, stream_id, payload, encryption)