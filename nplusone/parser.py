import csv
import codecs
from typing import TypedDict
import collections
from .mecab import Mecab, Token
import os

SENTENCE_COLUMN_DEFAULT = 1
FREQUENCY_INCREMENT_DEFAULT = 100


class Sentence(TypedDict):
    new_tokens: dict[str, Token]
    row: list[str]
    line: str
    tokens: list[Token]


class Parser(object):

    def __init__(self):
        self.mecab = Mecab()

    def parse(
            self,
            in_file: str,
            out_file: str,
            sentence_column: int = SENTENCE_COLUMN_DEFAULT,
            frequency_increment: int = FREQUENCY_INCREMENT_DEFAULT,
            frequency_limit: int = None,
            known_file: str = None,
            update_known_file: bool = False,
            frequency_from_input: bool = False,
    ):

        known_vocab = {}
        if known_file:
            with codecs.open(known_file, 'r', 'utf-8') as f:
                i = 1
                for line in f:
                    known_vocab[line.rstrip('\n').rstrip('\r')] = i
                    i += 1

        sentences = []
        sentence_index = sentence_column - 1
        with codecs.open(in_file, 'r', 'utf-8') as in_file_handle:
            reader = csv.reader(in_file_handle, delimiter='\t')
            column_count = len(next(reader))
            if sentence_column > column_count or sentence_column < 1:
                raise Exception(f'Sentence column {sentence_column} out of range')
            in_file_handle.seek(0)

            for row in reader:
                if len(row) < sentence_index + 1:
                    continue
                sentence: Sentence = {}
                sentence['new_tokens'] = {}
                sentence['row'] = row
                sentence['line'] = row[sentence_index]
                sentence['tokens'] = self.mecab.reading(sentence['line'])

                for token in sentence['tokens']:
                    if 'dict_form' in token and token['dict_form'] not in known_vocab:
                        sentence['new_tokens'][token['dict_form']] = token

                if len(sentence['new_tokens']) > 0:
                    sentences.append(sentence)

        if len(sentences) == 0:
            raise Exception(
                'No new vocabulary found. Either all vocabulary is in the known file or you have used the wrong sentence column.')

        frequency_list = {}
        if frequency_from_input:
            input_frequency = []
            for sentence in sentences:
                for token in sentence['tokens']:
                    if 'dict_form' in token:
                        input_frequency.append(token['dict_form'])

            counts = collections.Counter(input_frequency)
            i = 1
            for vocab, _ in counts.most_common():
                frequency_list[vocab] = i
                i += 1
        else:
            frequency_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'support', 'frequency.txt')
            with codecs.open(frequency_file, 'r', 'utf-8') as f:
                i = 1
                for line in f:
                    frequency_list[line.rstrip('\n').rstrip('\r')] = i
                    i += 1

        frequency_list_length = len(frequency_list)
        if frequency_limit is None or frequency_limit > frequency_list_length:
            frequency_limit = frequency_list_length

        known_file_handle = None
        if known_file and update_known_file:
            known_file_handle = codecs.open(known_file, 'a', 'utf-8')

        out_file_handle = codecs.open(out_file, "w", "utf-8")
        frequency_index = min(frequency_increment, frequency_list_length)

        while True:
            added_words = {}
            remove_indexes = []

            for i in range(0, len(sentences)):
                sentence = sentences[i]
                if len(sentence['new_tokens']) == 0:
                    remove_indexes.append(i)
                elif len(sentence['new_tokens']) >= 1:
                    for dict_form, token in sentence['new_tokens'].items():
                        # Ignore if this word has been added
                        if dict_form in added_words:
                            remove_indexes.append(i)
                            continue
                        frequency = 0
                        if dict_form in frequency_list:
                            frequency = frequency_list[dict_form]

                        if frequency_index:
                            if frequency == 0 or frequency > frequency_index:
                                print(f'Frequency: {frequency} > {frequency_index}')
                                continue
                        elif frequency_limit:
                            if frequency == 0 or frequency > frequency_limit:
                                remove_indexes.append(i)
                                print(f'Frequency: {frequency} > {frequency_limit}')
                                continue

                        reading = ''
                        for sentence_token in sentence['tokens']:
                            cloze = 'dict_form' in sentence_token and \
                                    sentence_token['dict_form'] == dict_form

                            if cloze: reading += '<cloze>'
                            reading += sentence_token['surface']
                            if cloze: reading += '</cloze>'

                        # Wrap the cloze more closely
                        reading = reading.replace('<cloze> ', ' <cloze>')
                        reading = reading.strip()

                        out_cols = []
                        out_cols += sentence['row']
                        out_cols.append(token['surface'])
                        out_cols.append(token['dict_form'])
                        out_cols.append(token['dict_form_reading'])
                        out_cols.append(str(frequency))
                        out_cols.append(reading)
                        out_line = '\t'.join(out_cols)
                        out_line += '\n'
                        out_file_handle.write(out_line)

                        if known_file and update_known_file:
                            known_file_handle.write(token['dict_form'] + '\n')

                        added_words[dict_form] = i
                        if i not in remove_indexes:
                            remove_indexes.append(i)

            if len(added_words) > 0:
                # Remove added from list
                for i in remove_indexes[::-1]:
                    try:
                        del (sentences[i])
                    except IndexError:
                        pass

                # Remove added from existing sentences
                for i in range(len(sentences) - 1, -1, -1):
                    sentence = sentences[i]
                    for dict_form_reading, _ in added_words.items():
                        sentence['new_tokens'].pop(dict_form_reading, None)

            if len(sentences) == 0:
                break
            if frequency_index:
                if not frequency_limit and frequency_index == frequency_list_length:
                    # Allow more passes without any frequency limit
                    frequency_index = None
                    continue
                elif frequency_limit and frequency_index == frequency_limit and len(added_words) == 0:
                    break

                frequency_index += frequency_increment
                if frequency_limit and frequency_index > frequency_limit:
                    frequency_index = frequency_limit
                elif not frequency_limit and frequency_index > frequency_list_length:
                    frequency_index = frequency_list_length

            elif len(added_words) == 0:
                break

        if known_file_handle:
            known_file_handle.close()
        out_file_handle.close()


# Test
if __name__ == '__main__':
    parser = Parser()
    parser.parse(
        in_file='test.txt',
        out_file='output.txt',
        sentence_column=1,
        frequency_increment=10000000,
        frequency_limit=None,
        update_known_file=False,
        frequency_from_input=True,
    )
