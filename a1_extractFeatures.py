import numpy as np
import sys
import argparse
import os
import json

# Classes
left = 0
center = 1
right = 2
alt = 3

class_lookup = {
    "Left" : left,
    "Center" : center,
    "Right" : right,
    "Alt" : alt
}

# Declare our word lists variables etc


def extract1( comment ):
    ''' This function extracts features from a single comment

    Parameters:
        comment : string, the body of a comment (after preprocessing)

    Returns:
        feats : numpy Array, a 173-length vector of floating point features (only the first 29 are expected to be filled, here)
    '''

    # TODO: your code here
    feat_row = np.zeros(173)

    # 1. Number of first-person pronouns

    # 2. Number of second-person pronouns

    # 3. Number of third-person pronouns
    # 4. Number of coordinating conjunctions
    # 5. Number of past-tense verbs
    # 6. Number of future-tense verbs
    # 7. Number of commas
    # 8. Number of multi-character punctuation tokens
    # 9. Number of common nouns
    # 10. Number of proper nouns
    # 11. Number of adverbs
    # 12. Number of wh-words
    # 13. Number of slang acronyms
    # 14. Number of words in uppercase(>= 3 letters long)
    # 15. Average length of sentences, in tokens
    # 16. Average length of tokens, excluding punctuation - only tokens, in characters
    # 17. Number of sentences.

    ### Bristol, Gilhooly, and Logie norms ###

    # 18. Average of AoA(100 - 700) from Bristol, Gilhooly, and Logie norms
    # 19. Average of IMG from Bristol, Gilhooly, and Logie norms
    # 20. Average of FAM from Bristol, Gilhooly, and Logie norms
    # 21. Standard deviation of AoA(100 - 700) from Bristol, Gilhooly, and Logie norms
    # 22. Standard deviation of IMG from Bristol, Gilhooly, and Logie norms
    # 23. Standard deviation of FAM from Bristol, Gilhooly, and Logie norms

    ### Warringer norms ###

    # 24. Average of V.Mean.Sum from Warringer norms
    # 25. Average of A.Mean.Sum from Warringer norms
    # 26. Average of D.Mean.Sum from Warringer norms
    # 27. Standard deviation of V.Mean.Sum from Warringer norms
    # 28. Standard deviation of A.Mean.Sum from Warringer norms
    # 29. Standard deviation of D.Mean.Sum from Warringer norms

    return feat_row


def main(args):

    data = json.load(open(args.input))
    feats = np.zeros((len(data), 173+1))
    print(data)

    # TODO: your code here

    for i in range(len(data)):
        line = data[i]
        comment = line['body']
        # the first 29 features
        feats[i, 0:173] = extract1(comment)  # first 173, everything after 29th are still zeros
        #print(feats[i])

        # feat 30-173

        # feat 174 ie integer for class
        cat = line['cat']
        feats[i, 173] = class_lookup[cat]
        print(feats[i])

    print(feats)

    np.savez_compressed(args.output, feats)

    
if __name__ == "__main__": 

    parser = argparse.ArgumentParser(description='Process each .')
    parser.add_argument("-o", "--output", help="Directs the output to a filename of your choice", required=True)
    parser.add_argument("-i", "--input", help="The input JSON file, preprocessed as in Task 1", required=True)
    args = parser.parse_args()

    main(args)

