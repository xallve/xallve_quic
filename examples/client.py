from quic.connection import QUICConnection


def main():
    conn = QUICConnection(('localhost', 4433))
    conn.connect()
    conn.send_stream_data(1, 0, b'hello from client')
    frame = conn.receive_frame()
    print(f"Received: {frame.data}")


if __name__ == '__main__':
    main()
