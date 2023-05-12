'''
Thomas Matlak Avi Vajpeyi, Avery Rapson
CS 310 Final Project

Loads the NN saved in the dir 'savedFile'. The function predictmood(input_midi_file)
takes a midi files in MIDO format and returns if it is happy or sad

Usage:
python usingMusicNN.py
'''

import tensorflow as tf
import json
from mido import MidiFile
import numpy as np
import tempfile


midiFile =  "01.mid"
saveFile = "savedModels/musicModelpy27"


pianoSize = 128

print("Bad ass Neural Net being loaded...")


hm_data = 2000000


n_nodes_hl1 = 1000
n_nodes_hl2 = 1000
n_nodes_hl3 = 1000

n_classes = 2
batch_size = 10
hm_epochs = 9


x = tf.placeholder('float')
y = tf.placeholder('float')


current_epoch = tf.Variable(1)

hidden_1_layer = {'f_fum':n_nodes_hl1,
                  'weight':tf.Variable(tf.random_normal([pianoSize, n_nodes_hl1])),
                  'bias':tf.Variable(tf.random_normal([n_nodes_hl1]))}

hidden_2_layer = {'f_fum':n_nodes_hl2,
                  'weight':tf.Variable(tf.random_normal([n_nodes_hl1, n_nodes_hl2])),
                  'bias':tf.Variable(tf.random_normal([n_nodes_hl2]))}

hidden_3_layer = {'f_fum':n_nodes_hl3,
                  'weight':tf.Variable(tf.random_normal([n_nodes_hl2, n_nodes_hl3])),
                  'bias':tf.Variable(tf.random_normal([n_nodes_hl3]))}

output_layer = {'f_fum':None,
                'weight':tf.Variable(tf.random_normal([n_nodes_hl3, n_classes])),
                'bias':tf.Variable(tf.random_normal([n_classes])),}



def neural_network_model(data):
    ####INPUT LAYER (HIDDEN LAYER 1)
    l1 = tf.add(tf.matmul(data,hidden_1_layer['weight']), hidden_1_layer['bias'])
    l1 = tf.nn.relu(l1)
    ####HIDDEN LAYER 2
    l2 = tf.add(tf.matmul(l1,hidden_2_layer['weight']), hidden_2_layer['bias'])
    l2 = tf.nn.relu(l2)
    ####HIDDEN LAYER 3
    l3 = tf.add(tf.matmul(l2,hidden_3_layer['weight']), hidden_3_layer['bias'])
    l3 = tf.nn.relu(l3)
    ####OUTPUT LAYER
    output = tf.matmul(l3,output_layer['weight']) + output_layer['bias']
    return output






#
def predictmood(input_midi_file):
    prediction = neural_network_model(x)
    # with open('musicModel.pickle','rb') as f:
    #     lexicon = pickle.load(f)
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        saver = tf.train.import_meta_graph(saveFile+'.meta')
        saver.restore(sess, saveFile)
        #### CONVERT THE MIDI TO NOTES AND FEATURES (without [0,1])
        #### need it in the [0 112 1 1 0 0 0 ....] format
        mid = input_midi_file
        notes = []
        time = float(0)
        prev = float(0)
        for msg in mid:
            if time >= 10:
                break
            ### this time is in seconds, not ticks
            time += msg.time
            if not msg.is_meta:
                ### only interested in piano channel
                if msg.channel == 0:
                    if msg.type == 'note_on':
                        # note in vector form to train on
                        note = msg.bytes()
                        # only interested in the note #and velocity. note message is in the form of [type, note, velocity]
                        note = note[1] #:3]
                        # note.append(time - prev)
                        prev = time
                        notes.append(note)
        noteCount = np.zeros(pianoSize)
        for note in notes:
            noteCount[note] += 1
        noteCount = list(noteCount)
        #features = np.array(list(features))
        # pos: [1,0] , argmax: 0
        # neg: [0,1] , argmax: 1
        result = (sess.run(tf.argmax(prediction.eval(feed_dict={x:[noteCount]}),1)))
        if result[0] == 0:
            return ("Sad")
        elif result[0] == 1:
            return ("Happy")
        # with open('mood.txt', 'w') as outfile:
        #     mood_dict = dict()
        #     if result[0] == 0:
        #         mood_dict = {'Mood': "Happy"}
        #     elif result[0] == 1:
        #         mood_dict = {'Mood': "Sad"}
        #     json.dump(mood_dict, outfile)
#    output.seek(0) #resets the pointer to the data of the file to the start
#    return output
