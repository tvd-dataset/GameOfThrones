#!/usr/bin/env python
# encoding: utf-8

# this script process clean transcript through vrbs_align

# usage
# python force_align.py GameOfThrones.Season01.Episode01
#                       /path/to/transcript/{episode}.txt
#                       /path/to/wav/{episode}.en.wav
#                       /path/to/timed_transcript/{episode}.ctm

# GameOfThrones.Season01.Episode01.txt
# CHARACTER1 dialogue line from CHARACTER 1
# CHARACTER2 dialogue line from CHARACTER 2


# it can be launched on LIMSI's cluster using pyjob:
# python -m pyjob.grid
#        /path/to/pyjob.cfg        # pyjob config file defines the list of 'episode' to process
#        /path/to/vrbs_align.py    # <-- this script
#        %episode
#        /input/path/to/transcript/{episode}.txt # <-- as output by process_wikia_raw.py
#        /input/path/to/wav/{episode}.en.wav     # <-- english wav file extracted from dvd
#        /output/path/to/ctm/{episode}.ctm       # <-- where to store resulting ctm

import os
import sys
from tempfile import mkstemp

episode = sys.argv[1]
path2txt = sys.argv[2].format(episode=episode)
path2wav = sys.argv[3].format(episode=episode)
path2ctm = sys.argv[4].format(episode=episode)

vrbs_align = "vrbs_align -l:eng -v -f {path2wav} {path2txt} > {path2xml}"
xml2ctm = "cat {path2xml} | xml2ctm > {path2ctm}"


# start by keeping only dialogue lines from txt file

# CHARACTER1 dialogue line from CHARACTER 1
# CHARACTER2 dialogue line from CHARACTER 2

# becomes

# dialogue line from CHARACTER 1
# dialogue line from CHARACTER 2

with open(path2txt, 'r') as ftxt:
    lines = ftxt.readlines()
_, path2txt = mkstemp(suffix='.txt', text=True)

with open(path2txt, 'w') as f:
    for line in lines:
        tokens = line.split()
        f.write(" ".join(tokens[1:]) + "\n")

print 'temp txt file: %s' % path2txt

# run vrbs_align
_, path2xml = mkstemp(suffix='.xml', text=True)

print 'temp xml file: %s' % path2xml

command = vrbs_align.format(path2wav=path2wav,
                            path2txt=path2txt,
                            path2xml=path2xml)

os.system(command)

# run xml2ctm
command = xml2ctm.format(path2xml=path2xml, path2ctm=path2ctm)
os.system(command)
