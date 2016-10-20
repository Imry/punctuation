#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import sys
import re

# import pymorphy2

# from parsimonious.grammar import Grammar
# from parsimonious.nodes import NodeVisitor
import parsimonious

grammar_rule = """
    expression = rule+
    rule = space "(" space rule_body space ")" space
    rule_body = simple_rule / add_punctuation / remove_punctuation
    simple_rule = word ((or / and) word)*
    and = "&"
    word = space (not space)? (primitive_word / ("_" primitive_part "_")) space
    primitive_word = ~"[йцукенгшщзхъфывапролджэячсмитьбю]+"
    primitive_part = ~"[QWERTYUIOPASDFGHJKLZXCVBNM]+"
    or = "|"
    add = "+"
    not = "!"
    remove = "-"
    add_punctuation = add punctuation
    remove_punctuation = remove punctuation
    punctuation = ~"."
    space = ~" *"
"""

class SimpleRule(parsimonious.nodes.NodeVisitor):
    def __init__(self, ast):
        self.text = ''
        self.visit(ast)

    def visit_primitive_word(self, n, c):
        self.text += '%s\([^\(\)]*?\)'%(n.text)

    def visit_primitive_part(self, n, c):
        self.text += '[^\(\)]*?\([^\(\)]*?%s[^\(\)]*?\)'%(n.text)

    def visit_or(self, n, c):
        self.text += n.text

    def visit_and(self, n, c):
        self.text += n.text

    def visit_not(self, n, c):
        self.text += n.text

    def generic_visit(self, n, c):
        pass

class PunctuationRule(parsimonious.nodes.NodeVisitor):
    def __init__(self, ast):
        self.text = None
        self.visit(ast)

    def visit_punctuation(self, n, c):
        self.text = n.text

    def generic_visit(self, n, c):
        pass

class RuleParser(parsimonious.nodes.NodeVisitor):
    def __init__(self, grammar=grammar_rule):
        self.grammar = grammar
        pass

    def parse_rule(self, rule_str):
        ast = parsimonious.grammar.Grammar(self.grammar).parse(rule_str)
        self.idx = 1
        self.pattern = ''
        self.repl = ''
        self.visit(ast)
        return (self.pattern, self.repl)

    def visit_simple_rule(self, n, c):
        # if self.repl != '':
            # self.repl += ' '
        # self.pattern += '\s*'

        text = SimpleRule(n).text
        self.pattern += '(?P<space_%d>\s*)'%(self.idx)
        self.repl += '\g<space_%d>'%(self.idx)
        self.idx += 1
        self.pattern += '(?P<rule_%d>%s)'%(self.idx, text)
        self.repl += '\g<rule_%d>'%(self.idx)
        self.idx += 1

    def visit_add_punctuation(self, n, c):
        ptn = PunctuationRule(n).text
        self.pattern += '(\%s)?'%(ptn)
        self.repl += ptn
        # self.pattern += '(?P<space_%d>\s*)'%(self.idx)
        # self.repl += '%s\g<space_%d>'%(ptn, self.idx)
        # self.idx += 1

    def visit_remove_punctuation(self, n, c):
        self.pattern += '(\%s)?'%(PunctuationRule(n).text)
        self.repl += ''

    def generic_visit(self, n, c):
        pass

if __name__ == '__main__':

    rule = '(+,)( вернее|!точнее) (-, )(говоря|сказать)(+,)'
    rule = '(+,)( _COMP_ |!точнее) (-, )(говоря|сказать)(+,)'
    text = 'он познакомился с ними вернее сказать они познакомились с ним'
    text_h = 'он(NPRO,masc,3per,Anph sing,nomn) познакомился(VERB,perf,intr masc,sing,past,indc) с(PREP) ними(NPRO,3per,Anph plur,ablt,Af-p) вернее(COMP,Qual) сказать(тут херня) они(NPRO,3per,Anph plur,nomn) познакомились(VERB,perf,intr plur,past,indc) с(PREP) ним(NPRO,masc,3per,Anph sing,ablt,Af-p)'

    rules = ['(+,)(вернее|точнее)(+,)',
            '(+,)( вернее|!точнее) (-, )(говоря|сказать)(+,)',
            '(показания|узнаю)(-,)(точнее)(-,)',
            '(-,)(точнее)(-,)(показания|узнаю)',
            '(по)(-,)(точнее)(-,)']

    print(rule)
    r = RuleParser()
    r.parse_rule(rule)
    # print()
    print(r.pattern)
    print(r.repl)
    print()

    t = re.sub(r.pattern,
        r.repl,
        text_h)

    print(t)

    # grm = parsimonious.grammar.Grammar(grammar_parse_rule)
    # print (grm.parse(rule))

    # for rule in rules:
    #     print(rule)
    #     r = RuleParser(grammar_parse_rule, rule)
    #     # print()
    #     print(r.pattern)
    #     print(r.repl)
    #     print()
