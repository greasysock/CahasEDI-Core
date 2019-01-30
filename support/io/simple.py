# A simple directory watch/send class. Could be more robust


class Connection:

    def __init__(self, watch_dir, send_dir):
        self._watch_dir = watch_dir
        self._send_dir = send_dir

    class _Send:
        pass

    class _Receive:
        pass