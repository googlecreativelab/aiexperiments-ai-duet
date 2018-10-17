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
"""Shared Melody RNN generation code as a SequenceGenerator interface."""

import random

# internal imports
from six.moves import range  # pylint: disable=redefined-builtin
import tensorflow as tf

from magenta.music import constants
from magenta.music import melodies_lib
from magenta.music import sequence_generator
from magenta.music import sequences_lib
from magenta.protobuf import generator_pb2


class MelodyRnnSequenceGenerator(sequence_generator.BaseSequenceGenerator):
  """Shared Melody RNN generation code as a SequenceGenerator interface."""

  def __init__(self, details, checkpoint, bundle, melody_encoder_decoder,
               build_graph, steps_per_quarter, hparams):
    """Creates a MelodyRnnSequenceGenerator.

    Args:
      details: A generator_pb2.GeneratorDetails for this generator.
      checkpoint: Where to search for the most recent model checkpoint.
      bundle: A generator_pb2.GeneratorBundle object that includes both the
          model checkpoint and metagraph.
      melody_encoder_decoder: A melodies_lib.MelodyEncoderDecoder object
          specific to your model.
      build_graph: A function that when called, returns the tf.Graph object for
          your model. The function will be passed the parameters:
          (mode, hparams_string, input_size, num_classes, sequence_example_file)
          For an example usage, see models/basic_rnn/basic_rnn_graph.py.
      steps_per_quarter: What precision to use when quantizing the melody. How
          many steps per quarter note.
      hparams: A dict of hparams.
    """
    super(MelodyRnnSequenceGenerator, self).__init__(
        details, checkpoint, bundle)
    self._melody_encoder_decoder = melody_encoder_decoder
    self._build_graph = build_graph
    self._session = None
    self._steps_per_quarter = steps_per_quarter

    # Start with some defaults
    self._hparams = {
        'temperature': 1.0,
    }
    # Update with whatever was supplied.
    self._hparams.update(hparams)
    self._hparams['dropout_keep_prob'] = 1.0
    self._hparams['batch_size'] = 1

  def _initialize_with_checkpoint(self, checkpoint_file):
    graph = self._build_graph('generate',
                              repr(self._hparams),
                              self._melody_encoder_decoder)
    with graph.as_default():
      saver = tf.train.Saver()
      self._session = tf.Session()
      tf.logging.info('Checkpoint used: %s', checkpoint_file)
      saver.restore(self._session, checkpoint_file)

  def _initialize_with_checkpoint_and_metagraph(self, checkpoint_filename,
                                                metagraph_filename):
    self._session = tf.Session()
    new_saver = tf.train.import_meta_graph(metagraph_filename)
    new_saver.restore(self._session, checkpoint_filename)

  def _write_checkpoint_with_metagraph(self, checkpoint_filename):
    with self._session.graph.as_default():
      saver = tf.train.Saver(sharded=False)
      saver.save(self._session, checkpoint_filename, meta_graph_suffix='meta',
                 write_meta_graph=True)

  def _close(self):
    self._session.close()
    self._session = None

  def _seconds_to_steps(self, seconds, qpm):
    """Converts seconds to steps.

    Uses the generator's steps_per_quarter setting and the specified qpm.

    Args:
      seconds: number of seconds.
      qpm: current qpm.

    Returns:
      Number of steps the seconds represent.
    """

    return int(seconds * (qpm / 60.0) * self._steps_per_quarter)

  def _generate(self, generate_sequence_request):
    if len(generate_sequence_request.generator_options.generate_sections) != 1:
      raise sequence_generator.SequenceGeneratorException(
          'This model supports only 1 generate_sections message, but got %s' %
          (len(generate_sequence_request.generator_options.generate_sections)))

    generate_section = (
        generate_sequence_request.generator_options.generate_sections[0])
    primer_sequence = generate_sequence_request.input_sequence

    notes_by_end_time = sorted(primer_sequence.notes, key=lambda n: n.end_time)
    last_end_time = notes_by_end_time[-1].end_time if notes_by_end_time else 0
    if last_end_time > generate_section.start_time_seconds:
      raise sequence_generator.SequenceGeneratorException(
          'Got GenerateSection request for section that is before the end of '
          'the NoteSequence. This model can only extend sequences. '
          'Requested start time: %s, Final note end time: %s' %
          (generate_section.start_time_seconds, notes_by_end_time[-1].end_time))

    # Quantize the priming sequence.
    quantized_sequence = sequences_lib.QuantizedSequence()
    quantized_sequence.from_note_sequence(
        primer_sequence, self._steps_per_quarter)
    # Setting gap_bars to infinite ensures that the entire input will be used.
    extracted_melodies, _ = melodies_lib.extract_melodies(
        quantized_sequence, min_bars=0, min_unique_pitches=1,
        gap_bars=float('inf'), ignore_polyphonic_notes=True)
    assert len(extracted_melodies) <= 1

    qpm = (primer_sequence.tempos[0].qpm if primer_sequence
           and primer_sequence.tempos
           else constants.DEFAULT_QUARTERS_PER_MINUTE)
    start_step = self._seconds_to_steps(
        generate_section.start_time_seconds, qpm)
    end_step = self._seconds_to_steps(generate_section.end_time_seconds, qpm)

    if extracted_melodies and extracted_melodies[0]:
      melody = extracted_melodies[0]
    else:
      tf.logging.warn('No melodies were extracted from the priming sequence. '
                      'Melodies will be generated from scratch.')
      melody = melodies_lib.MonophonicMelody()
      melody.from_event_list([
          random.randint(self._melody_encoder_decoder.min_note,
                         self._melody_encoder_decoder.max_note)])
      start_step += 1

    transpose_amount = melody.squash(
        self._melody_encoder_decoder.min_note,
        self._melody_encoder_decoder.max_note,
        self._melody_encoder_decoder.transpose_to_key)

    # Ensure that the melody extends up to the step we want to start generating.
    melody.set_length(start_step)

    inputs = self._session.graph.get_collection('inputs')[0]
    initial_state = self._session.graph.get_collection('initial_state')[0]
    final_state = self._session.graph.get_collection('final_state')[0]
    softmax = self._session.graph.get_collection('softmax')[0]

    final_state_ = None
    for i in range(end_step - len(melody)):
      if i == 0:
        inputs_ = self._melody_encoder_decoder.get_inputs_batch(
            [melody], full_length=True)
        initial_state_ = self._session.run(initial_state)
      else:
        inputs_ = self._melody_encoder_decoder.get_inputs_batch([melody])
        initial_state_ = final_state_

      feed_dict = {inputs: inputs_, initial_state: initial_state_}
      final_state_, softmax_ = self._session.run(
          [final_state, softmax], feed_dict)
      self._melody_encoder_decoder.extend_event_sequences([melody], softmax_)

    melody.transpose(-transpose_amount)

    generate_response = generator_pb2.GenerateSequenceResponse()
    generate_response.generated_sequence.CopyFrom(melody.to_sequence(qpm=qpm))
    return generate_response
