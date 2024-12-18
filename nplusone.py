import argparse
import os
from nplusone.parser import \
    Parser, \
    SENTENCE_COLUMN_DEFAULT, \
    FREQUENCY_INCREMENT_DEFAULT

VERSION='1.1.0'

def parse(args):

    support_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'support')
    if not os.path.isdir(support_path):
        raise Exception("Missing support folder, please download from NPlusOne releases page.")

    parser = Parser()
    parser.parse(args.input, args.output, args.column, args.increment, args.limit, args.known, args.update_known, args.frequency_from_input)

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.set_defaults(func=parse)

    arg_parser.add_argument('-v', '--version', action='version', version='NPlusOne Japanese Sentence Miner v' + VERSION)
    arg_parser.add_argument('-c', '--column', type=int, default=SENTENCE_COLUMN_DEFAULT, help='Column of sentence in input TSV. Default={}.'.format(SENTENCE_COLUMN_DEFAULT))
    arg_parser.add_argument('-i', '--increment', type=int, default=FREQUENCY_INCREMENT_DEFAULT, help='Increments to scan frequency of vocabulary. Default={}, Set to 0 to disable.'.format(FREQUENCY_INCREMENT_DEFAULT))
    arg_parser.add_argument('-l', '--limit', type=int, default=None, help='Maximum frequency index of vocabulary to allow. Default=Length of frequency list, Set to 0 to disable.')
    arg_parser.add_argument('-k', '--known', default=None, help='Text file of known vocabulary, one word per line. Default=None')
    arg_parser.add_argument('-r', '--update-known', action='store_true', help='Add new words to known file automatically.')
    arg_parser.add_argument('-f', '--frequency-from-input', action='store_true', help='Calculate the frequency from the input TSV.')
    arg_parser.add_argument('input', help='Path of TSV file to read')
    arg_parser.add_argument('output', help='Path of TSV file to write')

    args = arg_parser.parse_args()
    args.func(args)  # call the default function