from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
from functools import partial, wraps
from itertools import chain, repeat
from random import Random, getrandbits
from subprocess import Popen, PIPE
from sys import stdout, stderr
from threading import Thread


def to_stderr(stream, prefix):
    while line := stream.readline():
        stderr.write(prefix + line)
        stderr.flush()


def sender_stream_to_bits(seq):
    for r in seq:
        if r.strip():
            try:
                bit = int(r)
            except Exception as ex:
                raise RuntimeError(f"Cannot read bit {r!r}") from ex


            if bit not in {0, 1}:
                raise RuntimeError(f"Invalid bit {bit}")
            
            yield bit


def noisify(seq, *, flip_prob: float, rand: Random):
    for bit in seq:
        if bit not in {0, 1}:
            raise RuntimeError(f"Invalid bit {bit!r}")

        # randomly flip
        if rand.random() < flip_prob:
            bit ^= 1

        yield bit


def count_calls(func):
    callc = 0
    @wraps(func)
    def func_with_calls(*args, **kwargs):
        nonlocal callc
        callc += 1
        return func(*args, **kwargs)

    func_with_calls.call_count = lambda: callc
    return func_with_calls


def count_yields(seq):
    yieldc = 0
    def _seq():
        nonlocal yieldc
        for v in seq:
            yieldc += 1
            yield v

    return _seq(), lambda: yieldc


def noisy_channel(input, output, *, zlow, zhigh, seed, flip_prob, verbose=False):

    pprint = partial(print, '[Channel]')

    rand = Random(seed)

    zero_pad = rand.randint(zlow, zhigh)

    if verbose:
        pprint(f'padding with {zero_pad} zeroes', file=stderr)

    bits, bits_count = count_yields(sender_stream_to_bits(iter(lambda: input.read(1), '')))
    trail, trail_yield_count = count_yields(repeat(0))
    noisy_stream = noisify(
        chain(repeat(0, zero_pad), bits, trail),
        flip_prob=flip_prob,
        rand=rand,
    )

    for v in noisy_stream:
        assert v in {0, 1}
        try:
            output.write(str(v))
            output.flush()
        except BrokenPipeError:
            if verbose:
                pprint("Received BrokenPipeError. The stream presumably ended", file=stderr)
            break

    while not trail_yield_count(): next(noisy_stream)

    return bits_count()



def make_main(*, default_flip_prob=0.0, has_flip=False):
    def main():

        parser = ArgumentParser(description='Simulates the communication between a sender and a receiver through an imperfect channel.')

        parser.add_argument('command', nargs='+',
            help='the command for the sender/receiver')
        parser.add_argument('-z', '--zero-pad', type=int, nargs=2, metavar=('ZLOW', 'ZHIGH'), default=(100, 1000),
            help='the interval for the number of zeroes to prepend (default: %(default)s)')
        if has_flip:
            parser.add_argument('-f', '--flip-prob', type=float, default=default_flip_prob,
                help='the probability of flipping a bit (default: %(default)s)')
        parser.add_argument('-s', '--seed', type=int, default=None,
            help='the seed for the random number generator. (default: based on system time)')
        parser.add_argument('-v', '--verbose', action='store_true',
            help='the interval for the word count')

        args = parser.parse_args()

        if args.verbose:
            print("Received arguments:", args, file=stderr)

        zlow, zhigh = args.zero_pad
        if not (0 <= zlow <= zhigh):
            raise RuntimeError(f"Invalid zero pad parameter: {zlow, zhigh}")

        if args.seed is None:
            seed = getrandbits(64)
        else:
            seed = int(args.seed)

        if args.verbose:
            print(f'Using random seed {seed}', file=stderr)



        if has_flip:
            flip_prob = args.flip_prob
        else:
            flip_prob = default_flip_prob


        command = [arg.removeprefix('___') for arg in args.command]
        if args.verbose:
            command.append('--verbose')
        sender_command   = *command, 'sender'
        receiver_command = *command, 'receiver'
        if args.verbose:
            print(  f"Sender command is:", *sender_command, file=stderr)
            print(f"Receiver command is:", *receiver_command, file=stderr)

        sender_process   = Popen(sender_command,   stdout=PIPE, stderr=PIPE, encoding='utf-8')
        receiver_process = Popen(receiver_command, stdin=PIPE, stdout=PIPE, stderr=PIPE, encoding='utf-8', bufsize=0)

        sender_piper   = Thread(target=to_stderr, args=(sender_process.stderr,   '  [Sender stderr] '))
        receiver_piper = Thread(target=to_stderr, args=(receiver_process.stderr, '[Receiver stderr] '))

        # executor with just one...
        with ThreadPoolExecutor() as executor:
            future = executor.submit(noisy_channel, sender_process.stdout, receiver_process.stdin,
                    zlow=zlow,
                    zhigh=zhigh,
                    seed=seed,
                    flip_prob=flip_prob,
                    verbose=args.verbose,
                )
            read_count = future.result()

        threads = sender_piper, receiver_piper
        for thread in threads: thread.start()
        for thread in threads: thread.join()

        if args.verbose:
            print('Finished!', file=stderr)

        print(f'Exactly {read_count} bits were written by the sender.')
        stdout.write(receiver_process.stdout.read())

    return main
