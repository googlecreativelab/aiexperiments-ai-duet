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
"""Tests for pipeline."""

import os
import tempfile

# internal imports
import tensorflow as tf

from magenta.common import testing_lib
from magenta.pipelines import pipeline
from magenta.pipelines import statistics


MockStringProto = testing_lib.MockStringProto  # pylint: disable=invalid-name


class MockPipeline(pipeline.Pipeline):

  def __init__(self):
    super(MockPipeline, self).__init__(
        input_type=str,
        output_type={'dataset_1': MockStringProto,
                     'dataset_2': MockStringProto})

  def transform(self, input_object):
    return {
        'dataset_1': [
            MockStringProto(input_object + '_A'),
            MockStringProto(input_object + '_B')],
        'dataset_2': [MockStringProto(input_object + '_C')]}


class PipelineTest(tf.test.TestCase):

  def testFileIteratorRecursive(self):
    target_files = [
        ('0.ext', 'hello world'),
        ('a/1.ext', '123456'),
        ('a/2.ext', 'abcd'),
        ('b/c/3.ext', '9999'),
        ('b/z/3.ext', 'qwerty'),
        ('d/4.ext', 'mary had a little lamb'),
        ('d/e/5.ext', 'zzzzzzzz'),
        ('d/e/f/g/6.ext', 'yyyyyyyyyyy')]
    extra_files = [
        ('stuff.txt', 'some stuff'),
        ('a/q/r/file', 'more stuff')]

    root_dir = tempfile.mkdtemp(dir=self.get_temp_dir())
    for path, contents in target_files + extra_files:
      abs_path = os.path.join(root_dir, path)
      tf.gfile.MakeDirs(os.path.dirname(abs_path))
      tf.gfile.FastGFile(abs_path, mode='w').write(contents)

    file_iterator = pipeline.file_iterator(root_dir, 'ext', recurse=True)

    self.assertEqual(set([contents for _, contents in target_files]),
                     set(file_iterator))

  def testFileIteratorNotRecursive(self):
    target_files = [
        ('0.ext', 'hello world'),
        ('1.ext', 'hi')]
    extra_files = [
        ('a/1.ext', '123456'),
        ('a/2.ext', 'abcd'),
        ('b/c/3.ext', '9999'),
        ('d/e/5.ext', 'zzzzzzzz'),
        ('d/e/f/g/6.ext', 'yyyyyyyyyyy'),
        ('stuff.txt', 'some stuff'),
        ('a/q/r/file', 'more stuff')]

    root_dir = tempfile.mkdtemp(dir=self.get_temp_dir())
    for path, contents in target_files + extra_files:
      abs_path = os.path.join(root_dir, path)
      tf.gfile.MakeDirs(os.path.dirname(abs_path))
      tf.gfile.FastGFile(abs_path, mode='w').write(contents)

    file_iterator = pipeline.file_iterator(root_dir, 'ext', recurse=False)

    self.assertEqual(set([contents for _, contents in target_files]),
                     set(file_iterator))

  def testTFRecordIterator(self):
    tfrecord_file = os.path.join(
        tf.resource_loader.get_data_files_path(),
        '../testdata/tfrecord_iterator_test.tfrecord')
    self.assertEqual(
        [MockStringProto(string)
         for string in ['hello world', '12345', 'success']],
        list(pipeline.tf_record_iterator(tfrecord_file, MockStringProto)))

  def testRunPipelineSerial(self):
    strings = ['abcdefg', 'helloworld!', 'qwerty']
    root_dir = tempfile.mkdtemp(dir=self.get_temp_dir())
    pipeline.run_pipeline_serial(
        MockPipeline(), iter(strings), root_dir)

    dataset_1_dir = os.path.join(root_dir, 'dataset_1.tfrecord')
    dataset_2_dir = os.path.join(root_dir, 'dataset_2.tfrecord')
    self.assertTrue(tf.gfile.Exists(dataset_1_dir))
    self.assertTrue(tf.gfile.Exists(dataset_2_dir))

    dataset_1_reader = tf.python_io.tf_record_iterator(dataset_1_dir)
    self.assertEqual(
        set(['serialized:%s_A' % s for s in strings] +
            ['serialized:%s_B' % s for s in strings]),
        set(dataset_1_reader))

    dataset_2_reader = tf.python_io.tf_record_iterator(dataset_2_dir)
    self.assertEqual(
        set(['serialized:%s_C' % s for s in strings]),
        set(dataset_2_reader))

  def testPipelineIterator(self):
    strings = ['abcdefg', 'helloworld!', 'qwerty']
    result = pipeline.load_pipeline(MockPipeline(), iter(strings))

    self.assertEqual(
        set([MockStringProto(s + '_A') for s in strings] +
            [MockStringProto(s + '_B') for s in strings]),
        set(result['dataset_1']))
    self.assertEqual(
        set([MockStringProto(s + '_C') for s in strings]),
        set(result['dataset_2']))

  def testPipelineKey(self):
    # This happens if Key() is used on a pipeline with out a dictionary output,
    # or the key is not in the output_type dict.
    pipeline_inst = MockPipeline()
    pipeline_key = pipeline_inst['dataset_1']
    self.assertTrue(isinstance(pipeline_key, pipeline.Key))
    self.assertEqual(pipeline_key.key, 'dataset_1')
    self.assertEqual(pipeline_key.unit, pipeline_inst)
    self.assertEqual(pipeline_key.output_type, MockStringProto)
    with self.assertRaises(KeyError):
      _ = pipeline_inst['abc']

    class TestPipeline(pipeline.Pipeline):

      def __init__(self):
        super(TestPipeline, self).__init__(str, str)

      def transform(self, input_object):
        pass

    pipeline_inst = TestPipeline()
    with self.assertRaises(KeyError):
      _ = pipeline_inst['abc']

    with self.assertRaises(ValueError):
      _ = pipeline.Key(1234, 'abc')

  def testInvalidTypeSignatureException(self):

    class PipelineShell(pipeline.Pipeline):

      def __init__(self, input_type, output_type):
        super(PipelineShell, self).__init__(input_type, output_type)

      def transform(self, input_object):
        pass

    _ = PipelineShell(str, str)
    _ = PipelineShell({'name': str}, {'name': str})

    good_type = str
    for bad_type in [123, {1: str}, {'name': 123},
                     {'name': str, 'name2': 123}, [str, int]]:
      with self.assertRaises(pipeline.InvalidTypeSignatureException):
        PipelineShell(bad_type, good_type)
      with self.assertRaises(pipeline.InvalidTypeSignatureException):
        PipelineShell(good_type, bad_type)

  def testPipelineGivenName(self):

    class TestPipeline123(pipeline.Pipeline):

      def __init__(self):
        super(TestPipeline123, self).__init__(str, str, 'TestName')
        self.stats = []

      def transform(self, input_object):
        self._set_stats([statistics.Counter('counter_1', 5),
                         statistics.Counter('counter_2', 10)])
        return []

    pipe = TestPipeline123()
    self.assertEqual(pipe.name, 'TestName')
    pipe.transform('hello')
    stats = pipe.get_stats()
    self.assertEqual(
        set([(stat.name, stat.count) for stat in stats]),
        set([('TestName_counter_1', 5), ('TestName_counter_2', 10)]))

  def testPipelineDefaultName(self):

    class TestPipeline123(pipeline.Pipeline):

      def __init__(self):
        super(TestPipeline123, self).__init__(str, str)
        self.stats = []

      def transform(self, input_object):
        self._set_stats([statistics.Counter('counter_1', 5),
                         statistics.Counter('counter_2', 10)])
        return []

    pipe = TestPipeline123()
    self.assertEqual(pipe.name, 'TestPipeline123')
    pipe.transform('hello')
    stats = pipe.get_stats()
    self.assertEqual(
        set([(stat.name, stat.count) for stat in stats]),
        set([('TestPipeline123_counter_1', 5),
             ('TestPipeline123_counter_2', 10)]))

  def testInvalidStatisticsException(self):

    class TestPipeline1(pipeline.Pipeline):

      def __init__(self):
        super(TestPipeline1, self).__init__(object, object)
        self.stats = []

      def transform(self, input_object):
        self._set_stats([statistics.Counter('counter_1', 5), 12345])
        return []

    class TestPipeline2(pipeline.Pipeline):

      def __init__(self):
        super(TestPipeline2, self).__init__(object, object)
        self.stats = []

      def transform(self, input_object):
        self._set_stats(statistics.Counter('counter_1', 5))
        return [input_object]

    tp1 = TestPipeline1()
    with self.assertRaises(pipeline.InvalidStatisticsException):
      tp1.transform('hello')

    tp2 = TestPipeline2()
    with self.assertRaises(pipeline.InvalidStatisticsException):
      tp2.transform('hello')


if __name__ == '__main__':
  tf.test.main()
