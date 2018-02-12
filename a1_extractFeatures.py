import numpy as np
import sys
import argparse
import os
import json
import string
import csv

# Classes
left = 0
center = 1
right = 2
alt = 3

class_lookup = {
    "left" : left,
    "center" : center,
    "right" : right,
    "alt" : alt
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

# BGL norms file
BGL_dict = {}
with open("BristolNorms+GilhoolyLogie.csv") as file:
    reader = csv.reader(file)
    for row in reader:
        key = row[1]
        BGL_dict[key] = row

# Warringer norms file
Warringer_dict = {}
with open("Ratings_Warriner_et_al.csv") as file:
    reader = csv.reader(file)
    for row in reader:
        key = row[1]
        Warringer_dict[key] = row

### LIWC/Receptiviti files ###

# Alt IDs
alt_ID_to_ind = {}
with open("feats/Alt_IDs.txt") as file:  # REMEMBER TO CHANGE THIS PATH RELATIVE TO CDF LAB
    ind = 0
    for row in file:
        alt_ID_to_ind[row.strip()] = ind
        ind += 1

# Center IDs
center_ID_to_ind = {}
with open("feats/Center_IDs.txt") as file:
    ind = 0
    for row in file:
        center_ID_to_ind[row.strip()] = ind
        ind += 1

# Left IDs
left_ID_to_ind = {}
with open("feats/Left_IDs.txt") as file:
    ind = 0
    for row in file:
        left_ID_to_ind[row.strip()] = ind
        ind += 1

# Right IDs
right_ID_to_ind = {}
with open("feats/Right_IDs.txt") as file:
    ind = 0
    for row in file:
        right_ID_to_ind[row.strip()] = ind
        ind += 1

# Alt feats
alt_feats = np.load("feats/Alt_feats.dat.npy")

# Center feats
center_feats = np.load("feats/Center_feats.dat.npy")

# Left feats
left_feats = np.load("feats/Left_feats.dat.npy")

# Right feats
right_feats = np.load("feats/Right_feats.dat.npy")


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

    # 18-29
    AoA_array = []
    IMG_array = []
    FAM_array = []

    VMeanSum_array = []
    AMeanSum_array = []
    DMeanSum_array = []

    # make a set of parallel array, where each index matches a token/TAG pair from comment
    token_tags = comment.split(" ")
    token_tags = [t if not t.isspace() or t == "\n" else "" for t in token_tags]
    token_tags = list(filter(None, token_tags))
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

            # Norms
            if token in BGL_dict:
                AoA_array.append(BGL_dict[token][3])
                IMG_array.append(BGL_dict[token][4])
                FAM_array.append(BGL_dict[token][5])

            if token in Warringer_dict:
                VMeanSum_array.append(Warringer_dict[token][2])
                AMeanSum_array.append(Warringer_dict[token][5])
                DMeanSum_array.append(Warringer_dict[token][8])


    # if the last token/tag pair is not \n, add a \n pair
    if token_tags and token_tags[token_tags_len - 1] != "\n":
        token_list.append("\n")
        tag_list.append("\n")
        num_sentences += 1

    # track 15-17

    # since we include \n in that count and num_sentences counts \n
    num_tokens = token_tags_len - num_sentences
    avg_length_sentence = num_tokens / num_sentences if num_sentences > 0 else 0

    # make sure to exclude punctuation only tokens
    avg_len_token = 0
    if num_non_punct_only_tokens > 0:
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
    avg_AoA = 0
    std_AoA = 0
    AoA_np_array = np.array(AoA_array).astype(np.float)
    if AoA_np_array.size:
        avg_AoA = np.mean(AoA_np_array)
        std_AoA = np.std(AoA_np_array)  # 21.
    feat_row[17] = avg_AoA

    # 19. Average of IMG from Bristol, Gilhooly, and Logie norms
    avg_IMG = 0
    std_IMG = 0
    IMG_np_array = np.array(IMG_array).astype(np.float)
    if IMG_np_array.size:
        avg_IMG = np.mean(IMG_np_array)
        std_IMG = np.std(IMG_np_array)  # 22.
    feat_row[18] = avg_IMG

    # 20. Average of FAM from Bristol, Gilhooly, and Logie norms
    avg_FAM = 0
    std_FAM = 0
    FAM_np_array = np.array(FAM_array).astype(np.float)
    if FAM_np_array.size:
        avg_FAM = np.mean(FAM_np_array)
        std_FAM = np.std(FAM_np_array)  # 23.
    feat_row[19] = avg_FAM

    # 21. Standard deviation of AoA(100 - 700) from Bristol, Gilhooly, and Logie norms
    feat_row[20] = std_AoA

    # 22. Standard deviation of IMG from Bristol, Gilhooly, and Logie norms
    feat_row[21] = std_IMG

    # 23. Standard deviation of FAM from Bristol, Gilhooly, and Logie norms
    feat_row[22] = std_FAM

    ### Warringer norms ###

    # 24. Average of V.Mean.Sum from Warringer norms
    avg_vms = 0
    std_vms = 0
    vms_np_array = np.array(VMeanSum_array).astype(float)
    if vms_np_array.size:
        avg_vms = np.mean(vms_np_array)
        std_vms = np.std(vms_np_array)  # 27.
    feat_row[23] = avg_vms

    # 25. Average of A.Mean.Sum from Warringer norms
    avg_ams = 0
    std_ams = 0
    ams_np_array = np.array(AMeanSum_array).astype(float)
    if ams_np_array.size:
        avg_ams = np.mean(ams_np_array)
        std_ams = np.std(ams_np_array)  # 28.
    feat_row[24] = avg_ams

    # 26. Average of D.Mean.Sum from Warringer norms
    avg_dms = 0
    std_dms = 0
    dms_np_array = np.array(DMeanSum_array).astype(float)
    if dms_np_array.size:
        avg_dms = np.mean(dms_np_array)
        std_dms = np.std(dms_np_array)  # 29.
    feat_row[25] = avg_dms

    # 27. Standard deviation of V.Mean.Sum from Warringer norms
    feat_row[26] = std_vms

    # 28. Standard deviation of A.Mean.Sum from Warringer norms
    feat_row[27] = std_ams

    # 29. Standard deviation of D.Mean.Sum from Warringer norms
    feat_row[28] = std_dms

    return feat_row


def main(args):

    data = json.load(open(args.input))
    feats = np.zeros((len(data), 173+1))

    # TODO: your code here

    for i in range(len(data)):
        line = data[i]
        comment = line['body']
        id = line['id'].lower()
        cat = line['cat'].lower()

        # the first 29 features
        feats[i, 0:173] = extract1(comment)

        # feat 30-173
        if cat == "alt":
            feats[i, 29:173] = alt_feats[alt_ID_to_ind[id]]
        elif cat == "center":
            feats[i, 29:173] = center_feats[center_ID_to_ind[id]]
        elif cat == "left":
            feats[i, 29:173] = left_feats[left_ID_to_ind[id]]
        elif cat == "right":
            feats[i, 29:173] = right_feats[right_ID_to_ind[id]]

        # feat 174 ie integer for class
        feats[i, 173] = class_lookup[cat]

    np.savez_compressed(args.output, feats)

    
if __name__ == "__main__": 

    parser = argparse.ArgumentParser(description='Process each .')
    parser.add_argument("-o", "--output", help="Directs the output to a filename of your choice", required=True)
    parser.add_argument("-i", "--input", help="The input JSON file, preprocessed as in Task 1", required=True)
    args = parser.parse_args()

    main(args)
