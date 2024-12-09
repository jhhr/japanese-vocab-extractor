# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Automatic reading generation with kakasi and mecab.
# See http://ichi2.net/anki/wiki/JapaneseSupport
#

from typing import TypedDict
import re
import pykakasi
import MeCab
from .utils import escapeText

mecabArgs = []


class Token(TypedDict):
    # surface form of the token (the original text)
    surface: str
    # dictionary form of the token (the base form) or None if not available
    dict_form: str
    # reading of the dictionary form or None if not available
    dict_form_reading: str


class Mecab(object):

    def __init__(self, mecabArgs=None):
        if mecabArgs is None:
            mecabArgs = []
        self.mecabArgs = mecabArgs
        self.kakasi = pykakasi.kakasi()
        self.tagger = MeCab.Tagger(' '.join(mecabArgs))

    def reading(self, expr: str) -> list[Token]:
        expr = escapeText(expr)
        node = self.tagger.parseToNode(expr)
        out = []

        while node:
            token: Token = {}
            features = node.feature.split(',')
            token['surface'] = node.surface
            if len(features) > 6:
                token['dict_form'] = features[6]
                token['dict_form_reading'] = self.kakasi.convert(features[7])[0]['hira']
            out.append(token)
            node = node.next

        return out

    def anki_reading(
            self,
            kanji: str,
            reading: str,
    ) -> str:
        """
        Return a string with the kanji and reading combined in a way that
        Anki will show the reading above the kanji.
        :param kanji: The kanji string, eg. '漢字'
        :param reading: The reading string, eg. 'かんじ'
        :return: The combined string, eg. '漢字[かんじ]'
        """
        # strip matching characters and beginning and end of reading and kanji
        # reading should always be at least as long as the kanji
        placeL = 0
        placeR = 0
        # if its not all kanji until the end, step from right to left to find reading
        # This is to handle when we have 'ー' but its a kanji only
        if not re.match(r'[\u4e00-\u9faf]+$', kanji):
            for i in range(1, len(kanji)):
                if kanji[-i] != reading[-i] and reading[-i] != r'ー':
                    break
                placeR = i
        for i in range(0, len(kanji) - 1):
            if kanji[i] != reading[i]:
                break
            placeL = i + 1
        if placeL == 0:
            if placeR == 0:
                return " %s[%s]" % (kanji, reading)
            else:
                return " %s[%s]%s" % (
                    kanji[:-placeR], reading[:-placeR], reading[-placeR:])
        else:
            if placeR == 0:
                return "%s %s[%s]" % (
                    reading[:placeL], kanji[placeL:], reading[placeL:])
            else:
                return "%s %s[%s]%s" % (
                    reading[:placeL], kanji[placeL:-placeR],
                    reading[placeL:-placeR], reading[-placeR:])