import time
import threading


class RetransmissionHandler:
    def __init__(self, socket, address, encryption):
        self.socket = socket
        self.address = address
        self.encryption = encryption
        self.sent_packets = {}
        self.acknowledged_packets = set()
        self.lock = threading.Lock()
        self.retransmission_interval = 1
        self.stop_event = threading.Event()

    def send_packet(self, packet):
        serialized_packet = packet.serialize()
        self.socket.sendto(serialized_packet, self.address)
        with self.lock:
            self.sent_packets[packet.stream_id] = (packet, time.time())

    def acknowledge_packet(self, packet):
        with self.lock:
            if packet.stream_id in self.sent_packets:
                del self.sent_packets[packet.stream_id]
            self.acknowledged_packets.add(packet.stream_id)
            if not self.sent_packets:
                self.stop_event.set()

    def check_retransmissions(self):
        while not self.stop_event.is_set():
            time.sleep(self.retransmission_interval)
            with self.lock:
                current_time = time.time()
                for stream_id, (packet, timestamp) in list(self.sent_packets.items()):
                    if current_time - timestamp > self.retransmission_interval:
                        print(f'Retransmitting packet {stream_id}')
                        self.socket.sendto(packet.serialize(), self.address)
                        self.sent_packets[stream_id] = (packet, current_time)
