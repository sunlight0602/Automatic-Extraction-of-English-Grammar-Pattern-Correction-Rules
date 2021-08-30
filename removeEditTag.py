"""
Functions for removing various format of edit tags.
"""

import re


def removeEditTag(sent):
    """Remove edit tags of a sentence.
    E.g.[- -]{+ +}

    Args:
        sent (str): given sentence to remove edit tag.

    Returns:
        before_edit (str) : sentence before editing
        after_edit (str) : sentence after editing
    """

    before_edit = re.sub('{+.+?\+}|\[-|-]|\/\/[A-Z]*', '', sent).strip()
    after_edit = re.sub('\[-.+?-]|{\+|\+}|\/\/[A-Z]*', '', sent).strip()

    before_edit = re.sub('\s+', ' ', before_edit)
    after_edit = re.sub('\s+', ' ', after_edit)

    return before_edit, after_edit


def removeEditTag_exclusive(sent):
    """Remove edit tags of a sentence exclusively, only reserves XC, D, IS, MW, PR, WC features.

    Args:
        sent (str): given sentence to remove edit tag.

    Returns:
        before_edit (str) : sentence before editing
        after_edit (str) : sentence after editing
    """

    before_edit = re.sub('{\+[^ ]+?\/\/(XC|D|IS|MW|PR|WC)\+}|\[-[^ ]+?\/\/(AG|AR|AS|CO|C|EX|HL|NS|NSL|PH|PL|PO|PS|PU|RS|SI|SP|VT|WO)\-]', '', sent).strip()
    before_edit = re.sub('{\+|\[-|\/\/[A-Z]*-]|\/\/[A-Z]*\+}', '', before_edit)
    before_edit = re.sub('\s+', ' ', before_edit)

    after_edit = re.sub('\[-.+?-]|{\+|\+}|\/\/[A-Z]*', '', sent).strip()
    after_edit = re.sub('\s+', ' ', after_edit)

    return before_edit, after_edit

def removeEditTag_P(sent):
    """Remove edit tags of a sentence, including the following feature tag.
    E.g. [- -]{+ +}(  )

    Args:
        sent (str): given sentence to remove edit tag.

    Returns:
        before_edit (str) : sentence before editing
        after_edit (str) : sentence after editing
    """
    
    before_edit = re.sub('\[-|-].+?\)|{\+.+?\)','',sent).strip()
    before_edit = re.sub('\s+', ' ', before_edit)

    after_edit = re.sub('\[-.+?-]\(.+?\)|\[-.+?-]|{\+|\+}\(.+?\)','',sent).strip()
    after_edit = re.sub('\s+', ' ', after_edit)

    return before_edit, after_edit

def removeEditTag_P_exclusive(sent):
    """Remove edit tags of a sentence, including the following feature tag,
    and only reserves XC, D, IS, MW, PR, WC features.
    E.g. [- -]{+ +}(XC)

    Args:
        sent (str): given sentence to remove edit tag.

    Returns:
        before_edit (str) : sentence before editing
        after_edit (str) : sentence after editing
    """
    
    before_edit = re.sub('-]({\+[^()]+?\+})?\((XC|D|IS|MW|PR|WC)+?\)','',sent).strip()
    before_edit = re.sub('\[[^\[\]{}]+?\]|{\+|\+}\((AG|AR|AS|CO|C|EX|HL|NS|NSL|PH|PL|PO|PS|PU|RS|SI|SP|VT|WO)+?\)|[^+]+?\+}\((XC|D|IS|MW|PR|WC)+?\)|\[-|\(.+?\)', '', before_edit)
    before_edit = re.sub('\s+', ' ', before_edit)

    after_edit = re.sub('\[-[^\[\]{}]+?-]\(.+?\)|\[-.+?-]|{\+|\+}\(.+?\)','',sent).strip()
    after_edit = re.sub('\s+', ' ', after_edit)

    return before_edit, after_edit


# Testing code
if __name__=='__main__':
    # with open('EF201403.diff.tokenized.txt', 'r') as f:
    #     EF =  f.readlines()[120:130]

    # for sent in EF:
    #     before, after = removeEditTag_P_exclusive(sent)

    #     print(sent)
    #     print(before)
    #     print(after)

    before, after = removeEditTag('Hello [-.-]{+!+}')
    print(before)
    print(after)
    
    # ??
    before, after = removeEditTag_exclusive('Hello [-A-]{+B+}(XC) [-.-]{+!+}(PU)')
    print(before)
    print(after)
    
    before, after = removeEditTag_P('Hello [-.-]{+!+}(PU)')
    print(before)
    print(after)
    
    before, after = removeEditTag_P_exclusive('Hello [-A-]{+B+}(XC) [-.-]{+!+}(PU)')
    print(before)
    print(after)