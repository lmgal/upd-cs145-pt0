from argparse import ArgumentParser
from pathlib import Path
from random import Random, getrandbits
from string import ascii_lowercase
from sys import stderr


def make_sentence(rand, wlow, whigh, words):
    wc = rand.randint(wlow, whigh)

    swords = [rand.choice(words) for it in range(wc)]

    swords[0] = swords[0].title()

    return swords


def format_sentence(words):
    return ' '.join(words) + '.'


def main():
    parser = ArgumentParser(description='Generates a random "sentence" from the given corpus of words.')

    parser.add_argument('-c', '--corpus-file', type=Path, default='corpus.txt',
        help='corpus of words to take from (default: %(default)s)')

    parser.add_argument('-s', '--seed', type=int, default=None,
        help='the seed for the random number generator (default: based on system time)')

    parser.add_argument('-w', '--word-count', type=int, nargs=2, metavar=('WLOW', 'WHIGH'), default=(3, 5),
        help='the interval for the word count (default: %(default)s)')

    args = parser.parse_args()

    if args.seed is None:
        seed = getrandbits(64)
    else:
        seed = int(args.seed)

    corpus_file = Path(args.corpus_file)

    with corpus_file.open() as f:
        words = f.read().split()

    print(format_sentence(make_sentence(Random(seed), *args.word_count, words)))



if __name__ == '__main__':
    main()
