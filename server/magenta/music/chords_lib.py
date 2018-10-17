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
"""Utility functions for working with chord progressions.

Use extract_chords_for_melodies to extract chord progressions from a
QuantizedSequence object, aligned with already-extracted melodies.

Use ChordProgression.to_sequence to write a chord progression to a
NoteSequence proto, encoding the chords as text annotations.
"""

import abc

from six.moves import range  # pylint: disable=redefined-builtin

from magenta.music import chord_symbols_lib
from magenta.music import constants
from magenta.music import events_lib
from magenta.pipelines import statistics
from magenta.protobuf import music_pb2


STANDARD_PPQ = constants.STANDARD_PPQ
NOTES_PER_OCTAVE = constants.NOTES_PER_OCTAVE
NO_CHORD = constants.NO_CHORD

# Shortcut to CHORD_SYMBOL annotation type.
CHORD_SYMBOL = music_pb2.NoteSequence.TextAnnotation.CHORD_SYMBOL


class CoincidentChordsException(Exception):
  pass


class BadChordException(Exception):
  pass


class ChordEncodingException(Exception):
  pass


class ChordProgression(events_lib.SimpleEventSequence):
  """Stores a quantized stream of chord events.

  ChordProgression is an intermediate representation that all chord or lead
  sheet models can use. Chords are represented here by a chord symbol string;
  model-specific code is responsible for converting this representation to
  SequenceExample protos for TensorFlow.

  ChordProgression implements an iterable object. Simply iterate to retrieve
  the chord events.

  ChordProgression events are chord symbol strings like "Cm7", with special
  event NO_CHORD to indicate no chordal harmony. When a chord lasts for longer
  than a single step, the chord symbol event is repeated multiple times. Note
  that this is different from MonophonicMelody, where the special
  MELODY_NO_EVENT is used for subsequent steps of sustained notes; in the case
  of harmony, there's no distinction between a repeated chord and a sustained
  chord.

  Chords must be inserted in ascending order by start time.

  Attributes:
    start_step: The offset of the first step of the progression relative to the
        beginning of the source sequence.
    end_step: The offset to the beginning of the bar following the last step
       of the progression relative to the beginning of the source sequence.
    steps_per_quarter: Number of steps in in a quarter note.
    steps_per_bar: Number of steps in a bar (measure) of music.
  """

  def __init__(self):
    """Construct an empty ChordProgression."""
    super(ChordProgression, self).__init__(pad_event=NO_CHORD)

  def __deepcopy__(self, unused_memo=None):
    new_copy = type(self)()
    new_copy.from_event_list(list(self._events),
                             self.start_step,
                             self.steps_per_bar,
                             self.steps_per_quarter)
    return new_copy

  def __eq__(self, other):
    if not isinstance(other, ChordProgression):
      return False
    else:
      return super(ChordProgression, self).__eq__(other)

  def _add_chord(self, figure, start_step, end_step):
    """Adds the given chord to the `events` list.

    `start_step` is set to the given chord. Everything after `start_step` in
    `events` is deleted before the chord is added. `events`'s length will be
     changed so that the last event has index `end_step` - 1.

    Args:
      figure: Chord symbol figure. A string like "Cm9" representing the chord.
      start_step: A non-negative integer step that the chord begins on.
      end_step: An integer step that the chord ends on. The chord is considered
          to end at the onset of the end step. `end_step` must be greater than
          `start_step`.

    Raises:
      BadChordException: If `start_step` does not precede `end_step`.
    """
    if start_step >= end_step:
      raise BadChordException(
          'Start step does not precede end step: start=%d, end=%d' %
          (start_step, end_step))

    self.set_length(end_step)

    for i in range(start_step, end_step):
      self._events[i] = figure

  def from_quantized_sequence(self, quantized_sequence, start_step, end_step):
    """Populate self with the chords from the given QuantizedSequence object.

    A chord progression is extracted from the given sequence starting at time
    step `start_step` and ending at time step `end_step`.

    The number of time steps per bar is computed from the time signature in
    `quantized_sequence`.

    Args:
      quantized_sequence: A sequences_lib.QuantizedSequence instance.
      start_step: Start populating chords at this time step.
      end_step: Stop populating chords at this time step.

    Raises:
      NonIntegerStepsPerBarException: If `quantized_sequence`'s bar length
          (derived from its time signature) is not an integer number of time
          steps.
      CoincidentChordsException: If any of the chords start on the same step.
    """
    self._reset()

    steps_per_bar_float = quantized_sequence.steps_per_bar()
    if steps_per_bar_float % 1 != 0:
      raise events_lib.NonIntegerStepsPerBarException(
          'There are %f timesteps per bar. Time signature: %d/%d' %
          (steps_per_bar_float, quantized_sequence.time_signature.numerator,
           quantized_sequence.time_signature.denominator))
    self._steps_per_bar = int(steps_per_bar_float)
    self._steps_per_quarter = quantized_sequence.steps_per_quarter

    # Sort track by chord times.
    chords = sorted(quantized_sequence.chords, key=lambda chord: chord.step)

    prev_step = None
    prev_figure = NO_CHORD

    for chord in chords:
      if chord.step >= end_step:
        # No more chords within range.
        break

      elif chord.step < start_step:
        # Chord is before start of range.
        prev_step = chord.step
        prev_figure = chord.figure
        continue

      if chord.step == prev_step:
        if chord.figure == prev_figure:
          # Identical coincident chords, just skip.
          continue
        else:
          # Two different chords start at the same time step.
          self._reset()
          raise CoincidentChordsException('chords %s and %s are coincident' %
                                          (prev_figure, chord.figure))

      if chord.step > start_step:
        # Add the previous chord.
        start_index = max(prev_step, start_step) - start_step
        end_index = chord.step - start_step
        self._add_chord(prev_figure, start_index, end_index)

      prev_step = chord.step
      prev_figure = chord.figure

    if prev_step < end_step:
      # Add the last chord active before end_step.
      start_index = max(prev_step, start_step) - start_step
      end_index = end_step - start_step
      self._add_chord(prev_figure, start_index, end_index)

    self._start_step = start_step
    self._end_step = end_step

  def to_sequence(self,
                  sequence_start_time=0.0,
                  qpm=120.0):
    """Converts the ChordProgression to NoteSequence proto.

    This doesn't generate actual notes, but text annotations specifying the
    chord changes when they occur.

    Args:
      sequence_start_time: A time in seconds (float) that the first chord in
          the sequence will land on.
      qpm: Quarter notes per minute (float).

    Returns:
      A NoteSequence proto encoding the given chords as text annotations.
    """
    seconds_per_step = 60.0 / qpm / self.steps_per_quarter

    sequence = music_pb2.NoteSequence()
    sequence.tempos.add().qpm = qpm
    sequence.ticks_per_quarter = STANDARD_PPQ

    current_figure = NO_CHORD
    for step, figure in enumerate(self):
      if figure != current_figure:
        current_figure = figure
        chord = sequence.text_annotations.add()
        chord.time = step * seconds_per_step + sequence_start_time
        chord.text = figure
        chord.annotation_type = CHORD_SYMBOL

    return sequence

  def transpose(self, transpose_amount, chord_symbol_functions=
                chord_symbols_lib.ChordSymbolFunctions.get()):
    """Transpose chords in this ChordProgression.

    Args:
      transpose_amount: The number of half steps to transpose this
          ChordProgression. Positive values transpose up. Negative values
          transpose down.
      chord_symbol_functions: ChordSymbolFunctions object with which to perform
          the actual transposition of chord symbol strings.

    Raises:
      ChordSymbolException: If a chord (other than "no chord") fails to be
          interpreted by the ChordSymbolFunctions object.
    """
    for i in xrange(len(self._events)):
      if self._events[i] != NO_CHORD:
        self._events[i] = chord_symbol_functions.transpose_chord_symbol(
            self._events[i], transpose_amount % NOTES_PER_OCTAVE)


def extract_chords_for_melodies(quantized_sequence, melodies):
  """Extracts from the QuantizedSequence a chord progression for each melody.

  This function will extract the underlying chord progression (encoded as text
  annotations) from `quantized_sequence` for each monophonic melody in
  `melodies`.  Each chord progression will be the same length as its
  corresponding melody.

  Args:
    quantized_sequence: A sequences_lib.QuantizedSequence object.
    melodies: A python list of MonophonicMelody instances.

  Returns:
    A python list of ChordProgression instances, the same length as `melodies`.
        If a progression fails to be extracted for a melody, the corresponding
        list entry will be None.
  """
  chord_progressions = []
  stats = dict([('coincident_chords', statistics.Counter('coincident_chords'))])
  for melody in melodies:
    try:
      chords = ChordProgression()
      chords.from_quantized_sequence(
          quantized_sequence, melody.start_step, melody.end_step)
    except CoincidentChordsException:
      stats['coincident_chords'].increment()
      chords = None
    chord_progressions.append(chords)

  return chord_progressions, stats.values()


class ChordRenderer(object):
  """An abstract class for rendering NoteSequence chord symbols as notes."""
  __metaclass__ = abc.ABCMeta

  @abc.abstractmethod
  def render(self, sequence):
    """Renders the chord symbols of a NoteSequence.

    This function renders chord symbol annotations in a NoteSequence as actual
    notes. Notes are added to the NoteSequence object, and the chord symbols
    remain also.

    Args:
      sequence: The NoteSequence for which to render chord symbols.
    """
    pass


class BasicChordRenderer(ChordRenderer):
  """A chord renderer that holds each note for the duration of the chord."""

  def __init__(self,
               velocity=100,
               instrument=1,
               program=88,
               chord_symbol_functions=
               chord_symbols_lib.ChordSymbolFunctions.get()):
    """Initialize a BasicChordRenderer object.

    Args:
      velocity: The MIDI note velocity to use.
      instrument: The MIDI instrument to use.
      program: The MIDI program to use.
      chord_symbol_functions: ChordSymbolFunctions object with which to perform
          the actual transposition of chord symbol strings.
    """
    self._velocity = velocity
    self._instrument = instrument
    self._program = program
    self._chord_symbol_functions = chord_symbol_functions

  def _render_notes(self, sequence, pitches, start_time, end_time):
    for pitch in pitches:
      # Add a note.
      note = sequence.notes.add()
      note.start_time = start_time
      note.end_time = end_time
      note.pitch = pitch
      note.velocity = self._velocity
      note.instrument = self._instrument
      note.program = self._program

  def render(self, sequence):
    # Sort text annotations by time.
    annotations = sorted(sequence.text_annotations, key=lambda a: a.time)

    prev_time = 0.0
    prev_figure = NO_CHORD

    for annotation in annotations:
      if annotation.time >= sequence.total_time:
        break

      if annotation.annotation_type == CHORD_SYMBOL:
        if prev_figure != NO_CHORD:
          # Render the previous chord.
          pitches = self._chord_symbol_functions.chord_symbol_midi_pitches(
              prev_figure)
          self._render_notes(sequence=sequence,
                             pitches=pitches,
                             start_time=prev_time,
                             end_time=annotation.time)

        prev_time = annotation.time
        prev_figure = annotation.text

    if (prev_time < sequence.total_time and
        prev_figure != NO_CHORD):
      # Render the last chord.
      pitches = self._chord_symbol_functions.chord_symbol_midi_pitches(
          prev_figure)
      self._render_notes(sequence=sequence,
                         pitches=pitches,
                         start_time=prev_time,
                         end_time=sequence.total_time)


class SingleChordEncoderDecoder(object):
  """An abstract class for encoding and decoding individual chords.
  """
  __metaclass__ = abc.ABCMeta

  @abc.abstractproperty
  def num_classes(self):
    """The number of distinct chord encodings.

    Returns:
      An int, the range of ints that can be returned by self.encode_chord.
    """
    pass

  @abc.abstractmethod
  def encode_chord(self, figure):
    """Convert from a chord symbol string to a chord encoding integer.

    Args:
      figure: A chord symbol string representing the chord.

    Returns:
      An integer representing the encoded chord, in range [0, self.num_classes).
    """
    pass

  @abc.abstractmethod
  def decode_chord(self, index):
    """Convert from a chord encoding integer to a chord symbol string.

    Args:
      index: The encoded chord, an integer in the range [0, self.num_classes).

    Returns:
      A chord symbol string representing the decoded chord.
    """
    pass


class MajorMinorEncoderDecoder(SingleChordEncoderDecoder):
  """Encodes chords as root + major/minor, with zero index for "no chord".

  Encodes chords as follows:
    0:     "no chord"
    1-12:  chords with a major triad, where 1 is C major, 2 is C# major, etc.
    13-24: chords with a minor triad, where 13 is C minor, 14 is C# minor, etc.
  """

  # Mapping from pitch class index to name.  Eventually this should be defined
  # more globally, but right now only `decode_chord` needs it.
  _PITCH_CLASS_MAPPING = ['C', 'C#', 'D', 'E-', 'E', 'F',
                          'F#', 'G', 'A-', 'A', 'B-', 'B']

  def __init__(self, chord_symbol_functions=
               chord_symbols_lib.ChordSymbolFunctions.get()):
    """Initialize the MajorMinorEncoderDecoder object.

    Args:
      chord_symbol_functions: ChordSymbolFunctions object with which to perform
          the actual transposition of chord symbol strings.
    """
    self._chord_symbol_functions = chord_symbol_functions

  @property
  def num_classes(self):
    return 2 * NOTES_PER_OCTAVE + 1

  def encode_chord(self, figure):
    if figure == NO_CHORD:
      return 0

    root = self._chord_symbol_functions.chord_symbol_root(figure)
    quality = self._chord_symbol_functions.chord_symbol_quality(figure)

    if quality == chord_symbols_lib.CHORD_QUALITY_MAJOR:
      return root + 1
    elif quality == chord_symbols_lib.CHORD_QUALITY_MINOR:
      return root + NOTES_PER_OCTAVE + 1
    else:
      raise ChordEncodingException('chord is neither major nor minor: %s'
                                   % figure)

  def decode_chord(self, index):
    if index == 0:
      return NO_CHORD
    elif index - 1 < 12:
      # major
      return self._PITCH_CLASS_MAPPING[index - 1]
    else:
      # minor
      return self._PITCH_CLASS_MAPPING[index - NOTES_PER_OCTAVE - 1] + 'm'


class ChordsEncoderDecoder(events_lib.EventsEncoderDecoder):
  """An abstract class for translating between chords and model data.

  When building your dataset, the `encode` method takes in a chord progression
  and returns a SequenceExample of inputs and labels. These SequenceExamples
  are fed into the model during training and evaluation.

  During generation, the `get_inputs_batch` method takes in a list of the
  current chord progressions and returns an inputs batch which is fed into the
  model to predict what the next chord should be for each progression. The
  `extend_event_sequences` method takes in the list of chord progressions
  and the softmax returned by the model and extends each progression by one
  step by sampling from the softmax probabilities. This loop
  (`get_inputs_batch` -> inputs batch is fed through the model to get a
  softmax -> `extend_event_sequences`) is repeated until the generated
  chord progressions have reached the desired length.
  """
  __metaclass__ = abc.ABCMeta

  @abc.abstractmethod
  def events_to_input(self, events, position):
    """Returns the input vector for the chord event at the given position.

    Args:
      events: A ChordProgression object.
      position: An integer event position in the chord progression.

    Returns:
      An input vector, a self.input_size length list of floats.
    """
    pass

  @abc.abstractmethod
  def events_to_label(self, events, position):
    """Returns the label for the chord event at the given position.

    Args:
      events: A ChordProgression object.
      position: An integer event position in the chord progression.

    Returns:
      A label, an integer in the range [0, self.num_classes).
    """
    pass

  @abc.abstractmethod
  def class_index_to_event(self, class_index, events):
    """Returns the chord event for the given class index.

    This is the reverse process of the self.events_to_label method.

    Args:
      class_index: An integer in the range [0, self.num_classes).
      events: A ChordProgression object.

    Returns:
      An chord progression event value, the chord symbol figure string.
    """
    pass

  def transpose_and_encode(self, chords, transpose_amount):
    """Returns a SequenceExample for the given chord progression.

    Args:
      chords: A ChordProgression object.
      transpose_amount: The number of half steps to transpose the chords.

    Returns:
      A tf.train.SequenceExample containing inputs and labels.
    """
    chords.transpose(transpose_amount)
    return self._encode(chords)
