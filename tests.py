#
#  tests.py
#  phpserialize
#
#  Copyright 2010 The phpserialize Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http:#www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS-IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import unittest

from phpserialize import serialize, unserialize, PhpObject

class TestPhpSerialize(unittest.TestCase):
  def assertUnserialize(self, obj, serialized):
    self.assertEqual(obj, unserialize(serialized))

  def assertSame(self, obj, serialized):
    self.assertUnserialize(obj, serialized)    
    self.assertEqual(serialize(obj), serialized)

  def test_null(self):
    self.assertSame(None, "N;")

  def test_boolean(self):
    self.assertSame(False, "b:0;")
    self.assertSame(True, "b:1;")

  def test_integer(self):
    self.assertSame(0, "i:0;")
    self.assertSame(4, "i:4;")
    self.assertSame(10, "i:10;")
    self.assertSame(105, "i:105;")
    self.assertSame(10512345, "i:10512345;")
    self.assertSame(-1, "i:-1;")
    self.assertSame(-125, "i:-125;")
    self.assertSame(-20123456, "i:-20123456;")

  def test_float(self):
    self.assertUnserialize(3.0, "d:3;")
    self.assertSame(3.0, "d:3.0;")
    self.assertUnserialize(35.0, "d:35.000;")
    self.assertSame(3.0002, "d:3.0002;")
    self.assertUnserialize(-1.0, "d:-1;")
    self.assertSame(-1.0, "d:-1.0;")
    self.assertSame(-1.5, "d:-1.5;")

  def test_string(self):
    self.assertSame("", 's:0:"";')
    self.assertSame("abc", 's:3:"abc";')
    self.assertSame("a:b", 's:3:"a:b";')
    self.assertSame('a"b', 's:3:"a"b";')

  def test_array(self):
    self.assertSame([], "a:0:{}")
    self.assertSame([1, 2, 3], "a:3:{i:0;i:1;i:1;i:2;i:2;i:3;}")
    self.assertSame([1, "2", 3], 'a:3:{i:0;i:1;i:1;s:1:"2";i:2;i:3;}')
    self.assertUnserialize([1, None, 3], 'a:2:{i:0;i:1;i:2;i:3;}')

  def test_dict(self):
    self.assertSame({'a': 'b', 'c': 'd'}, 'a:2:{s:1:"a";s:1:"b";s:1:"c";s:1:"d";}')

  def test_object(self):
    self.assertSame(
        PhpObject(
            'Zend_Oauth_Token_Access',
            {
              "\0*\0_params": {
                "oauth_token": "abcd",
                "oauth_token_secret": "efg"
              }
            }),
        'O:23:"Zend_Oauth_Token_Access":1:{s:10:"\0*\0_params";a:2:{s:11:"oauth_token";s:4:"abcd";s:18:"oauth_token_secret";s:3:"efg";}}')

if __name__ == '__main__':
  unittest.main()
