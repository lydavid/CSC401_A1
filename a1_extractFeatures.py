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
    print('TODO')
    # TODO: your code here
    feat_row = np.zeros(173)

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
        print(feats[i])

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

