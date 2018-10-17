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
"""Tests for pipelines_common."""

# internal imports
import tensorflow as tf

from magenta.common import testing_lib as common_testing_lib
from magenta.music import constants
from magenta.music import melodies_lib
from magenta.music import sequences_lib
from magenta.music import testing_lib
from magenta.pipelines import pipelines_common
from magenta.protobuf import music_pb2


NOTE_OFF = constants.MELODY_NOTE_OFF
NO_EVENT = constants.MELODY_NO_EVENT


class PipelineUnitsCommonTest(tf.test.TestCase):

  def _unit_transform_test(self, unit, input_instance,
                           expected_outputs):
    outputs = unit.transform(input_instance)
    self.assertTrue(isinstance(outputs, list))
    common_testing_lib.assert_set_equality(self, expected_outputs, outputs)
    self.assertEqual(unit.input_type, type(input_instance))
    if outputs:
      self.assertEqual(unit.output_type, type(outputs[0]))

  def testQuantizer(self):
    steps_per_quarter = 4
    note_sequence = common_testing_lib.parse_test_proto(
        music_pb2.NoteSequence,
        """
        time_signatures: {
          numerator: 4
          denominator: 4}
        tempos: {
          qpm: 60}""")
    testing_lib.add_track(
        note_sequence, 0,
        [(12, 100, 0.01, 10.0), (11, 55, 0.22, 0.50), (40, 45, 2.50, 3.50),
         (55, 120, 4.0, 4.01), (52, 99, 4.75, 5.0)])
    expected_quantized_sequence = sequences_lib.QuantizedSequence()
    expected_quantized_sequence.qpm = 60.0
    expected_quantized_sequence.steps_per_quarter = steps_per_quarter
    testing_lib.add_quantized_track(
        expected_quantized_sequence, 0,
        [(12, 100, 0, 40), (11, 55, 1, 2), (40, 45, 10, 14),
         (55, 120, 16, 17), (52, 99, 19, 20)])

    unit = pipelines_common.Quantizer(steps_per_quarter)
    self._unit_transform_test(unit, note_sequence,
                              [expected_quantized_sequence])

  def testMonophonicMelodyExtractor(self):
    quantized_sequence = sequences_lib.QuantizedSequence()
    quantized_sequence.steps_per_quarter = 1
    testing_lib.add_quantized_track(
        quantized_sequence, 0,
        [(12, 100, 2, 4), (11, 1, 6, 7)])
    testing_lib.add_quantized_track(
        quantized_sequence, 1,
        [(12, 127, 2, 4), (14, 50, 6, 8)])
    expected_events = [
        [NO_EVENT, NO_EVENT, 12, NO_EVENT, NOTE_OFF, NO_EVENT, 11],
        [NO_EVENT, NO_EVENT, 12, NO_EVENT, NOTE_OFF, NO_EVENT, 14, NO_EVENT]]
    expected_melodies = []
    for events_list in expected_events:
      melody = melodies_lib.MonophonicMelody()
      melody.from_event_list(events_list, steps_per_quarter=1, steps_per_bar=4)
      expected_melodies.append(melody)
    unit = pipelines_common.MonophonicMelodyExtractor(
        min_bars=1, min_unique_pitches=1, gap_bars=1)
    self._unit_transform_test(unit, quantized_sequence, expected_melodies)

  def testRandomPartition(self):
    random_partition = pipelines_common.RandomPartition(
        str, ['a', 'b', 'c'], [0.1, 0.4])
    random_nums = [0.55, 0.05, 0.34, 0.99]
    choices = ['c', 'a', 'b', 'c']
    random_partition.rand_func = iter(random_nums).next
    self.assertEqual(random_partition.input_type, str)
    self.assertEqual(random_partition.output_type,
                     {'a': str, 'b': str, 'c': str})
    for i, s in enumerate(['hello', 'qwerty', '1234567890', 'zxcvbnm']):
      results = random_partition.transform(s)
      self.assertTrue(isinstance(results, dict))
      self.assertEqual(set(results.keys()), set(['a', 'b', 'c']))
      self.assertEqual(len(results.values()), 3)
      self.assertEqual(len([l for l in results.values() if l == []]), 2)  # pylint: disable=g-explicit-bool-comparison
      self.assertEqual(results[choices[i]], [s])


if __name__ == '__main__':
  tf.test.main()
