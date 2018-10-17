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
r"""Train and evaluate the lookback RNN model.

Example usage:
  $ bazel build magenta/models/lookback_rnn:lookback_rnn_train

  $ ./bazel-bin/magenta/models/lookback_rnn/lookback_rnn_train \
    --run_dir=/tmp/lookback_rnn/logdir/run1 \
    --sequence_example_file=/tmp/lookback_rnn/training_melodies.tfrecord \
    --num_training_steps=20000

  $ ./bazel-bin/magenta/models/lookback_rnn/lookback_rnn_train \
    --run_dir=/tmp/lookback_rnn/logdir/run1 \
    --sequence_example_file=/tmp/lookback_rnn/eval_melodies.tfrecord \
    --num_training_steps=20000
    --eval

  $ tensorboard --logdir=/tmp/lookback_rnn/logdir

See /magenta/models/shared/melody_rnn_train.py for flag descriptions.
"""

# internal imports
import lookback_rnn_encoder_decoder
import lookback_rnn_graph
import tensorflow as tf

from magenta.models.shared import melody_rnn_train


def main(unused_argv):
  melody_encoder_decoder = lookback_rnn_encoder_decoder.MelodyEncoderDecoder()
  melody_rnn_train.run(melody_encoder_decoder, lookback_rnn_graph.build_graph)


def console_entry_point():
  tf.app.run(main)

if __name__ == '__main__':
  console_entry_point()
