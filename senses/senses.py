#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('all.csv', 'rb') as f:
    a = f.read().decode('utf-8').splitlines()

with open('2.txt', 'rb') as f:
    b = f.read().decode('utf-8').splitlines()

with open('3.txt', 'rb') as f:
    c = f.read().decode('utf-8').splitlines()

with open('4.txt', 'rb') as f:
    d = f.read().decode('utf-8').splitlines()

with open('5.txt', 'rb') as f:
    e = f.read().decode('utf-8').splitlines()

senses = []

print('Please wait a moment.')

for sense in a:
    word = sense.split(',')[0]
    if word in e:
        sense = sense + ',5'
    elif word in d:
        sense = sense + ',4'
    elif word in c:
        sense = sense + ',3'
    elif word in b:
        sense = sense + ',2'
    else:
        sense = sense + ',1'
    senses.append(sense)

with open('senses.csv', 'wb') as f:
    f = f.write('\n'.join(senses).encode('utf-8'))
