import socket
import threading
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.kdf.hkdf import HKDFExpand
from cryptography.hazmat.backends import default_backend
from .frame import Frame, StreamFrame, AckFrame, PingFrame, ConnectionCloseFrame
from .tls import TLSContext
from .congestion import CongestionControl


class QUICConnection:
    def __init__(self, server_address):
        self.server_address = server_address
        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(server_address)
        self.tls_context = TLSContext()
        self.congestion_control = CongestionControl()
        self.receive_thread = threading.Thread(target=self.receive_loop)
        self.receive_thread.daemon = True
        self.receive_thread.start()
        self.incoming_frames = []
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.peer_public_key = None
        self.shared_key = None

    def connect(self):
        self.initiate_tls_handshake()

    def initiate_tls_handshake(self):
        client_hello = self.create_client_hello()
        self.send_frame(client_hello)

        server_hello = self.receive_frame()

        if isinstance(server_hello, Frame) and server_hello.frame_type == 0x16:
            self.process_server_hello(server_hello)

    def create_client_hello(self):
        public_key_bytes = self.private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return Frame(0x01, public_key_bytes)

    def process_server_hello(self, server_hello):
        self.peer_public_key = serialization.load_pem_public_key(server_hello.data, backend=default_backend())
        encrypted_shared_key = self.private_key.decrypt(
            server_hello.data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        self.shared_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'handshake data',
            backend=default_backend()
        ).derive(encrypted_shared_key)

        self.send_frame(Frame(0x02, b'handshake complete'))

    def send_frame(self, frame):
        encrypted_data = self.tls_context.encrypt(frame.to_bytes())
        if self.congestion_control.can_send(len(encrypted_data)):
            self.send_socket.sendto(encrypted_data, self.server_address)

    def receive_loop(self):
        while True:
            data, _ = self.socket.recvfrom(4096)
            decrypted_data = self.tls_context.decrypt(data)
            frame = Frame.from_bytes(decrypted_data)

            if isinstance(frame, AckFrame):
                self.congestion_control.on_ack(len(decrypted_data))
            elif isinstance(frame, ConnectionCloseFrame):
                self.congestion_control.on_loss()

            self.incoming_frames.append(frame)

    def receive_frame(self):
        if self.incoming_frames:
            return self.incoming_frames.pop(0)
        return None

    def send_stream_data(self, stream_id, offset, data):
        frame = StreamFrame(stream_id, offset, data)
        self.send_frame(frame)

    def send_ping(self):
        frame = PingFrame()
        self.send_frame(frame)

    def send_ack(self, largest_acknowledged, ack_delay, ack_ranges):
        frame = AckFrame(largest_acknowledged, ack_delay, ack_ranges)
        self.send_frame(frame)

    def send_connection_close(self, error_code, reason_phrase):
        frame = ConnectionCloseFrame(error_code, reason_phrase)
        self.send_frame(frame)
