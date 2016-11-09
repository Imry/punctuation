#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

import parsimonious


grammar_rule = """
    expression = rule+
    rule = space "(" space rule_body space ")" space
    rule_body = simple_rule / add_punctuation / remove_punctuation
    simple_rule = word ((or / and) word)*
    and = "&"
    or = "|"
    word = space (not space)? (primitive_word / ("_" primitive_part "_")) space
    not = "!"
    primitive_word = ~"[йцукеёнгшщзхъфывапролджэячсмитьбю]+"
    primitive_part = ~"[QWERTYUIOPASDFGHJKLZXCVBNM]+"
    add = "+"
    remove = "-"
    add_punctuation = add punctuation
    remove_punctuation = remove punctuation
    punctuation = ~"."
    space = ~" *"
"""

class PEGParser(parsimonious.nodes.NodeVisitor):
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


    def __init__(self, grammar=grammar_rule):
        self.grammar = grammar
        pass

    def parse_rule(self, rule_str):
        try:
            ast = parsimonious.grammar.Grammar(self.grammar).parse(rule_str)
            self.idx = 1
            self.pattern = ''
            self.repl = ''
            self.visit(ast)
            # return Template(rule_str, self.pattern, self.repl)
            return self.Parser(self.pattern, self.repl)
        except Exception as e:
            print(e)
            return None

    def visit_simple_rule(self, n, c):
        # if self.repl != '':
            # self.repl += ' '
        # self.pattern += '\s*'

        text = self.SimpleRule(n).text
        self.pattern += r'(?P<space_%d>\s*\b)'%(self.idx)
        self.repl += r'\g<space_%d>'%(self.idx)
        self.idx += 1
        self.pattern += r'(?P<rule_%d>%s)'%(self.idx, text)
        self.repl += r'\g<rule_%d>'%(self.idx)
        self.idx += 1

# (\,)?(?P<space_1>\s*)(?P<rule_2>вернее\([^\(\)]*?\)|точнее\([^\(\)]*?\))(\,)?
# ,\g<space_1>\g<rule_2>,


    def visit_add_punctuation(self, n, c):
        ptn = self.PunctuationRule(n).text
        self.pattern += '(\%s)?'%(ptn)
        self.repl += ptn
        # self.pattern += '(?P<space_%d>\s*)'%(self.idx)
        # self.repl += '%s\g<space_%d>'%(ptn, self.idx)
        # self.idx += 1

    def visit_remove_punctuation(self, n, c):
        self.pattern += '(\%s)?'%(self.PunctuationRule(n).text)
        self.repl += ''

    def generic_visit(self, n, c):
        pass

    class Parser:
        def __init__(self, pattern, repl):
            self.pattern = pattern
            self.repl = repl

        def __call__(self, txt):
            ss = re.sub(self.pattern, self.repl, txt)

            # Велосипед
            ss = re.sub(r',,', r',', ss)
            ss = re.sub(r'^,', r'', ss)
            ss = re.sub(r',$', r'', ss)
            # ss = re.sub(r'  ', r' ', ss)
            #
            return ss 

        def __str__(self):
            return '-> \'%s\'\n<-\'%s\''%(self.pattern, self.repl)

    def prepare_sentence(self, sentence, morph):
        r = []
        for i, w in enumerate(sentence.split()):
            r.append('%s(%s)'%(w, morph[i]))
        return ' '.join(r)

    def norm_sentence(self, sentence):
        return re.sub(r'([^\(\)]*?)\([^\(\)]*\)', r'\1', sentence)


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

    rule = '(+,)(вернее|точнее)(+,)'
    print(rule)
    r = PEGParser()
    pp = r.parse_rule(rule)
    # print()
    print(r.pattern)
    print(r.repl)
    print()

    t = re.sub(r.pattern,
        r.repl,
        'а точнее всегда')

    t = pp('а() точнее() всегда()')
    print(t)
    t = pp('поточнее()')
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
