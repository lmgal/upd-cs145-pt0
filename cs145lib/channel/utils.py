__all__ = [
    'Channel',
    'SenderTestingChannel',
    'ReceiverTestingChannel',
]

from sys import stdin, stdout, stderr


class Channel:
    def send(self, bit: int) -> None:
        raise NotImplementedError

    def get(self) -> int:
        raise NotImplementedError


class SenderTestingChannel(Channel):
    def __init__(self, *, verbose=False):
        self._sent = []
        self._verbose = verbose
        super().__init__()

    def send(self, bit: int) -> None:
        if bit not in {0, 1}:
            raise RuntimeError(f"invalid bit {bit}")
        self._sent.append(bit)
        stdout.write(str(bit))

    def __enter__(self):
        if self._verbose:
            print(f"[Sender] Starting", file=stderr)
        return self

    def __exit__(self, *args):
        if self._verbose:
            print(f"[Sender] {len(self._sent)} bits sent:", ''.join(map(str, self._sent)), file=stderr)


class ReceiverTestingChannel(Channel):
    def __init__(self, *, verbose=False):
        self._read = []
        self._verbose = verbose
        super().__init__()

    def get(self) -> int:
        def get_char():
            while True:
                try:
                    r = stdin.read(1)
                except EOFError as ex:
                    raise RuntimeError(f"cannot read bit because the stream has ended") from ex
                else:
                    if not r:
                        raise RuntimeError(f"cannot read bit because the stream has ended")

                    if not r or r.strip():
                        return r

        r = get_char()

        try:
            bit = int(r)
        except Exception as ex:
            raise RuntimeError(f"cannot read bit {r!r}") from ex

        if bit not in {0, 1}:
            raise RuntimeError(f"invalid bit {bit}")

        self._read.append(bit)
        return bit

    def __enter__(self):
        if self._verbose:
            print(f"[Receiver] Starting", file=stderr)
        return self

    def __exit__(self, *args):
        if self._verbose:
            print(f"[Receiver] {len(self._read)} bits read:", ''.join(map(str, self._read)), file=stderr)
