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

# Load first-person list
first_person_list = []
with open("First-person") as file:  # add /u/cs401/WordLists/ OR submit this file as well
    first_person_list = file.read().lower().splitlines()



def extract1(comment):
    ''' This function extracts features from a single comment

    Parameters:
        comment : string, the body of a comment (after preprocessing)

    Returns:
        feats : numpy Array, a 173-length vector of floating point features (only the first 29 are expected to be filled, here)
    '''

    # TODO: your code here
    feat_row = np.zeros(173)

    # make a set of parallel array, where each index matches a token/TAG pair from comment
    token_tags = comment.split(" ")
    token_tags_len = len(token_tags)

    token_tag_list = np.zeros(2, token_tags_len)

    # if the last token/tag pair is not \n, add a \n pair
    if token_tags[token_tags_len - 1] != "\n":
        token_tags_len += 1
        token_tag_list = token_tag_list.reshape((2, token_tag_list))
        token_tag_list[0, token_tags_len - 1] = "\n"
        token_tag_list[1, token_tags_len - 1] = "\n"

    for t in len(token_tags):

        # if we happen across a \n, add \n into the tags parallel -> will be used for sentence-related features
        if token_tags[t] == "\n":
            token_tag_list[0, t] = "\n"
            token_tag_list[1, t] = "\n"
        else:
            ind = token_tags[t].rfind("/")
            token_tag_list[0, t] = token_tags[:ind]  # token
            token_tag_list[1, t] = token_tags[ind:]  # tag

    # track 1-14
    num_first_person = 0
    num_second_person = 0
    num_third_person = 0
    num_cc = 0
    num_past_verbs = 0
    num_future_verbs = 0
    num_commas = 0
    num_multi_punct = 0
    num_common_nouns = 0
    num_proper_nouns = 0
    num_adverbs = 0
    num_wh_words = 0
    num_slang = 0
    num_uppercase = 0

    # track 15-17
    avg_length_sentence = 0  # number of sentences / number of tokens -> num_sentences / (token_tags_len - num_sentences), since we include \n in that count and num_sentences counts \n

    avg_len_token = 0  #


    num_sentences = 0  # 


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

