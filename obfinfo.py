#!/usr/bin/python3

import sys
import os
import logging
from datetime import datetime, timedelta
from schemareader import Schema, SchemaReader
from pbreader import ProtobufReader
sys.path.insert(1, os.path.abspath('../geo'))
import obfdata
import geo

def unixtime(x):
    return datetime(1970,1,1)+timedelta(milliseconds=x)

def getlon(x):
    return (x * 360.0 / (1024.0 * 1<<21)) - 180.0

obschema = { 'start':'header', 'structures':[
        { 'name':'header', 'factory': obfdata.Map, 'fields':
    { 1 : { 'name':'version' }, 18:{'name':'creation', 'factory':unixtime},
    6:{ 'name':'section', 'children':{     # map_section
        2:{'name':'name', 'factory':ProtobufReader.readutf8},
        5:{'name':'maplevel', 'structure':'maplevel' } } } } },
    { 'name':'maplevel', 'fields':{
            1:{'name':'max'}, 2:{'name':'min'}, 3:{'name':'left'}, 4:{'name':'right'}, 5:{'name':'top'}, 6:{'name':'bottom'},
            7:{'name':'boxes', 'structure':'treenode' } } },
    { 'name':'treenode', 'fields': {
        1:{'name':'left', 'factory':ProtobufReader.readzigzag}, 2:{'name':'right', 'factory':ProtobufReader.readzigzag},
        3:{'name':'top', 'factory':ProtobufReader.readzigzag}, 4:{'name':'bottom', 'factory':ProtobufReader.readzigzag},
        5:{'name':'data'}, 7:{'name':'boxes', 'structure':'treenode'} }} ] }

def main2(fname):
    schema = Schema(obschema)
#    schema.addformat({ 'structures':[ { 'name':'header', 'fields': { 6:{'print':4, 'children': { 5: { 'print':0 } } } } } ] } )
    with open(fname, 'rb') as obfile:
        reader = SchemaReader(obfile, schema)
        obfmap = reader.read()
        print('Map version {0}'.format(obfmap.version))

if __name__ == '__main__':
    logging.basicConfig(filename='obinfo.log', filemode='w', level=logging.INFO)
    main2('/mnt/mobihome/maps/Russia_central-federal-district_asia_2.obf')

