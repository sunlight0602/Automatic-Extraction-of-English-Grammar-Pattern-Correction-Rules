"""
Function to generate alignment between two sequences with lowest cost.

Usage:
from twoSequenceAlignment import twoSequenceAlignment
s1, s2, final_score = twoSequenceAlignment(str1, str2, p_xy, p_gap, r_match)

Note:
    - the method is implemented using DP
    - but used greedy method while backtracking XD
    - so it only returns one alignment even if there are multiple kind of alignemets.
"""


def twoSequenceAlignment(str1, str2, p_xy, p_gap, r_match):
    """To generate alignment between two sequences with lowest cost.

    Args:
        str1 (list) : first sequence for alignment.
        str2 (list) : second sequence for alignment.
        p_xy (int) : penalty for mismatch.
        p_gap (int) : penalty for gap.
        r_match (int) : reward for match.

    Returns:
        s1 (list) : first sequence after alignment.
        s2 (list) : second sequence after alignment.
        final_score (int) : score for output alignment.
    """

    # Initialize dp_matrix
    dp_matrix = []
    for i in range(len(str2)+1):
        if i==0:
            temp = [ j*p_gap for j in range(len(str1)+1) ]
        else:
            temp = []
            for j in range(len(str1)+1):
                if j==0:
                    temp.append(i*p_gap)
                else:
                    temp.append(0)
        dp_matrix.append(temp)

    # Fill in dp_matrix
    for i in range(1, len(str2)+1):
        for j in range(1, len(str1)+1):
            word_miss = dp_matrix[i-1][j] + p_gap
            if str1[j-1]==str2[i-1]:
                word_word = dp_matrix[i-1][j-1] + r_match
            else:
                word_word = dp_matrix[i-1][j-1] + p_xy
            miss_word = dp_matrix[i][j-1] + p_gap

            dp_matrix[i][j] = max(word_miss, word_word, miss_word)
    final_score = dp_matrix[i][j]

    # # Print dp_matrix
    # for line in dp_matrix:
    #    print(line)

    # Backtrack
    s1 = []
    s2 = []
    s1, s2 = backtrack(dp_matrix, str1, str2, p_xy, p_gap, r_match, i, j, s1, s2)

    return s1, s2, final_score 


def backtrack(dp_matrix, str1, str2, p_xy, p_gap, r_match, i, j, s1, s2):

    if i==0 and j==0:
        s1.reverse()
        s2.reverse()
        return s1, s2

    #print('cur:', dp_matrix[i][j])

    if dp_matrix[i-1][j-1] + p_xy == dp_matrix[i][j] and i-1>=0 and j-1>=0:
        s1.append(str1[j-1])
        s2.append(str2[i-1])
        #print(s1, s2)
        #print(dp_matrix[i-1][j-1])
        backtrack(dp_matrix, str1, str2, p_xy, p_gap, r_match, i-1, j-1, s1, s2)
    elif dp_matrix[i-1][j] + p_gap == dp_matrix[i][j] and i-1>=0 and j>=0:
        s1.append('-')
        s2.append(str2[i-1])
        #print(s1, s2)
        #print(dp_matrix[i-1][j])
        backtrack(dp_matrix, str1, str2, p_xy, p_gap, r_match, i-1, j, s1, s2)
    elif dp_matrix[i][j-1] + p_gap == dp_matrix[i][j] and i>=0 and j-1>=0:
        s1.append(str1[j-1])
        s2.append('-')
        #print(s1, s2)
        #print(dp_matrix[i][j-1])
        backtrack(dp_matrix, str1, str2, p_xy, p_gap, r_match, i, j-1, s1, s2)
    elif dp_matrix[i-1][j-1] + r_match == dp_matrix[i][j] and str1[j-1]==str2[i-1] and i-1>=0 and j-1>=0:
        #print(dp_matrix[i-1][j-1], r_match, dp_matrix[i][j])
        s1.append(str1[j-1])
        s2.append(str2[i-1])
        #print(s1, s2)
        #print(dp_matrix[i-1][j-1])
        backtrack(dp_matrix, str1, str2, p_xy, p_gap, r_match, i-1, j-1, s1, s2)
    else:
        print('something wrong')

    return s1, s2


# Testing code
if __name__=='__main__':
    str1 = 'V about n n'
    str2 = 'V n of n'

    #str1 = 'V n for n'
    #str2 = 'V adj V n that'

    mismatch_penalty = 0
    gap_penalty = 0
    match_reward = 1

    str1, str2, final_score = twoSequenceAlignment(str1.split(), str2.split(), mismatch_penalty, gap_penalty, match_reward)

    print(str1)
    print(str2)
    print(final_score)
