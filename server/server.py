# 
# Copyright 2016 Google Inc.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
# http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# 

from predict import generate_midi
import os
from flask import send_file, request
import pretty_midi
import sys
if sys.version_info.major <= 2:
    from cStringIO import StringIO
else:
    from io import StringIO
import time
import json
import mido
import tempfile
from usingMusicNN import predictmood
import numpy as np

from flask import Flask
app = Flask(__name__, static_url_path='', static_folder=os.path.abspath('../static'))

HappyNote = 0
SadNote = 1

def HappyTrack():
    track = mido.MidiTrack()
    track.append(mido.Message('note_on', note=HappyNote, velocity=3, time=6))
    return track

def SadTrack():
    track = mido.MidiTrack()
    track.append(mido.Message('note_on', note=SadNote, velocity=3, time=6))
    return track

@app.route('/predict', methods=['POST'])
def predict():
    now = time.time()
    values = json.loads(request.data)
    midi_data = pretty_midi.PrettyMIDI(StringIO(''.join(chr(v) for v in values)))
    duration = float(request.args.get('duration'))
    ret_midi = generate_midi(midi_data, duration)

    # Store the received midi file in a temporary file to be able to use it with mido
    mfile = tempfile.NamedTemporaryFile()
    midi_data.write(mfile)
    mfile.seek(0)

    midofile = mido.MidiFile(mfile.name)

    mood = predictmood(midofile)
    print mood
    
    # Add a new track with the first note indicating the mood
    midi_to_mod = mido.MidiFile(ret_midi.name)
    midi_to_mod.tracks.append(HappyTrack() if mood == 'happy' else SadTrack())

    ret_file = tempfile.NamedTemporaryFile()
    midi_to_mod.save(ret_file.name)
    ret_file.seek(0)

    return send_file(ret_file, attachment_filename='return.mid', 
        mimetype='audio/midi', as_attachment=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    return send_file('../static/index.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
