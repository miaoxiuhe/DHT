#!/usr/bin/env python3.5
import itertools
import collections

try:
    range = xrange
except NameError:
    pass

def encode(obj):


    if isinstance(obj, bytes):
        #return '{0}:{1}'.format(len(obj), obj)
        return b'%i:%s'%(len(obj), obj)
    elif isinstance(obj, int):
        contents = b'i%ie'%(obj)
        return contents
    elif isinstance(obj, list):
        values = b''.join([encode(o) for o in obj])

        return b'l%se'% values
    elif isinstance(obj, dict):
        items = sorted(obj.items())
        values = b''.join([encode(key) + encode(value) for key, value in items])

        return b'd%se'%(values)
    else:
        raise TypeError('Unsupported type: {0}.'.format(type(obj)))
def decode(data):
    '''
    Bdecodes data into Python built-in types.
    '''

    return consume(LookaheadIterator(data))

class LookaheadIterator(collections.Iterator):
    '''
    An iterator that lets you peek at the next item.
    '''

    def __init__(self, iterator):
        self.iterator, self.next_iterator = itertools.tee(iter(iterator))

        # Be one step ahead
        self._advance()

    def _advance(self):
        self.next_item = next(self.next_iterator, None)

    def __next__(self):
        self._advance()

        return next(self.iterator)



def consume(stream):
    item = stream.next_item
    #print(item, type(item))
    if item is None:
        raise ValueError('Encoding empty data is undefined')
    elif item == b'i':
        return consume_int(stream)
    elif item == b'l':
        return consume_list(stream)
    elif item == b'd':
        return consume_dict(stream)
    elif item is not None and item.isdigit():
        return consume_str(stream)
    else:
        raise ValueError('Invalid bencode object type: ', item)

def consume_number(stream):
    result = b''

    while True:
        chunk = stream.next_item

        if not chunk.isdigit():
            return result
        elif result.startswith(b'0'):
            raise ValueError('Invalid number')

        next(stream)
        result += chunk

def consume_int(stream):
    if next(stream) != b'i':
        raise ValueError()

    negative = stream.next_item == b'-'

    if negative:
        next(stream)

    result = int(consume_number(stream))

    if negative:
        result *= -1

        if result == 0:
            raise ValueError('Negative zero is not allowed')

    if next(stream) != b'e':
        raise ValueError('Unterminated integer')

    return result

def consume_str(stream):
    length = int(consume_number(stream))

    if next(stream) != b':':
        raise ValueError('Malformed string')

    result = b''

    for i in range(length):
        try:
            result += next(stream)
        except StopIteration:
            raise ValueError('Invalid string length')

    return result

def consume_list(stream):
    if next(stream) != b'l':
        raise ValueError()

    l = []

    while stream.next_item != b'e':
        l.append(consume(stream))

    if next(stream) != b'e':
        raise ValueError('Unterminated list')

    return l

def consume_dict(stream):
    if next(stream) != b'd':
        raise ValueError()

    d = {}

    while stream.next_item != b'e':
        key = consume(stream)

        #pdb.set_trace()
        value = consume(stream)

        d[key] = value

    if next(stream) != b'e':
        raise ValueError('Unterminated dictionary')

    return d
