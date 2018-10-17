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
"""Tests for events_lib."""

import copy

# internal imports
import tensorflow as tf

from magenta.music import events_lib


class EventsLibTest(tf.test.TestCase):

  def testDeepcopy(self):
    events = events_lib.SimpleEventSequence(pad_event=0)
    events.from_event_list([0, 1, 2], start_step=0, steps_per_quarter=4,
                           steps_per_bar=8)
    events_copy = copy.deepcopy(events)
    self.assertEqual(events, events_copy)

    events.set_length(2)
    self.assertNotEqual(events, events_copy)

  def testAppendEvent(self):
    events = events_lib.SimpleEventSequence(pad_event=0)

    events.append_event(7)
    self.assertListEqual([7], list(events))
    self.assertEqual(0, events.start_step)
    self.assertEqual(1, events.end_step)

    events.append_event('cheese')
    self.assertListEqual([7, 'cheese'], list(events))
    self.assertEqual(0, events.start_step)
    self.assertEqual(2, events.end_step)

  def testSetLength(self):
    events = events_lib.SimpleEventSequence(pad_event=0)
    events.from_event_list([60], start_step=9)
    events.set_length(5)
    self.assertListEqual([60, 0, 0, 0, 0],
                         list(events))
    self.assertEquals(9, events.start_step)
    self.assertEquals(14, events.end_step)

    events = events_lib.SimpleEventSequence(pad_event=0)
    events.from_event_list([60], start_step=9)
    events.set_length(5, from_left=True)
    self.assertListEqual([0, 0, 0, 0, 60],
                         list(events))
    self.assertEquals(5, events.start_step)
    self.assertEquals(10, events.end_step)

    events = events_lib.SimpleEventSequence(pad_event=0)
    events.from_event_list([60, 0, 0, 0])
    events.set_length(3)
    self.assertListEqual([60, 0, 0], list(events))
    self.assertEquals(0, events.start_step)
    self.assertEquals(3, events.end_step)

    events = events_lib.SimpleEventSequence(pad_event=0)
    events.from_event_list([60, 0, 0, 0])
    events.set_length(3, from_left=True)
    self.assertListEqual([0, 0, 0], list(events))
    self.assertEquals(1, events.start_step)
    self.assertEquals(4, events.end_step)


if __name__ == '__main__':
  tf.test.main()
