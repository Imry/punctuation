#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

import pymorphy2

import peg

class TextParser:
    class Template:
        def __init__(self, text, handler):
            self.text = text
            self.handler = handler

        def __call__(self, sentence):
            if self.handler:
                return self.handler(sentence)
            else:
                return sentence

        def __str__(self):
            return self.handler.str()

    class Rule:
        def __init__(self, name, tmpl = None, text = None):
            self.name = name
            if tmpl:
                self.tmpl = tmpl
            else:
                self.tmpl = []
            if text:
                self.text = text
            else:
                self.text = []

        def __call__(self, sentence):
            r = []
            for t in self.tmpl:
                s = t(sentence)
                if s != sentence:
                    r.append((self.name, t.text, s))
                sentence = s
            return sentence, r

        def from_json(self, json):
            self.name = json['name']
            self.text = json['text']

        def to_json(self):
            data = {}
            data['name'] = self.name
            data['text'] = self.text
            return data

    def __init__(self, parser = peg.PEGParser):
        self.rules = []
        self.parser = parser()
        self.morph = pymorphy2.MorphAnalyzer()

    def get_morph_data(self, sentence):
        return [self.morph.parse(w)[0].tag for w in sentence.strip().split()]

    def parse(self, sentence, rules = None):
        if not rules:
            rules = self.rules
        sentence = self.parser.prepare_sentence(sentence, self.get_morph_data(sentence))
        res = []
        for r in rules:
            ss, chain = r(sentence)
            if chain != []:
                for c in chain:
                    res.append((c[0], c[1], self.parser.norm_sentence(c[2])))
            sentence = ss
        return self.parser.norm_sentence(sentence), res

    def parse_rule(self, rule):
        return self.parser.parse_rule(rule)
