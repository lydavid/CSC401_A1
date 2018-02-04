import sys
import argparse
import os
import json

#indir = '/u/cs401/A1/data/'; # TODO: remember to change it back!
indir = 'data/'; # changed to our pc's path to data directory


def preproc1( comment , steps=range(1,11)):
    ''' This function pre-processes a single comment

    Parameters:                                                                      
        comment : string, the body of a comment
        steps   : list of ints, each entry in this list corresponds to a preprocessing step  

    Returns:
        modComm : string, the modified comment 
    '''

    modComm = ''
    if 1 in steps:
        print('TODO')
    if 2 in steps:
        print('TODO')
    if 3 in steps:
        print('TODO')
    if 4 in steps:
        print('TODO')
    if 5 in steps:
        print('TODO')
    if 6 in steps:
        print('TODO')
    if 7 in steps:
        print('TODO')
    if 8 in steps:
        print('TODO')
    if 9 in steps:
        print('TODO')
    if 10 in steps:
        print('TODO')
        
    return modComm

def main( args ):

    allOutput = []
    for subdir, dirs, files in os.walk(indir):
        for file in files:
            fullFile = os.path.join(subdir, file)
            print("Processing " + fullFile)

            data = json.load(open(fullFile)) # 

            


            preprocessed = 0 # tracks number of lines processed
            looped = False # flag to indicate that we are circling around

            while preprocessed < args.max:

                # TODO: select appropriate args.max lines

                if looped:
                    ind = 0
                else:
                    ind = args.ID[0] % len(data)

                for i in range(ind, min(ind + args.max, len(data))):

                    # allows to break early in the case we are looping around
                    if preprocessed == args.max:
                        break

                    line = data[i]

                    # TODO: read those lines with something like `j = json.loads(line)`
                    decoded_line = json.loads(line)

                    # TODO: choose to retain fields from those lines that are relevant to you
                    decoded_line = {field: decoded_line[field] for field in ('subreddit', 'author', 'body', 'id')}

                    # TODO: add a field to each selected line called 'cat' with the value of 'file' (e.g., 'Alt', 'Right', ...) 
                    decoded_line['cat'] = fullFile.split('/')[-1] # it should be the part after the last /

                    # TODO: process the body field (j['body']) with preproc1(...) using default for `steps` argument
                    # TODO: replace the 'body' field with the processed text
                    decoded_line['body'] = preproc1(decoded_line['body'])

                    # TODO: append the result to 'allOutput'
                    allOutput.append(decoded_line)
                    preprocessed += 1

                looped = True

            print(len(allOutput)) # confirm that the dict is the right size

    fout = open(args.output, 'w')
    fout.write(json.dumps(allOutput))
    fout.close()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process each .')
    parser.add_argument('ID', metavar='N', type=int, nargs=1,
                        help='your student ID')
    parser.add_argument("-o", "--output", help="Directs the output to a filename of your choice", required=True)
    parser.add_argument("--max", help="The maximum number of comments to read from each file", default=10000) # add "type=int" if we get error for args.max
    args = parser.parse_args()

    if (args.max > 200272):
        print("Error: If you want to read more than 200,272 comments per file, you have to read them all.")
        sys.exit(1)
        
    main(args)
