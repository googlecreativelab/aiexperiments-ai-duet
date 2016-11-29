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

import magenta.models.basic_rnn.basic_rnn_generator as basic_rnn_generator
from magenta.music import sequence_generator_bundle
from magenta.protobuf import generator_pb2
from magenta.music import midi_io
from magenta.models.shared.melody_rnn_generate import _steps_to_seconds
import os
import tempfile


basic_generator = basic_rnn_generator.create_generator(
    None,
    sequence_generator_bundle.read_bundle_file(os.path.abspath('./magenta/basic_rnn.mag')),
    4)

def generate_midi(midi_data, total_seconds=10):
    primer_sequence = midi_io.midi_to_sequence_proto(midi_data)
    generate_request = generator_pb2.GenerateSequenceRequest()
    if len(primer_sequence.notes) > 4:
        estimated_tempo = midi_data.estimate_tempo()
        if estimated_tempo > 240:
            qpm = estimated_tempo / 2
        else:
            qpm = estimated_tempo
    else:
        qpm = 120
    primer_sequence.tempos[0].qpm = qpm
    generate_request.input_sequence.CopyFrom(primer_sequence)
    generate_section = (generate_request.generator_options.generate_sections.add())
    # Set the start time to begin on the next step after the last note ends.
    notes_by_end_time = sorted(primer_sequence.notes, key=lambda n: n.end_time)
    last_end_time = notes_by_end_time[-1].end_time if notes_by_end_time else 0
    generate_section.start_time_seconds = last_end_time + _steps_to_seconds(
            1, qpm)
    generate_section.end_time_seconds = total_seconds
    # generate_response = generator_map[generator_name].generate(generate_request)
    generate_response = basic_generator.generate(generate_request)
    output = tempfile.NamedTemporaryFile()
    midi_io.sequence_proto_to_midi_file(
          generate_response.generated_sequence, output.name)
    output.seek(0)
    return output
