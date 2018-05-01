import re
import ast
import random


def parse_equals(str):
    strspl = re.split('=| =|= ', str)
    strspl = list(filter(None, strspl))
    if len(strspl) != 2:
        raise Exception("Error parsing " + str + ".")
    lhs = strspl[0].strip(' ')
    rhs = strspl[1].strip(' ')
    return [lhs, rhs]


def startswith(string, prefixes):
    """Checks if str starts with any of the strings in the prefixes tuple.
    Returns the first string in prefixes that matches. If there is no match,
    the function returns None.
    """
    if isinstance(prefixes, tuple):
        for prefix in prefixes:
            if string.startswith(prefix):
                return prefix
        return None
    elif isinstance(prefixes, str):
        prefix = prefixes
        if string.startswith(prefix):
            return prefix
        return None
    else:
        raise Exception('Second argument must be string or a tuple of strings.')


def strsplit(string, substrings):
    """Splits up the specified string at each occurrence of any of the specified substrings,
    removing the substrings. Returns a list of strings and a list of matching substrings. If no
    match is found, return the empty list.
    """
    assert(type(string) == str)
    if type(substrings) is not list:
        substrings = [substrings]
    for substring in substrings:
        assert(type(substring) == str)
    # if not any(substring in string for substring in substrings):
    #     return [string]
    indices = list()
    for substring in substrings:
        ind = [m.start() for m in re.finditer(substring, string)]
        indices.extend(ind)
    indices.sort()
    parts = [string[i:j] for i, j in zip(indices, indices[1:] + [None])]

    # matches = list()
    # for i in range(len(parts)):d
    #     part = parts[i]
    #     for substring in substrings:
    #         if part.startswith(substring):
    #             # matches.append(substring)
    #             parts[i] = parts[i][len(substring):]
    #             break
    # assert(len(matches) == len(parts))
    return parts  # , matches


def split1(string, sep=' '):
    string_spl = string.split(sep, 1)
    out0 = string_spl[0]
    if len(string_spl) == 1:
        out1 = None
    else:
        out1 = string_spl[1]
    return out0, out1


def split1_strip(string, sep=' '):
    out0, out1 = split1(string, sep)
    if out0 is not None:
        out0 = out0.strip()
    if out1 is not None:
        out1 = out1.strip()
    return out0, out1


def is_posint(string):
    try:
        val = ast.literal_eval(string)
    except ValueError:
        return False, None
    if type(val) != int:
        return False, None
    if val <= 0:
        return False, None
    return True, val


def is_tuple(string):
    try:
        val = ast.literal_eval(string)
    except ValueError:
        return False, None
    if type(val) != tuple:
        return False, None
    return True, val


def is_tuple_of_str(input):
    input_type = type(input)
    if input_type is not tuple:
        return False
    for i in input:
        if type(i) is not str:
            return False
    return True


def is_number(string):
    try:
        val = ast.literal_eval(string)
        return True, val
    except ValueError:
        if string.count('/') != 1:
            return False, None
        else:
            num_str, den_str = string.split('/')
            num_ok, num = is_number(num_str)
            den_ok, den = is_number(den_str)
            if num_ok and den_ok:
                return True, num / den
            else:
                return False, None


def is_prob(string):
    isnum, val = is_number(string)
    if not isnum:
        return False, None
    else:
        if val < 0 or val > 1:
            return False, None
    return True, val


def strip_quotes(string):
    string_out = string
    string_out = string_out.replace('"', '')
    string_out = string_out.replace("'", "")
    return string_out


def weighted_choice(prob_cumsum):
    '''
       Returns index into prob_cumsum, chosen at random with probabilities given by prob_cumsum.
       If sum(prob_cumsum)<1, None is returned with probability (1-sum(prob_cumsum)).
    '''
    prob_cumsum1 = prob_cumsum[:]
    prob_cumsum1.append(1)
    rnd = random.random()
    ind = 0
    for i, cumsum_part in enumerate(prob_cumsum1):
        if rnd < cumsum_part:
            ind = i
            break
    if ind == len(prob_cumsum1) - 1:
        return None
    else:
        return i


def parse_sso(string):
    '''
       Parse a space-separated string of python objects and return the objects in a list.
       For example,
       line = "'reward' {'subject': 1}  [1, 2, 'foo']" gives the output
              ['reward', {'subject':1}, [1,2,'foo']]
       Note: Consecutive spaces in strings will be parsed into a single space. For example,
       line = "'re    ward' 123" gives the output
              ['re ward', 123]
    '''
    if len(string.strip()) == 0:
        return None
    stringspl = string.split()
    used_ind = list()
    nchunks = len(stringspl)
    out = list()
    startind = 0
    stopind = 1
    done = False
    while not done:
        string = ' '.join(stringspl[startind:stopind])
        try:
            valid_item = ast.literal_eval(string)
            out.append(valid_item)
            used_ind.extend(range(startind, stopind))
            startind = stopind
            stopind = startind + 1
        except Exception:
            stopind += 1
        done = (stopind == nchunks + 1)
    if len(used_ind) == nchunks:
        return out
    else:
        return None


def eval_average(datas):
    '''data is a list of float-lists (of different lengths).'''
    ndata = len(datas)
    data_lengths = [0] * ndata
    for i, data in enumerate(datas):
        data_lengths[i] = len(data)
    maxlen = max(data_lengths)
    sumpoints = [0] * maxlen
    npoints = [0] * maxlen
    for ind in range(maxlen):
        for i in range(ndata):
            if ind < data_lengths[i]:
                sumpoints[ind] += datas[i][ind]
                npoints[ind] += 1
    for ind in range(maxlen):
        sumpoints[ind] /= npoints[ind]
    return sumpoints


def dict_of_list_ind(d, ind):
    '''d is a dict where all values are lists of equal length. Returns a new dict where each
       value is the ind:th list item for each key.'''
    out = dict()
    for key, val in d.items():
        out[key] = d[key][ind]
    return out


def find_and_cumsum(seq, pattern, use_exact_match):
    '''seq is list of strings and tuples.
       pattern is a string, a tuple of strings or a list of strings and tuples of strings.
       If use_exact_match is false, count also part of tuples as match.'''

    assert(type(seq) == list)
    for s in seq:
        s_type = type(s)
        assert((s_type is str) or (s_type is tuple))

    pattern_type = type(pattern)
    assert((pattern_type is list) or (pattern_type is tuple) or (pattern_type is str))
    pattern_len = 1
    if pattern_type is tuple:
        for p in pattern:
            assert(type(p) is str)
        pattern_list = [pattern]
    elif pattern_type is list:
        pattern_len = len(pattern)
        for p in pattern:
            assert((type(p) is str) or (type(p) is tuple))
        pattern_list = pattern
    else:
        pattern_list = [pattern]

    seq_len = len(seq)

    findind = [0] * seq_len
    cumsum = [None] * seq_len
    cumsum_curr = 0
    # pattern_is_tuple = (pattern_type is tuple)
    for i in range(seq_len - pattern_len + 1):
        seqpart = seq[i: (i + pattern_len)]
        if _is_match(seqpart, pattern_list, use_exact_match):  # , pattern_is_tuple):
            findind[i] = 1
            cumsum_curr += 1
        cumsum[i] = cumsum_curr
    # The last indices for which the pattern is too long will be counted as no match:
    for i in range(seq_len - pattern_len + 1, seq_len):
        findind[i] = 0
        cumsum[i] = cumsum_curr

    return findind, cumsum


def _is_match(seq, pattern, use_exact_match):
    for i in range(len(seq)):
        if not _is_match_local(seq[i], pattern[i], use_exact_match):
            return False
    return True


def _is_match_local(st, pattern, use_exact_match):
    st_type = type(st)
    pattern_type = type(pattern)
    if pattern_type is tuple:
        if st_type is tuple:
            if use_exact_match:
                return set(st) == set(pattern)
            else:
                return set(pattern).issubset(set(st))
        else:
            return False
    else:
        if st_type is tuple:
            if use_exact_match:
                return False
            else:
                return pattern in st
        else:
            return pattern == st


def arraydivide(num, den):
    assert(type(num) == type(den) == list)
    arraylen = len(num)
    assert(len(den) == arraylen)
    out = [None] * arraylen
    for i in range(arraylen):
        if den[i] != 0:
            out[i] = num[i] / den[i]
        else:
            out[i] = num[i]
    return out


def diff(x, diffind):
    '''Returns [ x[ind1[0]]-x[0], x[ind1[1]]-x[ind1[0]], x[ind1[2]]-x[ind1[1]], ...,
                 x[-1]-x[ind1[-1]] ]
       where ind1 are the indices to the ones in diffind.'''
    assert (len(x) == len(diffind)), "x and diffind must have equal length."
    out = list()
    if len(x) > 0:
        curr = 0
        for i, indval in enumerate(diffind):
            if indval == 1:
                out.append(x[i] - curr)
                curr = x[i]
        out.append(x[-1] - curr)
    return out


def arrayind(x, ind):
    assert (len(x) == len(ind)), "x and ind must have equal length."
    out = list()
    for i, indval in enumerate(ind):
        if indval == 1:
            out.append(x[i])
    return out


def dict_inv(d_in):
    d = dict(d_in)
    key_errmsg = "All keys must be non-empty strings."
    val_errmsg = "All values must be non-empty strings or lists of non-empty strings."
    for key, val in d.items():
        if type(key) is not str:
            raise Exception(key_errmsg)
        elif len(key) == 0:
            raise Exception(key_errmsg)
        if type(val) is not list:
            val = [val]
            d[key] = val
        for v in val:
            if type(v) is not str:
                raise Exception(val_errmsg)
            elif len(v) == 0:
                raise Exception(val_errmsg)

    all_val = set()
    for key, val in d.items():
        for v in val:
            all_val.add(v)
    d_out = dict()
    for v in all_val:
        d_out[v] = list()
        for key, val in d.items():
            if v in val:
                d_out[v].append(key)
    return d_out
