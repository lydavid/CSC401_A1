from sklearn.model_selection import train_test_split
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_classif  # chi2
import numpy as np
import argparse
import sys
import os
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.svm import LinearSVC
import csv
import random


def accuracy(C):
    ''' Compute accuracy given Numpy array confusion matrix C. Returns a floating point value '''
    accuracy = np.trace(C) / np.sum(C)
    return accuracy


def recall(C):
    ''' Compute recall given Numpy array confusion matrix C. Returns a list of floating point values '''
    recall_list = []
    num_points = C.shape[0]
    for k in range(num_points):
        recall_list.append(C[k, k] / np.sum(C[k, :]))

    return recall_list


def precision(C):
    ''' Compute precision given Numpy array confusion matrix C. Returns a list of floating point values '''
    precision_list = []
    num_points = C.shape[0]
    for k in range(num_points):
        precision_list.append(C[k, k] / np.sum(C[:, k]))

    return precision_list


def get_classifier(ind):
    '''
    Given a classifier index, return appropriate classifier.
    :param ind: index of classifier
    :return: returns a classifier
    '''

    if ind == 1:
        clf = LinearSVC()  # 1. SVC linear kernel
    elif ind == 2:
        clf = SVC(gamma=2, max_iter=10000)  # 2. SVC radial basis function kernel
    elif ind == 3:
        clf = RandomForestClassifier(max_depth=5, n_estimators=10)  # 3. RandomForestClassifier
    elif ind == 4:
        clf = MLPClassifier(alpha=0.05)  # 4. MLPClassifier
    else:
        clf = AdaBoostClassifier()  # 5. AdaBoostClassifier

    return clf


def class31(filename):
    ''' This function performs experiment 3.1
    
    Parameters
       filename : string, the name of the npz file from Task 2

    Returns:      
       X_train: NumPy array, with the selected training features
       X_test: NumPy array, with the selected testing features
       y_train: NumPy array, with the selected training classes
       y_test: NumPy array, with the selected testing classes
       i: int, the index of the supposed best classifier
    '''

    # process the input file
    feats = np.load(filename)
    feats = feats[feats.files[0]]

    # dict used to track our data so that we can write them all at once at the end
    classifiers_to_data = {}

    # split data into 80% for training, 20% for testing
    y = feats[:, -1]
    X = np.delete(feats, -1, axis=1)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, train_size=0.8)

    iBest = 1
    best_accuracy = 0

    '''
    for i in range(1, 6):
        if i == 1:
            clf = LinearSVC()  # 1. SVC linear kernel
        elif i == 2:
            clf = SVC(gamma=2, max_iter=10000)  # 2. SVC radial basis function kernel
        elif i == 3:
            clf = RandomForestClassifier(max_depth=5, n_estimators=10)  # 3. RandomForestClassifier
        elif i == 4:
            clf = MLPClassifier(alpha=0.05)  # 4. MLPClassifier
        else:
            clf = AdaBoostClassifier()  # 5. AdaBoostClassifier

        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)
        c_matrix = confusion_matrix(y_test, y_pred)
        acc = accuracy(c_matrix)
        rec = recall(c_matrix)
        prec = precision(c_matrix)

        if acc > best_accuracy:
            iBest = i

        arr = [i, acc]
        arr.extend(rec)
        arr.extend(prec)
        for row in range(c_matrix[1,:].size):
            arr.extend(c_matrix[row,:])
        classifiers_to_data[i] = arr
        print(c_matrix, flush=True)
    
    print(classifiers_to_data, flush=True)

    # write to a1_3.1.csv
    with open("a1_3.1.csv", "w+", newline="") as file:
        csv_writer = csv.writer(file)
        for i in range(1, 6):
            data = classifiers_to_data[i]
            csv_writer.writerow(data)
    '''

    return (X_train, X_test, y_train, y_test, iBest)


def class32(X_train, X_test, y_train, y_test, iBest):
    ''' This function performs experiment 3.2
    
    Parameters:
       X_train: NumPy array, with the selected training features
       X_test: NumPy array, with the selected testing features
       y_train: NumPy array, with the selected training classes
       y_test: NumPy array, with the selected testing classes
       i: int, the index of the supposed best classifier (from task 3.1)  

    Returns:
       X_1k: numPy array, just 1K rows of X_train
       y_1k: numPy array, just 1K rows of y_train
   '''

    clf = get_classifier(iBest)

    # sample arbitrarily from X_train and y_train
    training_sizes = [1000, 5000, 10000, 15000, 20000]
    X_1k = []
    y_1k = []
    accs = []

    for training_size in training_sizes:
        start = random.randint(0, y_train.size - training_size)
        new_X_train = X_train[start:start+training_size, ]
        new_y_train = y_train[start:start+training_size, ]

        if training_size == 1000:
            X_1k = new_X_train
            y_1k = new_y_train

        '''
        clf.fit(new_X_train, new_y_train)
        y_pred = clf.predict(X_test)
        c_matrix = confusion_matrix(y_test, y_pred)
        acc = accuracy(c_matrix)
        accs.append(acc)

    # write to a1_3.2.csv
    with open("a1_3.2.csv", "w+", newline="") as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(accs)
        comment = "There does not seem to be an expected trend of accuracy increase with training sampling size " \
            "increase. This could possibly be because the features we are testing on are not enough of an " \
            "indicator as to what category a comment belongs to. So even if the training size increases, we do " \
            "not necessarily get more relevant knowledge to progress closer towards the truth."
        print(comment, file=file)
    '''

    return (X_1k, y_1k)


def class33(X_train, X_test, y_train, y_test, i, X_1k, y_1k):
    ''' This function performs experiment 3.3
    
    Parameters:
       X_train: NumPy array, with the selected training features
       X_test: NumPy array, with the selected testing features
       y_train: NumPy array, with the selected training classes
       y_test: NumPy array, with the selected testing classes
       i: int, the index of the supposed best classifier (from task 3.1)  
       X_1k: numPy array, just 1K rows of X_train (from task 3.2)
       y_1k: numPy array, just 1K rows of y_train (from task 3.2)
    '''

    k_vals = [5, 10, 20, 30, 40, 50]
    k5_32k_inds = []  # stores indices of the best 5 features for 32k set
    k5_1k_inds = []  # " " for 1k set

    k5_X_new = []
    k5_X_1k_new = []

    with open("a1_3.3.csv", "w+", newline="") as file:
        csv_writer = csv.writer(file)

        for k_val in k_vals:
            selector = SelectKBest(f_classif, k=k_val)
            X_new = selector.fit_transform(X_train, y_train)
            pp = selector.pvalues_

            inds_32k = selector.get_support(indices=True)

            associated_pp = [pp[inds_32k[0]]]
            for ind in range(1, len(inds_32k)):
                associated_pp.append(pp[inds_32k[ind]])
            associated_pp = np.array(associated_pp, dtype=float)

            csv_writer.writerow(np.append(np.array([k_val]), associated_pp))  # writes the num of feats and associated p-values

            selector1k = SelectKBest(f_classif, k=k_val)
            X_1k_new = selector1k.fit_transform(X_1k, y_1k)

            if k_val == 5:
                k5_32k_inds.extend(inds_32k.tolist())
                k5_1k_inds.extend(selector1k.get_support(indices=True).tolist())
                k5_X_new = X_new
                k5_X_1k_new = X_1k_new

        X_test_new = X_test[:,k5_32k_inds[0]]
        for i in range(1, 5):
            X_test_new = np.column_stack((X_test_new, X_test[:,k5_32k_inds[i]]))

        # Train classifier i on on best k=5 features for 32k and 1k set
        clf = get_classifier(i)
        clf.fit(k5_X_new, y_train)
        y_pred = clf.predict(X_test_new)
        c_matrix = confusion_matrix(y_test, y_pred)
        acc = accuracy(c_matrix)

        X_test_new = X_test[:, k5_1k_inds[0]]
        for i in range(1, 5):
            X_test_new = np.column_stack((X_test_new, X_test[:, k5_1k_inds[i]]))

        clf1 = get_classifier(i)
        clf1.fit(k5_X_1k_new, y_1k)
        y_pred = clf.predict(X_test_new)
        c_matrix = confusion_matrix(y_test, y_pred)
        acc1 = accuracy(c_matrix)

        csv_writer.writerow([acc, acc1])

        # Answer questions on lines 8-10
        a = "num pronouns, liwc_auxverb, liwc_feel, liwc_home and receptiviti_ambitious seems to be chosen at both" \
            "low and higher amounts of data input. num pronouns is most likely because since every pronoun was " \
            "removed via our stopwords list, so it's always 0. liwc_home may be because politics is personal to some " \
            "people. ambitious could be people pushing a political agenda."
        b = "p-values seems to be generally higher given more input data. This may be because as we receive more " \
            "data, the significance of features goes down."
        c = "num pronouns, liwc_home, receptiviti_assertive, receptiviti_dutiful, receptiviti_self_assured. " \
            "people belonging to certain classes are possibly more likely to use assertive words (right-wing?), " \
            "while others will use more dutiful words (left-wing?). certain classes are possibly more home focused " \
            "and others extremely assured in their view, possibly those in the farther ends of the spectrum."
        print(a, file=file)
        print(b, file=file)
        print(c, file=file)


def class34( filename, i ):
    ''' This function performs experiment 3.4
    
    Parameters
       filename : string, the name of the npz file from Task 2
       i: int, the index of the supposed best classifier (from task 3.1)  
        '''
    print('TODO Section 3.4')
    


def main(args):

    c32_param = class31(args.input)
    c33_param = c32_param + class32(*c32_param)
    class33(*c33_param)
    i_best = c32_param[-1]
    class34(args.input, i_best)

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process each .')
    parser.add_argument("-i", "--input", help="the input npz file from Task 2", required=True)
    args = parser.parse_args()

    # TODO : complete each classification experiment, in sequence.
    main(args)
