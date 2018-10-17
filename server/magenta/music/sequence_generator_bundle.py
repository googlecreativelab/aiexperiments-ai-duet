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
"""Utility functions for handling bundle files."""

# internal imports

import tensorflow as tf

from google.protobuf import message
from magenta.protobuf import generator_pb2


class GeneratorBundleParseException(Exception):
  """Exception thrown when a bundle file cannot be parsed."""
  pass


def read_bundle_file(bundle_file):
  # Read in bundle file.
  bundle = generator_pb2.GeneratorBundle()
  with tf.gfile.Open(bundle_file, 'rb') as f:
    try:
      bundle.ParseFromString(f.read())
    except message.DecodeError as e:
      raise GeneratorBundleParseException(e)
  return bundle
