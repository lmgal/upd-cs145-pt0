from sys import stderr

from cs145lib.task0 import Channel, node_main


def sender(channel: Channel, sentence: str) -> None:

    print("This is an example debugging print from the sender.", file=stderr)

    # example: send 69*5 bits
    for it in range(69):
        for bit in 1, 0, 1, 1, 0:
            channel.send(bit)


def receiver(channel: Channel) -> str:

    print("This is an example debugging print from the receiver.", file=stderr)

    # example: read 69 bits, and replace 0 with '.', and 1 with 'X'
    return ''.join(('X' if channel.get() else '.') for it in range(69))


if __name__ == '__main__':
    node_main(sender=sender, receiver=receiver)
