#!/usr/bin/python3

import os
import logging

class ProtobufReader:
    def __init__(self, obf):
        ProtobufReader.init()
        self.obf = obf
        self.pos = 0
        self.size = 0
        self.wiretype = 2
        self.fieldno = 0
        self.value = None

    def read_children(self, num):
        pos = self.pos
        self.obf.seek(0, os.SEEK_END)
        eof = self.obf.tell()
        logging.debug('read_children start, pos=%s eof=%s', pos, eof)
        while True:
            if pos >= eof or num <= 0:
                return
            child = self.read_child(pos)
            if child == None:
                return
            pos = pos + child.size
            num = num - 1
            yield child

    def read_child(self, at):
        logging.debug('read_child start, at=%s', at)
        child = ProtobufReader(self.obf)
        child.pos = at
        child.obf.seek(child.pos)
        desc, child.size = self.read_varint()
        logging.debug('read_child desc read, desc=%s, size=%s, wiretype=%s, field=%s', desc, child.size, desc & 0x7, desc >> 3)
        child.wiretype = desc & 0x7
        child.fieldno = desc >> 3
        reader = ProtobufReader.select_reader(child.wiretype)
        if reader == None:
            return None
        child.value, size = reader(self)
        child.size = child.size + size
        return child

    def read_varint(self):
        size = 0
        value = 0
        while True:
            chunk = self.obf.read(1)[0]
            value = ( ( chunk & 0x7F ) << ( size * 7) ) | value
            size = size + 1
            if (chunk & 0x80) == 0:
                return (value, size)

    def read_fixed64(self):
        return ( int.from_bytes( self.obf.read(8), 'little'), 8)

    def read_fixed32(self):
        return ( int.from_bytes( self.obf.read(4), 'little'), 4)

    def read_sequence(self):
        amount, size = self.read_varint()
        value = self.obf.read( min(amount, 0x20) )
        return (value, size + amount)

    @classmethod
    def select_reader(cls, wiretype):
        if wiretype in ProtobufReader.readers:
            return ProtobufReader.readers[wiretype]
        return None

    @classmethod
    def init(cls):
        if not hasattr(cls, 'readers'):
            cls.readers = { 0:cls.read_varint, 1:cls.read_fixed64, 2:cls.read_sequence, 5:cls.read_fixed32, 6:cls.read_fixed32 }
            logging.basicConfig(filename='pbread.log', filemode='w', level=logging.DEBUG)

def main(fname):
    with open(fname, 'rb') as obf:
        reader = ProtobufReader(obf)
        for c in reader.read_children(3):
            print("{0} at {1} of {2} = {3}".format(c.fieldno, c.pos, c.wiretype, c.value) )

main('/mnt/mobihome/maps/Russia_central-federal-district_asia_2.obf')