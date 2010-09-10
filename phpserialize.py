#
#  phpserialize.py
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


import cStringIO
import types


class PhpObject:
  def __init__(self, className, attributes):
    self.className = className
    self.attributes = attributes

  def __repr__(self):
    return str({
      'className': self.className,
      'attributes': self.attributes
    })

  def __eq__(self, other):
    return (self.className == other.className and
            self.attributes == other.attributes)


# Serialize.

def serialize(obj):
  output = cStringIO.StringIO()
  __serialize(obj, output)
  result = output.getvalue()
  output.close()
  return result

def __writeDict(obj, output):
  output.write("%i:{" % len(obj))
  for key in sorted(obj.keys()):
    __serialize(key, output)
    __serialize(obj[key], output)
  output.write("}")

def __serialize(obj, output):
  objType = type(obj)

  if objType is types.NoneType:
    output.write("N;")

  elif objType is types.BooleanType:
    output.write("b:%i;" % (obj == 1))

  elif objType in (types.LongType, types.FloatType):
    output.write("d:%s;" % obj)

  elif objType is types.IntType:
    output.write("i:%s;" % obj)

  elif objType is types.StringType:
    output.write("s:%i:\"%s\";" % (len(obj), obj))

  elif objType is types.DictType:
    output.write("a:")
    __writeDict(obj, output)

  elif  objType is types.ListType or objType is types.TupleType:
    output.write("a:%i:{" % len(obj))
    for i in xrange(len(obj)):
      __serialize(i, output)
      __serialize(obj[i], output)
    output.write('}')

  elif isinstance(obj, PhpObject):
    output.write("O:%i:\"%s\":" % (len(obj.className), obj.className))
    __writeDict(obj.attributes, output)

  else:
    raise TypeError("Unsupported type: " + str(objType))


# Unserialize.


def unserialize(str):
  value, index = __unserialize(str, 0)
  assert(index == len(str))
  return value


def __getLength(str, index):
  endIndex = str.find(":", index)
  return int(str[index:endIndex]), endIndex + 2


def __getString(str, index):
  # TODO: Support UTF-8.  
  length, index = __getLength(str, index)
  return str[index:index + length], index + length + 2


def __getDict(str, index):
  result = {}
  isList = True
  length, index = __getLength(str, index)
  for i in xrange(length):
    key, index = __unserialize(str, index)
    value, index = __unserialize(str, index)
    result[key] = value
    isList = isList and type(key) == type(1) and key >= 0
  return result, index + 1, isList


def __unserialize(str, index):
  type = str[index]

  if type == "N":
    # Null.
    return None, index + 2

  if type == "b":
    # Boolean.    
    return str[index + 2] == "1", index + 4

  if type == "d":
    # Float.
    endIndex = str.find(";", index)
    return float(str[index + 2:endIndex]), endIndex + 1    

  if type == "i":
    # Integer.
    endIndex = str.find(";", index)
    return int(str[index + 2:endIndex]), endIndex + 1

  if type == "s":
    # String.
    return __getString(str, index + 2)

  if type == "a":
    # Array / dictionary.
    result, index, isList = __getDict(str, index + 2)

    if isList:
      resultList = []
      for key in result:
        pos = len(resultList)
        while key > pos:
          resultList.append(None)
          pos = pos + 1
        resultList.append(result[key])
      return resultList, index

    return result, index

  if type == "O":
    # Object.
    className, index = __getString(str, index + 2)
    attributes, index, _ = __getDict(str, index)
    return PhpObject(className, attributes), index

  # If we get this far we failed.
  raise ValueError("Unsupported value: " + v[self.__c])
