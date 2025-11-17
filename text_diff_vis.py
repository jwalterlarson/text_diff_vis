"""
text_diff_vis:  A visualizer/highlighter of differences in closely related text passages.
"""
from collections import OrderedDict
import string
import re
import difflib
from pprint import pprint

class AnsiColors:
    """
    ANSI color code and typesetting sequences.
    """
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    MAGENTA = '\033[35m'
    BLUE = '\033[94m'
    GREEN = '\033[32m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    BLACK = '\033[30m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

ansi_colors = AnsiColors()

def buf_to_tokens(buf, 
                  remove_punctuation=True,
                  exempt_punc_marks=['-', '$', '/'],
                  junk=['�', '_x000D_', 'x000D', '¬']):
    """
    Take input character buffer and split on whitespace,
    removing punctuation marks if desired.
    
    Returns list of tokens.
    """
    
    # Split on <CR>.  Straight str.replace() didn't work.
    buff = ' '.join(buf.split('\n'))
    cruft_strings = ['_x000D_', 'x000D',  r'\r\n', r'\n\n', r'\n?', r'\n']
    for s in cruft_strings:
        buff.replace(s, ' ')
    tokens = buff.split(' ')
    
    if remove_punctuation:
        # Grab corpus of punctuation marks.
        punc_marks = string.punctuation
        # Remove Exempt punctuation marks.
        for m in exempt_punc_marks:
            punc_marks = punc_marks.replace(m, '')
        # Create regex pattern.
        pattern = r"[{}]".format(punc_marks)
        #tokens = [re.sub(r'[^\w\s]', '', t) for t in tokens
        tokens = [re.sub(pattern, '', t) for t in tokens]
        for j in junk:
            tokens = [t.replace(j, '') for t in tokens]
    
    # Remove leading/trailing whitespace and empty tokens.
    tokens = [t.strip() for t in tokens]
    tokens = [t for t in tokens if t != '']
    
    return tokens

def label_changes_and_matches(old_buf, new_buf):
    """
    Uses a difflib Matcher to 'chunk' a pair of previously
    tokenised buffers and label these chunks as:
    
    * removed--present in old_buf but absent in new_buf
    * added--present in new_buf but absent in old_buf
    * shared--present in both buffers.
    
    The idea is that we can then interleave these results
    to create a compelling visualisaiton of the changes.
    
    Returns a dict of lists with the following keys:
    
    * 'deletions'
    * 'insertions'
    * 'matches'

    The indexing convention here is that the individual 
    deletions/insertions precede the corresponding 
    matches.
    """
    result = OrderedDict([('deletions', []),
                          ('insertions', []),
                          ('matches', [])])
    matcher = difflib.SequenceMatcher(a=old_buf, b=new_buf)
    next_rem_start = 0
    next_add_start = 0
    for match in list(matcher.get_matching_blocks()):
        result['deletions'].append(old_buf[next_rem_start:match.a])
        next_rem_start = match.a + match.size
        result['insertions'].append(new_buf[next_add_start:match.b])
        next_add_start = match.b + match.size
        result['matches'].append(old_buf[match.a:match.a+match.size])
        
    return result

def is_valid_changes_dict(changes):
    """
    Standard sanity checks applied to a changes 
    dict instance:
    
    * is a dict;
    * has all required keys;
    * has the same number of segments in each keyed list
    
    Returns True if fed a valid changes dict instance, False
    if not.
    """
    # Argument changes must be a dict.
    if not isinstance(changes, dict):
        print('ERROR--input argument \"changes\" is not a dict!')
        print('ERROR--type(changes) = ', type(changes))
        return False
    
    # The dict must contain the following keys
    legit_keys = ['deletions', 'insertions', 'matches']
    if list(set(legit_keys).difference(changes.keys())) != []:
        print('ERROR--key mismatch in input argument dict \"changes\"')
        print('ERROR--changes.keys() = ', changes.keys())
        print('ERROR--expected changes.keys() = ', legit_keys)
        return False
    
    # All keyed lists have the same length.
    num_segs = []
    for k in changes.keys():
        num_segs.append(len(changes[k]))
    min_segs = min(num_segs)
    max_segs = max(num_segs)
    if min_segs != max_segs:
        print('ERROR--number redaction/addition/matches segments differ!')
        print('ERROR--segment lengths list = ', num_segs)
        return False
    else:
        return True

def interleave_and_format(changes):
    """
    Takes an input dict describing changes between 
    two text buffers--'old' and 'new'--as viewed by
    the 'new' buffer.  The text is formatted as follows
    
    * RED--text present in the 'old' buffer but absent 
      in the 'new' buffer;
    * GREEN--text present in the 'new' buffer but absent
      in the 'old' buffer; and
    * YELLOW--text shared between the two buffers.
    
    A single text string is returned that includes the 
    appropriate ANSI control sequences to colour the 
    text in most terminal displays (and will render as
    such with Python's print() function).
    """
    # Sanity checks offloaded to is_valid_changes_dict().
    if is_valid_changes_dict(changes):
        seg_count = len(changes['matches'])
    else:
        return None
    
    # Get Started--set bold face text.
    # result = ascii_color.BOLD # Disable--somehow
    # renders green as grey in Jupyter.  Us empty instead.
    result = ''
    # Concatenate formatted segments.
    for i in range(0, seg_count):
        if len(changes['deletions'][i]) > 0:
            result += ansi_colors.RED + ' '.join(changes['deletions'][i]) + ' '
        if len(changes['insertions'][i]) > 0:
            result += ansi_colors.GREEN + ' '.join(changes['insertions'][i]) + ' '
        if len(changes['matches'][i]) > 0:
            result += ansi_colors.YELLOW + ' '.join(changes['matches'][i])
            if i < seg_count - 1:
                result += ' '
    
    # Finish and clean out double white spaces.
    result += ansi_colors.END
    result = ' '.join(result.split()).strip()
    
    return result

"""
Trivial test (with apologies to Orwell).
"""
if __name__ == '__main__':
    
    # Before/after text specimens.
    text1 = """Citizens!  The government regrets to announce that the chocolate 
               ration has been decreased from 50g/day to 25g/day."""
    text2 = """Citizens!  The government is pleased to announce that the chocolate 
               ration has been increased from 50g/day to 25g/day.  Doubleplusgood!"""

    print("Old text: \n {0} \n New Text: \n {1}".format(text1, text2))
    
    # Tokenize.
    old = buf_to_tokens(text1)
    new = buf_to_tokens(text2)

    # Detect changes and label them.
    changes = label_changes_and_matches(old, new)

    # Print merged old/new texts with highlighted changes.
    print("""Merged text with 
            * Common words in YELLOW
            * Deleted words in RED
            * Inserted words in GREEN""")
    print(interleave_and_format(changes))

    
