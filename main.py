"""
Files needed:
    - removeEditTag.py
    - twoSequenceAlignment.py
    - gpv_24.py
    - verb_pattern.json
    - EF877.edit.txt

Output files:
    - Error_message.txt
    - Error_pattern_example.json
    - Error_pattern_example.txt: content same as above
    - Error_pattern.json
    - Error_pattern.txt: content same as above

Output example:
    - From Error_pattern_example.txt:
        ('give', 'V n to>>V n', [9, 7469, ...])
        (headword, wrong_pattern>>correct_pattern, examples_in_EF)
    - From Error_pattern.txt:
        ('give', 'V to n>>V n', 325)
        (headword, wrong_pattern>>correct_pattern, frequency_in_EF)

Note:
    - adjust threshold() for desired result
"""

from multiprocessing import Pool
import re
import json
from collections import defaultdict
from datetime import datetime

import spacy

from removeEditTag import removeEditTag_exclusive # for EF877
#from removeEditTag import removeEditTag_P_exclusive # for EF2014
from gpv_24 import pattern_extract, sent2Collins_NP 
from twoSequenceAlignment import twoSequenceAlignment

nlp = spacy.load('en_core_web_lg')


def threshold(dic):
    """
    Patterns with first 5 large frequency
    Frequency > 10
    """
    for key in list(dic.keys()):
        sub = dic[key]
        sub = sorted(sub.items(), key=lambda v: v[1], reverse=True) #[:5]
        sub = [ pat_freq for pat_freq in sub if pat_freq[1]>10 ]
       
        for item in list(dic[key].items()):
            if item not in sub:
                del dic[key][item[0]]

        if list(dic[key].keys())==[]:
            del dic[key]
        
    return dic


with open('verb_pattern.json') as f:
    Collins_verb_pattern = json.load(f)
def checkInCollins(pattern_after):
    new_pattern_after = []
    for pattern in pattern_after:
        if pattern[0] in Collins_verb_pattern.keys():
            if pattern[1] in Collins_verb_pattern[ pattern[0] ]:
                new_pattern_after.append( pattern )
            else:
                pass
                #print('"{}" is not a pattern of "{}"'.format(pattern[1], pattern[0]))
        else:
            pass
            #print('"{}" not in Collins'.format(pattern[0]))
            
    return new_pattern_after


def alignment_post_process(s1, s2, score):
    """
    Only reserve alignments with score >= 2
    
    To check if s1 and s2 are actually relevent
    """
    if score<2:
        return '', ''

    # Strip head and tail's '-'
    start_idx = s1.index('V')
    for idx, tag in reversed(list(enumerate(s1[start_idx:]))):
        if tag!='-':
            end_idx = idx+start_idx
            break
    extract_s1 = [ tag for tag in s1[start_idx:end_idx+1] ]
    extract_s2 = [ tag for tag in s2[start_idx:end_idx+1] ]
    extract = [ (extract_s1[i], extract_s2[i]) for i in range(len(extract_s1)) ]

    # Calculate scores
    score = [1]
    for idx, s1_s2_tag in enumerate(extract[1:]):
        if s1_s2_tag[0]==s1_s2_tag[1]:
            score.append(score[idx]+1)
        else:
            score.append(score[idx]-1)

    # Find length of determined pattern
    slash_flag = False
    longest_idx = -1
    for idx, s in enumerate(score[1:]):
        if s<score[idx] and slash_flag==False:
            slash_flag = True
        elif s<score[idx] and slash_flag==True:
            longest_idx = idx
            break
    if longest_idx==-1:
        longest_idx = len(score)-1
    
    # Extract determined pattern with caculated length
    pat_before = [ s2_tag for s1_tag, s2_tag in extract[:longest_idx+1] if s2_tag.isalpha() ]
    pat_after = [ s1_tag for s1_tag, s2_tag in extract[:longest_idx+1] if s1_tag.isalpha() ]
   
    return pat_before, pat_after


def gen_ef_pattern(sent_idx):
    
    EF_i, sent = sent_idx
    
    before_edit, after_edit = removeEditTag_exclusive(sent)

    # Extract pattern
    try:
        csent_before, NP_sent_before, noun_phrase_before = sent2Collins_NP(before_edit)
        pattern_after, _, NP_sent_after, noun_phrase_after = pattern_extract(after_edit, return_sent=True)
    except:
        return {"status": "error", "log": 'pattern_extract() fails\n{}\n{}'.format(before_edit, after_edit)}

    # Only reserve if headword and pattern combination is in Collins
    pattern_after = checkInCollins(pattern_after)

    # Add noun text into patterns
    """
    TO DO
    """

    # Pattern alignment, using pattern_after's headword as index
    doc = nlp(NP_sent_before)
    NP_sent_before = [ token.lemma_ for token in doc ]
    hw_pat_temp = []
    for hw_pat_after in pattern_after:

        # Preprocess
        # Determine str1
        str1 = hw_pat_after[1].split()

        # Determine str2
        # Find index of headword in before_edit
        if hw_pat_after[0] in NP_sent_before:
            hw_idx = NP_sent_before.index(hw_pat_after[0])
        else:
            return {"status": "error", "log": '{} is newly inserted into after_edit'.format((hw_pat_after[0]))}

        # Extract str2
        if hw_idx+5 <= len(csent_before):
            str2 = ['V'] + csent_before[ hw_idx+1:hw_idx+5 ]
        else:
            str2 = ['V'] + csent_before[ hw_idx+1: ]
        for idx,tag in enumerate(str2[1:]):
            if tag in ['V|inf|v','V']:
                str2 = str2[:idx+1]+['inf']

        # Optimal alignment
        try:
            aligned_s1, aligned_s2, score = twoSequenceAlignment(str1, str2, 0, 0, 1)
        except:
            return {"status": "error", "log": 'twoSequenceAlignment() fails, str1={}, str2={}'.format(str1, str2)}

        # Post process optimal alignment
        pat_before, pat_after = alignment_post_process(aligned_s1, aligned_s2, score)

        # Save result
        if pat_before!='' and pat_before!=pat_after:
            change = ' '.join(pat_before)+'>>'+' '.join(pat_after)
            if (hw_pat_after[0],change,EF_i) not in hw_pat_temp:
                hw_pat_temp.append( (hw_pat_after[0],change,EF_i) )
                
                
    return {"status": "success", "result": hw_pat_temp}


if __name__=='__main__':


    error_file = open('Error_message.txt','w')

    hw_pat_dict = defaultdict(lambda:defaultdict(lambda:0))
    hw_pat_dict_example = defaultdict(lambda:defaultdict(list))

    # Start timing
    start_time = datetime.now()
    
    input_f_idx = enumerate(open('EF877.edit.txt'))
    
    workers = 20
    with Pool(workers) as p:
        for res in p.imap(gen_ef_pattern, input_f_idx):
            if res['status'] == 'success':
                for hw,change,i in res['result']:
                    hw_pat_dict[hw][change]+=1
                    hw_pat_dict_example[hw][change].append(i)
            elif res['status'] == 'error':
                print(res['log'], file=error_file)

    
    # Threshold
    hw_pat_dict = threshold(hw_pat_dict)
    
    # End timing
    print(str(datetime.now()-start_time))

    # Output json file
    with open('Error_pattern.json', 'w') as f:
        json.dump(hw_pat_dict, f)

    # Output in txt format
    hw_pat_dict = [ (hw, pat, hw_pat_dict[hw][pat]) for hw in hw_pat_dict for pat in hw_pat_dict[hw] ]
    with open('Error_pattern.txt', 'w') as f:
        for line in hw_pat_dict:
            f.write(str(line)+'\n')

    # Output example json file
    with open('Error_pattern_example.json','w') as f:
        json.dump(hw_pat_dict_example, f)

    # Ouput in txt format
    hw_pat_dict_example = [ (hw, pat, hw_pat_dict_example[hw][pat]) for hw in hw_pat_dict_example for pat in hw_pat_dict_example[hw] ]
    with open('Error_pattern_example.txt', 'w') as f:
        for line in hw_pat_dict_example:
            f.write(str(line)+'\n')
    
    error_file.close()
    
