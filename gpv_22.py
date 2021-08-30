"""
Pattern Extraction API
To extract Collins' verb grammar pattern from a given sentence.

Sample:
    pattern_extract('I drive to a beautiful park and see green trees.')
Return:
    [('drive','V to n'),('see','V n')]

Can also return Collins_sentence, NP_sentence, noun_phrases:
pattern_extract(input_sent, return_sent=True)
default return_sent is False

Note:
    - 'prep' will be present in its lemma form in output
    - Cannot detect 'V and v'
    - Cannot detect 'singular_noun and singular_noun' as 'pl-n'
    - pattern_detection() only extract patterns that start with verb
    - 'V-ed' is not aligned

Files needed:
    - alignment.json
    - Collins_verb_pattern.txt

Edited Collins' verb grammar pattern:
    - Substitude 'wh-to-inf' to 'wh- to inf'
    - Substitude 'to-inf' to 'to inf'
"""
import spacy
import json

nlp = spacy.load('en_core_web_sm')

#texts that are within Collins' pattern
keys = ['about', 'across', 'after', 'against', 'among', 'and', 'around', 'as',\
        'at', 'before', 'between', 'by', 'favour', 'for', 'from', 'if', 'in',\
        'into', 'like', 'neither', 'nor', 'not', 'of', 'off', 'on', 'onto',\
        'out', 'over', 'round', 'since', 'so', 'that', 'there', 'though', 'through',\
        'to', 'together', 'toward', 'towards', 'under', 'way', 'when', 'with']

def pattern_extract(input_string, return_sent=False):
    """
    Extract Collins' pattern from a sentence
    Output format in list of tuples, [(headword, pattern), (), ...]
    """
    # Preprocess
    input_string = input_string.strip()
    tokenized_string = nlp(input_string)
    #for token in tokenized_string:
    #    print(token.text, token.tag_)
    NP_sent, noun_phrases = makeNPsent(tokenized_string)
    token_sent = nlp(NP_sent)
    for token in token_sent:
        print(token.text, token.tag_)
    
    # Alignment between SpaCy and Collins
    Collins_sent = [ alignment(token, Spacy_Collins) for token in token_sent ]
    #print(Collins_sent)
    
    # Detect pattern
    hw_pat = pattern_detection(Collins_sent, token_sent)
    #print(hw_pat)

    # Eliminate duplicate
    hw_pat = list(set(hw_pat))

    if return_sent==False:
        return hw_pat
    else:
        return hw_pat, Collins_sent, NP_sent, noun_phrases

def sent2Collins_NP(input_string):
    """
    Generate a sentence into Collins and NP sentence form.
    """
    # Preprocess
    input_string = input_string.strip()
    tokenized_string = nlp(input_string)
    
    # Generating NP sentence
    NP_sent, noun_phrases = makeNPsent(tokenized_string)
    token_sent = nlp(NP_sent)
    
    # Generating Collins sentence
    Collins_sent = [ alignment(token, Spacy_Collins) for token in token_sent ]
    
    return Collins_sent, NP_sent, noun_phrases

def alignment(token, align_dict):
    """
    Alignment between SpaCy's postag and Collins' pattern.

    Substitude SpaCy's postag to Collins' postag,
    excluding PREPs and the tokens that has text within Collins' patterns.
    """
    if token.text.lower() in keys:
        new_tag = token.text.lower()
    elif token.text in ['NP','it']:
        new_tag = 'n'
    elif token.tag_ in align_dict:
        new_tag = align_dict[token.tag_]
    else: #PREP
        new_tag = token.text.lower()
    
    return new_tag

def pattern_detection(c_sent, t_sent):
    """
    Iterate through each token of a sentence,
    start detecting for pattern if it is a verb.
    """
    hw_pat = []
    for start_idx,tag in enumerate(c_sent):
        
        # Looking for verb to start searching
        if tag in ['V|inf|v','V','-ed','-ing']:
            
            # Extract possible 5-gram with pattern
            if start_idx+5 <= len(c_sent):
                extract = c_sent[start_idx:start_idx+5] # len(Longest pattern starting with V)==5
            else:
                extract = c_sent[start_idx:]
            
            # Substitude misleading tag
            extract = ['V']+(' '.join(extract[1:])).replace('V|inf|v','inf').replace(' it ',' n ').split()
            extract = ' '.join(extract)
            
            # Determine pattern
            for pattern in patterns:
                pattern = ' '.join(pattern)
                if pattern in extract:
                    headword = t_sent[start_idx].lemma_
                    hw_pat.append( (headword, pattern, start_idx) )
                    #break
                if 'prep' in pattern:
                    #print(pattern)
                    sub_extract = extract.split()
                    prep_reg = []
                    for prep_idx,gram in enumerate(sub_extract):
                        if gram in keys and gram not in ['it','there','way','when']:
                            prep_reg.append(gram)
                            sub_extract[prep_idx] = 'prep'
                    sub_extract = ' '.join(sub_extract)
                    if pattern in sub_extract:
                        headword = t_sent[start_idx].lemma_
                        sub_pattern = pattern.split()
                        reg_idx = 0
                        for prep_idx,p in enumerate(sub_pattern):
                            if p=='prep':
                                sub_pattern[prep_idx] = prep_reg[reg_idx]
                                reg_idx += 1
                        hw_pat.append( (headword,' '.join(sub_pattern), start_idx) )

                        #break
    
    return hw_pat
    
def makeNPsent(sentence):
    """
    Substitude noun phrases of a sentence into 'NP'
    """
    chunks = list(sentence.noun_chunks)
    sent = [token.text for token in sentence]
    
    noun_phrases = []
    for chunk in chunks:
        if chunk.text in ['it', 'It']:
            continue
        end = chunk.root.i
        start = chunk.root.i - len(chunk.text.split()) + 1
        space = ['' for i in range(len(chunk.text.split())-1)]
        sent = sent[:start] + ['NP'] + space + sent[end+1:]
        noun_phrases.append( (chunk,start,end ) )
    
    sent = [word for word in sent if word != '']
    sent = ' '.join(sent)

    return sent, noun_phrases

def candidate_generate(patterns):
    """
    Sort patterns in length order
    To detect patterns from the longest to shortest
    """
    candidates = [ pattern.split() for pattern in patterns ]
    
    # Sorting
    candidates.sort(key=takeSecond, reverse=True)
    candidates.sort(key=len, reverse=True)
    candidates = candidates[:-1]
    return candidates
    
def takeSecond(elem):
    if len(elem) >= 2:
        return elem[1]
    else:
        return ''

with open('alignment.json') as f:
    Spacy_Collins = json.load(f)

with open('Collins_verb_pattern.txt') as f:
    patterns = f.read().split('\n')
    patterns = candidate_generate(patterns)

# Testing code
if __name__ == '__main__':
    
    with open('test_gpv.txt') as f:
        input_sents = f.read().split('\n')

    for sent in input_sents:
        print(sent)

        #determined_patterns = pattern_extract(sent)
        #print(determined_patterns)

        determined_patterns, csent, NPsent, noun_phrases = pattern_extract(sent, return_sent=True)
        print(determined_patterns)
        print(csent)
        print(NPsent)
        print(noun_phrases)

