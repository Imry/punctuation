#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re

import pymorphy2

# from parsimonious.grammar import Grammar
# from parsimonious.nodes import NodeVisitor
# import parsimonious

from peg_grammar import RuleParser

class Rule:
    def __init__(self, rule, pattern, repl):
        self.text = rule
        self.pattern = pattern
        self.repl = repl

    def __call__(self, sentence):
        return re.sub(self.pattern, self.repl, sentence)

    def __str__(self):
        return '-> \'%s\'\n<-\'%s\''%(self.pattern, self.repl)

class textParser:
    def __init__(self, parser):
        self.rules = []
        self.parser = parser()
        self.morph = pymorphy2.MorphAnalyzer()

    def prepare_sentence(self, sentence):
        r = []
        for w in sentence.strip().split():
            m = self.morph.parse(w)[0].tag
            r.append('%s(%s)'%(w, m))
        return ' '.join(r)

    def norm_sentence(self, sentence):
        return re.sub(r'([^\(\)]*?)\([^\(\)]*\)', r'\1', sentence)

    def parse(self, sentence):
        # print(sentence)
        sentence = self.prepare_sentence(sentence)
        # print(sentence)
        for r in self.rules:
            ss = r(sentence)

            # Велосипед
            ss = re.sub(r',,', r',', ss)
            ss = re.sub(r'^,', r'', ss)
            ss = re.sub(r',$', r'', ss)
            # ss = re.sub(r'  ', r' ', ss)

            if ss != sentence:
                print('%s: %s'%(r.text, self.norm_sentence(ss)))
            else:
                # print('.')
                None
            sentence = ss
        # print(sentence)
        return self.norm_sentence(sentence)

    def add(self, rule_str):
        print(rule_str)
        r = self.parser.parse_rule(rule_str)
        r = Rule(rule_str, r[0], r[1])
        print(r)
        self.rules.append(r)

if __name__ == '__main__':
    rules = ['(+,)(вернее|точнее)(+,)',
            '(+,) ( вернее|точнее) (-, ) (говоря|сказать)(+,)',
            '(показания|узнаю)(-,)(точнее)(-,)',
            '(-,)(точнее)(-,)(показания|узнаю)',
            '(по)(-,)(точнее)(-,)']

    # text = ['он познакомился с ними вернее говоря они познакомились с ним']
    text = ['он познакомился с ними вернее они познакомились с ним',
            'он познакомился с ними вернее сказать они познакомились с ним',
            'его показания точнее всех я им больше верю',
            'сейчас погоди узнаю точнее',
            'точнее узнаю и тебе позвоню',
            'узнай пожалуйста по точнее'
            ]

    tp = textParser(RuleParser)
    for r in rules:
        tp.add(r)

    print()

    for t in text:
        print('-> \'%s\''%(t))
        print('<- \'%s\''%(tp.parse(t)))