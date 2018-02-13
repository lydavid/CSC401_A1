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

    # since we aren't allowed to modify the parameters of these functions, we will repeat sections of the code here
    if iBest == 1:
        clf = LinearSVC()  # 1. SVC linear kernel
    elif iBest == 2:
        clf = SVC(gamma=2, max_iter=10000)  # 2. SVC radial basis function kernel
    elif iBest == 3:
        clf = RandomForestClassifier(max_depth=5, n_estimators=10)  # 3. RandomForestClassifier
    elif iBest == 4:
        clf = MLPClassifier(alpha=0.05)  # 4. MLPClassifier
    else:
        clf = AdaBoostClassifier()  # 5. AdaBoostClassifier

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
    print('TODO Section 3.3')


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

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process each .')
    parser.add_argument("-i", "--input", help="the input npz file from Task 2", required=True)
    args = parser.parse_args()

    # TODO : complete each classification experiment, in sequence.
    main(args)
