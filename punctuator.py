#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re

from PyQt5.QtWidgets import QApplication

from gui import Punctuator
# from parsimonious.grammar import Grammar
# from parsimonious.nodes import NodeVisitor
# import parsimonious

# from peg_grammar import RuleParser
from parse import TextParser

if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = Punctuator()
    form.move(50, 50)
    form.show()
    app.exec_()

    # if len(sys.argv) < 3:
    #     print('%s <rule file> <text file>'%(sys.argv[0]))
    #     exit(0)

    # rules = []
    # with open(sys.argv[1], 'rt', encoding = 'utf-8') as rules_f:
    #     for r in rules_f:
    #         rules.append(r.strip())

    # text = []
    # with open(sys.argv[2], 'rt', encoding = 'utf-8') as text_f:
    #     for t in text_f:
    #         text.append(t.strip())

    # rules = ['(+,)(вернее|точнее)(+,)',
    #         '(+,) ( вернее|точнее) (-, ) (говоря|сказать)(+,)',
    #         '(показания|узнаю)(-,)(точнее)(-,)',
    #         '(-,)(точнее)(-,)(показания|узнаю)',
    #         '(по)(-,)(точнее)(-,)']

    # text = ['он познакомился с ними вернее говоря они познакомились с ним']
    # text = ['он познакомился с ними вернее они познакомились с ним',
    #         'он познакомился с ними вернее сказать они познакомились с ним',
    #         'его показания точнее всех я им больше верю',
    #         'сейчас погоди узнаю точнее',
    #         'точнее узнаю и тебе позвоню',
    #         'узнай пожалуйста по точнее'
    #         ]

    # tp = textParser(PEGParser)
    # tp = TextParser()
    # for r in rules:
    #     print(r)
    #     r = tp.add(r)
    #     print(r)


    # print()

    # for t in text:
    #     tt, c = tp.parse(t)
    #     print('-> \'%s\''%(t))
    #     prev = t
    #     for cc in c:
    #         if cc != prev:
    #             print(cc)
    #         prev = cc
    #     print('<- \'%s\''%(tt))