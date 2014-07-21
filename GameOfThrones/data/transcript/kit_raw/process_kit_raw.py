#!/usr/bin/env python
# encoding: utf-8

#
# The MIT License (MIT)
#
# Copyright (c) 2013-2014 CNRS (Hervé BREDIN -- http://herve.niderb.fr/)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from __future__ import unicode_literals

# this script process raw episode transcripts from KIT
# and generate (hopefully) clean text files in the following format

# ../raw/GameOfThrones.Season01.Episode01.txt
# CHARACTER1 dialogue line from CHARACTER 1
# CHARACTER2 dialogue line from CHARACTER 2

import codecs
from tvd import GameOfThrones
gameOfThrones = GameOfThrones('whatever')
episodes = gameOfThrones.episodes

for episode in episodes[:10]:

    print episode

    inputFile = '%s.trans' % str(episode)
    outputFile = '../raw/%s.txt' % str(episode)

    with codecs.open(inputFile, 'r', 'utf8') as f:
        file_content = [line.strip().split(':', 1) for line in f.readlines()]

    with codecs.open(outputFile, 'w', 'utf8') as f:

        for left, right in file_content:

            speaker = '_'.join(left.split()).upper()
            dialogue = right.strip()
            f.write('{speaker:s} {dialogue:s}\n'.format(
                speaker=speaker, dialogue=dialogue))
