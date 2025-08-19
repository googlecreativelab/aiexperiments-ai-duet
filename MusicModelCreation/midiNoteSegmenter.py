'''
Thomas Matlak
CS 310 Final Project

Takes directory containing midi files as input, produces a text file containing only the midi note values for the first 10 seconds of each musical piece.

Usage:
python midiNoteSegments.py /path/to/midi/folder/ [/path/to/output/file.txt]
'''

import sys, glob
from mido import MidiFile, MidiTrack, Message
from keras.layers import LSTM, Dense, Activation, Dropout
from keras.preprocessing import sequence
from keras.models import Sequential
from keras.optimizers import RMSprop
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import mido
import csv

indir = sys.argv[1]
outfile_name = indir + "/out.txt"

if 2 < len(sys.argv):
    outfile_name = sys.argv[2]

midi_files = glob.glob(indir + "/*.mid")

transposition_intervals = {
    'Cb': -11,
    'Gb': -6,
    'Db': -1,
    'Ab': -8,
    'Eb': -3,
    'Bb': -10,
    'F': -5,
    'C': 0,
    'G': -7,
    'D': -2,
    'A': -9,
    'E': -4,
    'B': -11,
    'F#': -6,
    'C#':-1
}

with open(outfile_name, 'wb') as outfile:
    writer = csv.writer(outfile, delimiter=' ')

    for midi_file in midi_files:
        mid = MidiFile(midi_file)

        notes = []

        time = float(0)
        prev = float(0)

        key = "C"

        for msg in mid:
            if time >= 10:
                break
            ### this time is in seconds, not ticks
            time += msg.time

            if msg.type == "key_signature":
                key = msg.key

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
                        notes.append(note + transposition_intervals[key]) # this preserves the intervlas, but transposes a;; samples to C
        writer.writerow(notes)
