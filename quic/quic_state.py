class QuicState:
    INITIAL = 'INITIAL'
    HANDSHAKE = 'HANDSHAKE'
    ESTABLISHED = 'ESTABLISHED'
    CLOSED = 'CLOSED'

class QuicConnectionState:
    def __init__(self):
        self.state = QuicState.INITIAL

    def set_state(self, new_state):
        print(f'Transitioning from {self.state} to {new_state}')
        self.state = new_state

    def get_state(self):
        return self.state