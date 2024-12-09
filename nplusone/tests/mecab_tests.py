# -*- coding: UTF-8 -*-

import unittest
from ..mecab import Mecab

class TestMecab(unittest.TestCase):
 
    def setUp(self):
        self.sut = Mecab()

    def test_returns_tokenized_sentence(self):
        result = self.sut.reading('焦げてる')
        reading = self.sut.anki_reading('焦げてる', result)
        self.assertEqual(result[0]['dict_form_reading'], '焦[こ]げる')

    def test_na_adjectives_dont_have_da_suffix(self):
        result = self.sut.reading('安心する')
        self.assertEqual(result[0]['dict_form'], '安心')
        self.assertEqual(result[0]['dict_form_reading'], '安心[あんしん]')

    def test_verbs_in_potential_form_resolve_to_dictiory_form(self):
        result = self.sut.reading('会える')
        self.assertEqual(result[0]['dict_form'], '会う')
        self.assertEqual(result[0]['dict_form_reading'], '会[あ]う')

    def test_katakana_with_dash_is_converted_to_hiragana(self):
        result = self.sut.reading('大きい')
        self.assertEqual(result[0]['surface'], ' 大[おお]きい')

        result = self.sut.reading('行こう')
        self.assertEqual(result[0]['surface'], ' 行[い]こう')

        result = self.sut.reading('苦労')
        self.assertEqual(result[0]['surface'], ' 苦労[くろう]')

        result = self.sut.reading('間違い')
        self.assertEqual(result[0]['surface'], ' 間違[まちが]い')

        #リョウコ why is this in output

if __name__ == '__main__':
    unittest.main()