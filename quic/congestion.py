class CongestionControl:
    def __init__(self):
        self.cwnd = 10 * 1024
        self.ssthresh = 64 * 1024
        self.ack_count = 0

    def on_ack(self, acked_bytes):
        if self.cwnd < self.ssthresh:
            self.cwnd += acked_bytes
        else:
            self.ack_count += 1
            if self.ack_count * acked_bytes >= self.cwnd:
                self.cwnd += 1024
                self.ack_count = 0

    def on_loss(self):
        self.ssthresh = self.cwnd // 2
        self.cwnd = 1024

    def can_send(self, bytes_to_send):
        return bytes_to_send <= self.cwnd
