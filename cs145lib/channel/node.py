__all__ = [
    'node_main',
]

from argparse import ArgumentParser
from sys import stderr
from typing import Callable

from .utils import Channel, SenderTestingChannel, ReceiverTestingChannel

def node_main(*, sender: Callable[[Channel, str], None], receiver: Callable[[Channel], str]):
    parser = ArgumentParser(description='Runs either a sender or a receiver using a Channel.')

    parser.add_argument('type',
        help="must be one of: sender, receiver")
    parser.add_argument('-v', '--verbose', action='store_true',
        help="verbose output")

    args = parser.parse_args()

    # TODO python 'match'
    data: str
    if args.type == 'sender':
        data = input().strip()
        print(f"The data to be sent is {data!r}", file=stderr)
        with SenderTestingChannel(verbose=args.verbose) as sender_channel:
            sender(sender_channel, data)
        print() # whitespace in the stdio stream is ignored
            
    elif args.type == 'receiver':
        with ReceiverTestingChannel(verbose=args.verbose) as receiver_channel:
            data = receiver(receiver_channel)
            print(f"The string returned by the receiver is {data!r}")
    else:
        raise RuntimeError(f"Unknown type: {args.type!r}")

