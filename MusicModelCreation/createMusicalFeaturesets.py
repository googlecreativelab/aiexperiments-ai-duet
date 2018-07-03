'''
Thomas Matlak, Avi Vajpeyi, Avery Rapson
CS 310 Final Project

Given textfiles with the musical notes in int format, this creates a pickle of
the attributes and classes for all the musical data stored in the text files
(each text file is for one class).

The data is stored as frequencies of each note on a keyboard, and the class label
is stored in 'one hot' format. 10 pre cent of data present set aside as testing data.


Usage:
python createMusicalFeaturesets.py

OUTPUT: notesData.pickle
    A pickle with the attributes and classes for music data
    pickle data continas: train_attribute ,train_class, test_attribute, test_class

NOTE: Need to update the follwoing depending on usage of script
ROOT_DIR = root/directrory/where/text/reside
DataFile = ["emotion1.txt","emotion2.txt"...])
'''

from mido import MidiFile, MidiTrack, Message
import mido
import random
import pickle
from collections import Counter
import numpy as np
import os


'''
Assume we have the following as our 'LEXICON'
  unique word list : [chair, table, spoon, television]

Assume this is our current sample data:
  String: I pulled my chair up to the table

Create a training vector that holds the count of each lexicon word:
  training vector : [1, 1, 0, 0]
  (since chair table are in string, but spoon TV arnt)


Do this for all strings

'''

ROOT_DIR = "TrainingData/"
DataFile = ["NegExamples/sadSongs.txt","PosExamples/happySongs.txt"]

pianoSize = 128 # notes 0 - 127
# this also defines our lexicon

# larger dataset, more memory gets used up MemoryError
def sample_handling(sample, classification):
    featureset = []
    '''
    featureset =
    [
        [[0 1 0 0 1 0 0 ...], [1, 0]]
        [[0 1 0 0 1 1 1 ...], [0, 1]]
        ....
    ]
    so the first list is the array of matches with the lexicon
    the second is which classification the features falls into (yes or no)
    '''
    with open(sample,'r') as f:
        contents = f.readlines()
        for l in contents:
            notes = np.fromstring(l, dtype=int, sep=' ')
            noteCount = np.zeros(pianoSize)
            for note in notes:
                noteCount[note] += 1
            noteCount = list(noteCount)
            featureset.append([noteCount, classification])
    return featureset



def create_feature_sets_and_labels(DataFile,test_size = 0.1):
    features = []
    features += sample_handling(ROOT_DIR+DataFile[0],[0,1])# neg
    features += sample_handling(ROOT_DIR+DataFile[1],[1,0]) # pos
    random.shuffle(features)
    '''
        does tf.argmax([output]) == tf.argmax([expectations]) will look like:
                tf.argmax([55454, 342324]) == tf.argmax([1,0])
    '''

    features = np.array(features)
    testing_size = int(test_size*len(features))
    train_x = list(features[:,0][:-testing_size]) #[[5,8],[7,9]]  --> [:,0] does [5,7] (all of the 0 elememts) ie the labels in this case
    train_y = list(features[:,1][:-testing_size])

    test_x = list(features[:,0][-testing_size:])
    test_y = list(features[:,1][-testing_size:])


    return train_x,train_y,test_x,test_y


if __name__ == '__main__':
    train_x,train_y,test_x,test_y = create_feature_sets_and_labels(DataFile)
    with open('notesData.pickle','wb') as f:
        pickle.dump([train_x,train_y,test_x,test_y],f) # dump data as a list, into a file
        # this saves the lexicon for pos and neg words
        # every inputted value is converted to a lexicon saving this info
        # a lot of memory!
