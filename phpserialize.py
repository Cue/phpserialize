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

"""PHP-compatible serialize and unserialize."""

import cStringIO
import types



class PhpObject:
  """Object used in place of a PHP native object."""

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
  """Serialize a Python object to a string."""
  output = cStringIO.StringIO()
  __serialize(obj, output)
  result = output.getvalue()
  output.close()
  return result


def __writeDict(obj, output):
  """Writes a dictionary to the output."""
  output.write("%i:{" % len(obj))
  for key in sorted(obj.keys()):
    __serialize(key, output)
    __serialize(obj[key], output)
  output.write("}")


def __serialize(obj, output):
  """Serializes an object to the output."""
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


def unserialize(string):
  """Unserializes a string in to a Python object."""
  value, index = __unserialize(string, 0)
  assert(index == len(string))
  return value


def __getLength(string, index):
  """Reads a length at the given string index."""
  endIndex = string.find(":", index)
  return int(string[index:endIndex]), endIndex + 2


def __getString(string, index):
  """Reads the string at the given index."""
  # TODO: Support UTF-8.
  length, index = __getLength(string, index)
  return string[index:index + length], index + length + 2


def __getDict(string, index):
  """Reads a dict at the given index."""
  result = {}
  isList = True
  length, index = __getLength(string, index)
  for _ in xrange(length):
    key, index = __unserialize(string, index)
    value, index = __unserialize(string, index)
    result[key] = value
    isList = isList and type(key) == type(1) and key >= 0
  return result, index + 1, isList


def __unserialize(string, index):
  """Unserializes the next object in the serialized string."""
  nextType = string[index]

  if nextType == "N":
    # Null.
    return None, index + 2

  if nextType == "b":
    # Boolean.
    return string[index + 2] == "1", index + 4

  if nextType == "d":
    # Float.
    endIndex = string.find(";", index)
    return float(string[index + 2:endIndex]), endIndex + 1

  if nextType == "i":
    # Integer.
    endIndex = string.find(";", index)
    return int(string[index + 2:endIndex]), endIndex + 1

  if nextType == "s":
    # String.
    return __getString(string, index + 2)

  if nextType == "a":
    # Array / dictionary.
    result, index, isList = __getDict(string, index + 2)

    if isList:
      resultList = []
      for key in result:
        pos = len(resultList)
        while key > pos:
          resultList.append(None)
          pos += 1
        resultList.append(result[key])
      return resultList, index

    return result, index

  if nextType == "O":
    # Object.
    className, index = __getString(string, index + 2)
    attributes, index, _ = __getDict(string, index)
    return PhpObject(className, attributes), index

  # If we get this far we failed.
  raise ValueError("Unsupported value type: %s" % nextType)
