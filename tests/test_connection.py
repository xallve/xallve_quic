import unittest
from quic.connection import QUICConnection
from quic.frame import StreamFrame, PingFrame, AckFrame, ConnectionCloseFrame


class TestQUICConnection(unittest.TestCase):
    def test_connection(self):
        conn = QUICConnection(('localhost', 4433))
        conn.connect()
        self.assertTrue(conn)

    def test_send_receive_stream(self):
        conn = QUICConnection(('localhost', 4433))
        conn.connect()
        conn.send_stream_data(1, 0, b'hello stream')
        frame = conn.receive_frame()
        self.assertIsInstance(frame, StreamFrame)
        self.assertEqual(frame.data, b'hello stream')

    def test_send_receive_ping(self):
        conn = QUICConnection(('localhost', 4433))
        conn.connect()
        conn.send_ping()
        frame = conn.receive_frame()
        self.assertIsInstance(frame, PingFrame)

    def test_send_receive_ack(self):
        conn = QUICConnection(('localhost', 4433))
        conn.connect()
        conn.send_ack(1, 0, [(0, 1)])
        frame = conn.receive_frame()
        self.assertIsInstance(frame, AckFrame)
        self.assertEqual(frame.largest_acknowledged, 1)

    def test_send_receive_connection_close(self):
        conn = QUICConnection(('localhost', 4433))
        conn.connect()
        conn.send_connection_close(1, 'error')
        frame = conn.receive_frame()
        self.assertIsInstance(frame, ConnectionCloseFrame)
        self.assertEqual(frame.error_code, 1)
        self.assertEqual(frame.data.decode('utf-8'), 'error')

    def test_congestion_control(self):
        conn = QUICConnection(('localhost', 4433))
        conn.connect()
        data = b'a' * 1024
        for _ in range(20):
            conn.send_stream_data(1, 0, data)
        self.assertTrue(conn.congestion_control.cwnd > 10 * 1024)

    def test_tls_handshake(self):
        conn = QUICConnection(('localhost', 4433))
        conn.connect()
        self.assertIsNotNone(conn.shared_key)


if __name__ == '__main__':
    unittest.main()
