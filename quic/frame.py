import struct


class Frame:
    FRAME_TYPE = {
        0x00: 'STREAM',
        0x02: 'ACK',
        0x07: 'PING',
        0x1c: 'CONNECTION_CLOSE'
    }

    def __init__(self, frame_type, data):
        self.frame_type = frame_type
        self.data = data

    def to_bytes(self):
        """
        Convert frame to bytes
        """
        frame_type_byte = struct.pack('B', self.frame_type)
        return frame_type_byte + self.data

    @classmethod
    def from_bytes(cls, data):
        """
        Frame creation from bytes
        """
        frame_type = data[0]
        payload = data[1:]
        return cls(frame_type, payload)


class StreamFrame(Frame):
    def __init__(self, stream_id, offset, data):
        super().__init__(0x00, data)
        self.stream_id = stream_id
        self.offset = offset

    def to_bytes(self):
        frame_type_byte = struct.pack('B', self.frame_type)
        stream_id_bytes = struct.pack('!I', self.stream_id)
        offset_bytes = struct.pack('!Q', self.offset)
        return frame_type_byte + stream_id_bytes + offset_bytes + self.data

    @classmethod
    def from_bytes(cls, data):
        frame_type = data[0]  # 0x00 in any case
        stream_id = struct.unpack('!I', data[1:5])[0]
        offset = struct.unpack('!Q', data[5:13])[0]
        payload = data[13:]
        return cls(stream_id, offset, payload)


class AckFrame(Frame):
    def __init__(self, largest_acknowledged, ack_delay, ack_ranges):
        super().__init__(0x02, b'')
        self.largest_acknowledged = largest_acknowledged
        self.ack_delay = ack_delay
        self.ack_ranges = ack_ranges

    def to_bytes(self):
        frame_type_byte = struct.pack('B', self.frame_type)
        largest_acknowledged_bytes = struct.pack('!Q', self.largest_acknowledged)
        ack_delay_bytes = struct.pack('!Q', self.ack_delay)
        ack_ranges_bytes = b''.join([struct.pack('!Q', start) + struct.pack('!Q', end) for start, end in self.ack_ranges])
        return frame_type_byte + largest_acknowledged_bytes + ack_delay_bytes + ack_ranges_bytes

    @classmethod
    def from_bytes(cls, data):
        frame_type = data[0]
        largest_acknowledged = struct.unpack('!Q', data[1:9])[0]
        ack_delay = struct.unpack('!Q', data[9:17])[0]
        ack_ranges = []
        offset = 17
        while offset < len(data):
            start = struct.unpack('!Q', data[offset:offset+8])[0]
            end = struct.unpack('!Q', data[offset+8:offset+16])[0]
            ack_ranges.append((start, end))
            offset += 16
        return cls(largest_acknowledged, ack_delay, ack_ranges)


class PingFrame(Frame):
    def __init__(self):
        super().__init__(0x07, b'')


class ConnectionCloseFrame(Frame):
    def __init__(self, error_code, reason_phrase):
        super().__init__(0x1c, reason_phrase.encode('utf-8'))
        self.error_code = error_code

    def to_bytes(self):
        frame_type_byte = struct.pack('B', self.frame_type)
        error_code_bytes = struct.pack('!I', self.error_code)
        reason_phrase_length_bytes = struct.pack('!H', len(self.data))
        return frame_type_byte + error_code_bytes + reason_phrase_length_bytes + self.data

    @classmethod
    def from_bytes(cls, data):
        frame_type = data[0]  # 0x07
        error_code = struct.unpack('!I', data[1:5])[0]
        reason_phrase_length = struct.unpack('!H', data[5:7])[0]
        reason_phrase = data[7:7+reason_phrase_length].decode('utf-8')
        return cls(error_code, reason_phrase)
