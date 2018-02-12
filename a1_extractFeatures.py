import numpy as np
import sys
import argparse
import os
import json
import string

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

second_person_list = []
with open("Second-person") as file:  # add /u/cs401/WordLists/ OR submit this file as well
    second_person_list = file.read().lower().splitlines()

third_person_list = []
with open("Third-person") as file:  # add /u/cs401/WordLists/ OR submit this file as well
    third_person_list = file.read().lower().splitlines()

common_noun_tags = ["nn", "nns"]
proper_noun_tags = ["nnp", "nnps"]
adverb_tags = ["rb", "rbr", "rbs"]
wh_word_tags = ["wdt", "wp", "wp$", "wrb"]

slang_list = []
with open("Slang") as file:  # add /u/cs401/WordLists/ OR submit this file as well
    slang_person_list = file.read().lower().splitlines()

def extract1(comment):
    ''' This function extracts features from a single comment

    Parameters:
        comment : string, the body of a comment (after preprocessing)

    Returns:
        feats : numpy Array, a 173-length vector of floating point features (only the first 29 are expected to be filled, here)
    '''

    # TODO: your code here
    feat_row = np.zeros(173)

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

    # helpers for 15-17
    num_sentences = 0  # will be based on the num of \n, including the \n we will add if the comment did not end on one
    num_characters = 0  # tally up the number of characters in the
    num_non_punct_only_tokens = 0

    # make a set of parallel array, where each index matches a token/TAG pair from comment
    token_tags = comment.split(" ")
    token_tags_len = len(token_tags)

    token_list = []
    tag_list = []

    # we can improve performance by performing all of our counting feature step in this single for loop
    for t in token_tags:

        # if we happen across a \n, add \n into the tags parallel -> will be used for sentence-related features
        if t == "\n":
            token_list.append("\n")
            tag_list.append("\n")
            num_sentences += 1
        else:
            # this assumes that everything else has been tagged properly and thus has a "/" separating the token and tag
            ind = t.rfind("/")

            token = t[:ind]
            tag = t[ind + 1:]

            # process the uppercase sensitive features before we change the token to lowercase for everything else
            if len(token) >= 3 and token.isupper():
                num_uppercase += 1

            token = token.lower()
            tag = tag.lower()

            token_list.append(token)
            tag_list.append(tag)

            num_characters += len(token)
            num_non_punct_only_tokens += 1 if not all([c in string.punctuation for c in token]) else 0

            if token in first_person_list:
                num_first_person += 1

            if token in second_person_list:
                num_second_person += 1

            if token in third_person_list:
                num_third_person += 1

            if tag == "cc":
                num_cc += 1

            if tag == "vbd":
                num_past_verbs += 1

            # come back to future tense
            if token in ["'ll", "will", "gonna"]:
                num_future_verbs += 1

            if tag == ",":
                num_commas += 1

            if len(token) >= 2 and all([c in string.punctuation for c in token]):
                num_multi_punct += 1

            if tag in common_noun_tags:
                num_common_nouns += 1

            if tag in proper_noun_tags:
                num_proper_nouns += 1

            if tag in adverb_tags:
                num_adverbs += 1

            if tag in wh_word_tags:
                num_wh_words += 1

            if token in slang_list:
                num_slang += 1

            


    # if the last token/tag pair is not \n, add a \n pair
    if token_tags[token_tags_len - 1] != "\n":
        token_list.append("\n")
        tag_list.append("\n")
        num_sentences += 1

    # track 15-17

    # since we include \n in that count and num_sentences counts \n
    num_tokens = token_tags_len - num_sentences
    avg_length_sentence = num_tokens / num_sentences

    # make sure to exclude punctuation only tokens
    avg_len_token = 0
    if num_non_punct_only_tokens != 0:
        avg_len_token = num_characters / num_non_punct_only_tokens

    ### Assign features to appropriate index ###

    # 1. Number of first-person pronouns
    feat_row[0] = num_first_person

    # 2. Number of second-person pronouns
    feat_row[1] = num_second_person

    # 3. Number of third-person pronouns
    feat_row[2] = num_third_person

    # 4. Number of coordinating conjunctions
    feat_row[3] = num_cc

    # 5. Number of past-tense verbs
    feat_row[4] = num_past_verbs

    # 6. Number of future-tense
    feat_row[5] = num_future_verbs

    # 7. Number of commas
    feat_row[6] = num_commas

    # 8. Number of multi-character punctuation tokens
    feat_row[7] = num_multi_punct

    # 9. Number of common nouns
    feat_row[8] = num_common_nouns

    # 10. Number of proper nouns
    feat_row[9] = num_proper_nouns

    # 11. Number of adverbs
    feat_row[10] = num_adverbs

    # 12. Number of wh-words
    feat_row[11] = num_wh_words

    # 13. Number of slang acronyms
    feat_row[12] = num_slang

    # 14. Number of words in uppercase(>= 3 letters long)
    feat_row[13] = num_uppercase

    # 15. Average length of sentences, in tokens
    feat_row[14] = avg_length_sentence

    # 16. Average length of tokens, excluding punctuation - only tokens, in characters
    feat_row[15] = avg_len_token

    # 17. Number of sentences.
    feat_row[16] = num_sentences

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
        print(comment)
        print(feats[i])

    print(feats)

    np.savez_compressed(args.output, feats)

    
if __name__ == "__main__": 

    parser = argparse.ArgumentParser(description='Process each .')
    parser.add_argument("-o", "--output", help="Directs the output to a filename of your choice", required=True)
    parser.add_argument("-i", "--input", help="The input JSON file, preprocessed as in Task 1", required=True)
    args = parser.parse_args()

    main(args)

