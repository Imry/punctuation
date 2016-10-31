import pyparsing as pypa


class MyLiteral(pypa.Token):
    def __init__(self, matchString, tags):
        super(MyLiteral, self).__init__()
        self.match = matchString.upper()
        self.name = '"%s"' % self.match
        self.errmsg = "Expected " + self.name
        self.mayReturnEmpty = False
        self.mayIndexError = False
        self.tags = tags

    def parseImpl(self, instring, loc, doActions=True):
        if instring[loc]['word'].upper() == self.match:
            ret_value = instring[loc].copy()
            ret_value['parsing_value'] = self.value
            if isinstance(self.value, int):
                if self.suffix:
                    ret_value['parsing_suffix'] = self.suffix
                    ret_value['word'] = '%i%s' % (self.value, self.suffix)
                else:
                    ret_value['word'] = '%i' % (self.value)
            else:
                if self.suffix:
                    ret_value['parsing_suffix'] = self.suffix
                    ret_value['word'] = '%s%s' % (self.value, self.suffix)
                else:
                    ret_value['word'] = '%s' % (self.value)
            return loc + 1, ret_value
        raise pypa.ParseException(instring, loc, self.errmsg, self)

    def __str__(self):
        return self.match

def MyTransformString(rule, in_string):
    def flatten(L):
        ret = []
        for i in L:
            if isinstance(i, list):
                ret.extend(flatten(i))
            else:
                ret.append(i)
        return ret

    out = []
    last_e = 0
    rule.keepTabs = True
    try:
        for t, s, e in rule.scanString(in_string):
            out.append(in_string[last_e:s])
            if t:
                if isinstance(t, pypa.ParseResults):
                    out += t.asList()
                elif isinstance(t, list):
                    out += t
                else:
                    out.append(t)
            last_e = e
        out.append(in_string[last_e:])
        out = [o for o in out if o]
        return flatten(out)
    except pypa.ParseBaseException as exc:
        if pypa.ParserElement.verbose_stacktrace:
            raise
        else:
            raise exc

def make_new_node(t, s):
    if 'parsing_suffix' in t[-1]:
        ret_word = '%i%s' % (s, t[-1]['parsing_suffix'])
    else:
        ret_word = '%i' % (s)

    ret = t[0].copy()
    ret['parsing_value'] = s
    ret['word'] = ret_word
    if 'parsing_suffix' in t[-1]:
        ret['parsing_suffix'] = t[-1]['parsing_suffix']

    min_start = -1
    max_end = -1
    prob = []
    for d in t:
        prob.append(ret['prob'])
        if min_start < 0 or min_start > d['start']:
            min_start = d['start']
        if max_end < 0 or max_end < d['end']:
            max_end = d['end']
    if min_start < 0 or max_end < 0:
        ret['start'] = 0
        ret['end'] = -1
    else:
        ret['start'] = min_start
        ret['end'] = max_end
    ret['prob'] = float(sum(prob)) / len(prob)

    return ret
