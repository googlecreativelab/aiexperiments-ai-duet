# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for melody_rnn_create_dataset."""

# internal imports
import tensorflow as tf

from magenta.common import testing_lib as common_testing_lib
from magenta.models.shared import melody_rnn_create_dataset
from magenta.music import melodies_lib
from magenta.music import testing_lib
from magenta.pipelines import pipelines_common
from magenta.protobuf import music_pb2


FLAGS = tf.app.flags.FLAGS


class MelodyRNNPipelineTest(tf.test.TestCase):

  def testMelodyRNNPipeline(self):
    FLAGS.eval_ratio = 0.0
    note_sequence = common_testing_lib.parse_test_proto(
        music_pb2.NoteSequence,
        """
        time_signatures: {
          numerator: 4
          denominator: 4}
        tempos: {
          qpm: 120}""")
    testing_lib.add_track(
        note_sequence, 0,
        [(12, 100, 0.00, 2.0), (11, 55, 2.1, 5.0), (40, 45, 5.1, 8.0),
         (55, 120, 8.1, 11.0), (53, 99, 11.1, 14.1)])

    quantizer = pipelines_common.Quantizer(steps_per_quarter=4)
    melody_extractor = pipelines_common.MonophonicMelodyExtractor(
        min_bars=7, min_unique_pitches=5, gap_bars=1.0,
        ignore_polyphonic_notes=False)
    one_hot_encoder = melodies_lib.OneHotEncoderDecoder(0, 127, 0)
    quantized = quantizer.transform(note_sequence)[0]
    print quantized.tracks
    melody = melody_extractor.transform(quantized)[0]
    one_hot = one_hot_encoder.squash_and_encode(melody)
    print one_hot
    expected_result = {'training_melodies': [one_hot], 'eval_melodies': []}

    pipeline_inst = melody_rnn_create_dataset.get_pipeline(one_hot_encoder)
    result = pipeline_inst.transform(note_sequence)
    self.assertEqual(expected_result, result)


if __name__ == '__main__':
  tf.test.main()
