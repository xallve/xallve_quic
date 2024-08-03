from quic.connection import QUICConnection


def main():
    conn = QUICConnection(('localhost', 4433))
    conn.connect()
    while True:
        try:
            frame = conn.receive_frame()
            print(f"Received: {frame.data}")
            conn.send_stream_data(1, 0, b'hello from server')
        except Exception as e:
            pass


if __name__ == '__main__':
    main()
