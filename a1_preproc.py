import sys
import argparse
import os
import json
import html
import re
import string
import spacy

import time  # test performance

#indir = '/u/cs401/A1/data/'; # TODO: remember to change it back!
indir = 'data/'  # changed to our pc's path to data directory

abbrevs = {}
with open("abbrev.english") as file:  # change to /u/cs401/WordLists/abbrev.english OR submit this file as well
    abbrevs = set(file.read().lower().splitlines())
abbrevs.add("e.g.")

clitics = {"n't", "'m", "'ve", "'ll", "'re", "'d", "'s"}  # list of clitics we will use to look for them

nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])  # change en_core_web_sm to en before submission

stopwords = {}
with open("StopWords") as file:  # change to /u/cs401/WordLists/StopWords
    stopwords = set(file.read().lower().splitlines())

ending_punctuations = {".", "!", "?", ":", ";", "—"}
temp_bound = "<boundary>"  # used to mark temporary sentence ending boundary in step 9


def split_on_spaces(text):
    ''' Splits text on spaces, cleans up unnecessary spaces and returns the list '''
    text = text.split(" ")
    # make sure we don't have random spaces
    text = [t if not t.isspace() else "" for t in text]
    text = list(filter(None, text))

    return text

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
        comment1 = comment.strip()  # remove trailing/leading whitespaces
        modComm += comment1.replace("\n", " ").replace("\r", " ")  # remove intermediate newlines
        # -> should replace them with space or else text after them may be merged with an url and deleted in step 3

    if 2 in steps:
        modComm = html.unescape(modComm)  # convert from html code to ascii

    if 3 in steps:
        # mainly based off of: https://stackoverflow.com/questions/3809401/what-is-a-good-regular-expression-to-match-a-url
        # matches any number of non-whitespace characters after http or www
        # extended to allow for matching www on its own and to cover potentially more special characters
        # we are assuming there are no spaces in a URL
        modComm = re.sub(r"((https?:\/\/(www\.)?)|www)\S*", "", modComm)

    if 4 in steps:

        # split on whitespace, for each token, if there's a punctuation in it, split it at first punctuation
        # remerge string with space between each token
        tokens = split_on_spaces(modComm)
        #print(tokens)
        new_tokens = []  # stores new list of tokens, including the splitted punctuations

        for token in tokens:

            if token.lower() in abbrevs:  # since e.g. not in the given list
                new_tokens.append(token)

            else:

                # to handle cases like Mr.Bean -> Mr. Bean, we can try to find all occurrences of abbrev and
                # add a space between them if they are attached to something else
                # looking at the abbrev file and e.g. we shouldn't run into a scenario where this goes against us (like misidentifying a token as abbrev)
                # for abbrev in abbrevs:
                f2 = False  # flag to indicate where token is abbrev
                for abbrev in abbrevs:
                    ind = token.lower().find(abbrev)
                    if ind != -1:
                        token = token[:ind + len(abbrev)] + " " + token[ind + len(abbrev):]
                        new_tokens.append(token)
                        f2 = True
                        break
                if not f2:

                    flag = False  # used to determine that we have encountered a punctuation and splitted accordingly
                    for char in token:

                        if char in string.punctuation and char != "'":
                            splitted_tokens = token.split(char, 1)

                            # if second element in list is a punct as well, then we can add this punct in front of them (group a series of punct)
                            # note that our code will not account for erroneous punctuation like (Hello ,,how are you) -> (Hello, ,,how are you)
                            # ie we assume punctuations do not precede another token
                            if splitted_tokens[1] and splitted_tokens[1][0] in string.punctuation:
                                splitted_tokens[1] = char + splitted_tokens[1]
                            else:
                                splitted_tokens.insert(1, char)
                            splitted_tokens = filter(None, splitted_tokens) # remove any empty string
                            new_tokens.extend(splitted_tokens)
                            flag = True
                            break

                    # if we did not find a punctuation in token, make sure to add the token to our list
                    if not flag:
                        new_tokens.append(token)

        # build up our new mod comment
        modComm = " ".join(new_tokens)
        #print("4.2: " + modComm)

    if 5 in steps:

        # for each clitic, find all occurrences of it in the comment, and add a space to split it from its token
        for clitic in clitics:
            occurrences = modComm.count(clitic)
            start = 0
            while occurrences > 0:
                ind = modComm.find(clitic, start)
                modComm = modComm[:ind] + " " + modComm[ind:]
                start = ind + len(clitic)  # we makre sure we're not finding the same clitic over and over
                occurrences -= 1

        # now deal with possessive ' like dogs', cause we don't want to add ' to our clitics list
        # else it will mess things up above
        tokens = modComm.split(" ")
        for i in range(len(tokens)):
            if tokens[i] and tokens[i][-1] == "'":
                tokens[i] = tokens[i][:-1] + " " + tokens[i][-1:]

        # build up our new mod comment
        modComm = " ".join(new_tokens)


    if 6 in steps:

        doc = nlp(modComm)
        new_tokens = []
        for token in doc:
            new_tokens.append("%s/%s" % (token, token.tag_))

        # build up our new mod comment
        modComm = " ".join(new_tokens)
        #print("6: " + modComm)

    if 7 in steps:

        # if one of our tokens is a stop word according to our list above, remove it along with its tag
        tokens = split_on_spaces(modComm)
        new_tokens = []
        for token in tokens:
            # get the token part of token, ie the part before the /TAG
            slash_ind = token.rfind("/")
            token_only = token[:slash_ind]
            if token_only not in stopwords:
                new_tokens.append(token)

        # build up our new mod comment
        modComm = " ".join(new_tokens)

    if 8 in steps:

        #print("8.1: " + modComm)

        tokens = split_on_spaces(modComm)
        new_tokens = []
        for token in tokens:
            slash_ind = token.find("/", 1)
            token_only = token[:slash_ind]
            tag_only = token[slash_ind:]
            doc = nlp(token_only)
            for t in doc:
                if t.lemma_[0] == "-" and token[0] != "-":
                    new_tokens.append(token)
                else:
                    new_tokens.append("%s%s" % (t.lemma_, tag_only))

        # build up our new mod comment
        modComm = " ".join(new_tokens)
        #print("8.2: " + modComm)

    if 9 in steps:

        #print("9.1: " + modComm)
        # use a symbol to indicate temp sentence boundary: <boundary>
        # insert this after all .?!;:—

        tokens = split_on_spaces(modComm)

        new_tokens = []
        for i in range(len(tokens)):
            if tokens[i] and tokens[i][-1] == "'":  # spacy seems to use this particular quotation as the ending quotation tag
                # if there was a preceding <boundary>, insert this token before it
                if i > 0 and new_tokens[-1] == temp_bound:
                    new_tokens.insert(-1, tokens[i])
                else:
                    new_tokens.append(tokens[i])
            else:
                new_tokens.append(tokens[i])
                if tokens[i][0] in ending_punctuations:
                    new_tokens.append(temp_bound)

        # remove the boundary if it is preceded by abbrev commonly followed by capitalized proper name
        # or preceded by abbrev and not followed by uppercase word

        # Disqualify a boundary with a ? or ! if:
        #    – It is followed by a lowercase letter (or a known name).

        # Regard other putative sentence boundaries as sentence boundaries.
        for i in range(len(new_tokens)):
            if new_tokens[i] == temp_bound:
                new_tokens[i] = "\n"

        # build up our new mod comment
        modComm = " ".join(new_tokens)
        #print("9.2: " +  modComm)

    if 10 in steps:
        # convert to lowercase
        modComm = modComm.lower()


    return modComm

def main( args ):

    allOutput = []
    for subdir, dirs, files in os.walk(indir):
        for file in files:
            fullFile = os.path.join(subdir, file)
            print("Processing " + fullFile, flush=True)

            data = json.load(open(fullFile))

            # TODO: select appropriate args.max lines
            preprocessed = 0  # tracks number of lines processed
            looped = False  # flag to indicate that we are circling around

            while preprocessed < args.max:

                # allow for circular indexing
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
                    decoded_line = {field: decoded_line[field] for field in ('body', 'id')}

                    # TODO: add a field to each selected line called 'cat' with the value of 'file' (e.g., 'Alt', 'Right', ...) 
                    decoded_line['cat'] = fullFile.split('/')[-1]  # it should be the part after the last /

                    # TODO: process the body field (j['body']) with preproc1(...) using default for `steps` argument
                    # TODO: replace the 'body' field with the processed text
                    start = time.clock()

                    decoded_line['body'] = preproc1(decoded_line['body'])

                    finish = time.clock()

                    print("preproc1 time: %f" % (finish - start))

                    # TODO: append the result to 'allOutput'
                    allOutput.append(decoded_line)
                    preprocessed += 1

                looped = True

            print(len(allOutput))  # confirm that the dict is the right size, REMOVE THIS BEFORE SUBMISSION

    fout = open(args.output, 'w')
    fout.write(json.dumps(allOutput))
    fout.close()


# REMOVE THIS BEFORE SUBMISSION
def debug():
    test_bodies = [
        "&#36;Hello\n", 
        "\nWorld&gt;", 
        "In&#37 \n Between",
        "R\r",
        "NR\n\r",
        "I use https://regex101.com/ to check my regex.",
        "www.google.ca",
        "https://www.reddit.com/",
        "http://www.reddit.com/",
        "Tut: https://drive.google.com/file/d/1_1C2_yp_OtBK4jCbjsrFd4RQ-_ZfVScm/view",
        "Use www.fb.com.", # last . is not part of url
        "http://www.foxnews.com/us/2015/03/03/lapd-chief-says-homeless-man-shot-by-police-reached-for-officer-gun/ according to this story 2 of the cops involved in the shooting were wearing body cameras and the gun that was recovered which was allegedly taken from one of the officers by the homeless man was partially cocked and jammed with a round of ammo in the injection port which is indicative of a struggle over the weapon. unfortunately people won't wait to see the evidence and a lot of the people who do see the evidence will ignore it or say that it was planted/made up so this is \"just another unarmed black man killed by the police for minding his own business.\"",
        "Hello, we're here.",
        "e.g. should not be split",
        "Hi!!!",
        "Hi?!! Thinking/thonking",
        "Hello ,,how are you Hello,, how are you",
        "Mr.Bean should be Mr. Bean",
        "Miss.Carter will be on St.John St.",
        "non-whitespace",
        "This 'was' his.",
        "can't",
        "should've would've could've didn't",  # spacy seems to split should/md '/`` ve/vb
        "don't! I'll I'd I'm that's they're",
        "o'clock",
        "dogs' dog's",
        "couldn't I'm we've we'll they're I'd that's",
        "wouldn't've",
        "You should've did it.",
        "-I said.",
        "Ellipses...",
        "dogs' 'dude' \"cake\"",
        "\"Humans?\" she whispered.",
        "I walked the  dog.",
        "me my mine we us our ours",
        "you your yours u ur urs",
        "heh // ///"

    ]

    for i in range(len(test_bodies)):
        print(preproc1(test_bodies[i]) + "\n")
    print("Done")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process each .')
    parser.add_argument('ID', metavar='N', type=int, nargs=1,
                        help='your student ID')
    parser.add_argument("-o", "--output", help="Directs the output to a filename of your choice", required=True)
    parser.add_argument("--max", help="The maximum number of comments to read from each file", default=10000, type=int) # add "type=int" if we get error for args.max
    args = parser.parse_args()

    if (args.max > 200272):
        print("Error: If you want to read more than 200,272 comments per file, you have to read them all.")
        sys.exit(1)
        
    #debug()  # REMOVE THIS BEFORE SUBMISSION
    main(args)
