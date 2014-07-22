#!/usr/bin/env python
# encoding: utf-8

#
# The MIT License (MIT)
#
# Copyright (c) 2013-2014 CNRS
# - Camille GUINAUDEAU
# - Hervé BREDIN (http://herve.niderb.fr/)
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

import re
from pkg_resources import resource_filename
from bs4 import BeautifulSoup

from tvd import Plugin
from tvd import T, TStart, TEnd, Transcription
from tvd import Segment, Annotation
from pyannote.parser.ctm import CTMParser, IterLinesMixin


class GameOfThrones(Plugin, IterLinesMixin):

    def outline_www(self, url=None, episode=None, **kwargs):
        """
        Parameters
        ----------
        url : str, optional
            URL where resource is available
        episode : Episode, optional
            Episode for which resource should be downloaded
            Useful in case a same URL contains resources for multiple episodes.

        Returns
        -------
        G : Transcription
        """

        r = self.download_as_utf8(url)
        soup = BeautifulSoup(r)
        h2 = soup.find_all('h2')
        sp = ""
        i = 0
        outline = {}

        for element in h2[0].next_elements:
            if element.name == 'p':
                if outline.get(i) == "----":
                    sp = element.text
                else:
                    sp = outline.get(i) + " " + element.text
                outline.update({i: sp})
            if element.name == 'h2':
                i = i + 1
                sp = "----"
                outline.update({i: sp})

        G = Transcription(episode=episode)
        t2 = TStart

        i = 1
        while outline.get(i):
            # add /empty/ edge between previous and next annotations
            t1 = t2
            t2 = T()
            G.add_edge(t1, t2)

            # add next annotation
            t1 = t2
            t2 = T()
            G.add_edge(t1, t2, scene=outline.get(i))

            i = i + 1

        # add /empty/ edge between previous annotation and episode end
        t1 = t2
        t2 = TEnd
        G.add_edge(t1, t2)

        return G

    def _scenes(self, url=None, episode=None):
        """Load file at `url` as Annotation

        File must follow the following format:

        # start_time end_time label
        0.000 10.234 beginning
        10.234 56.000 scene_1
        """

        # initialize empty annotation
        # uri is set to episode when provided
        annotation = Annotation(uri=episode)

        # absolute path to resource file
        path = resource_filename(self.__class__.__name__, url)

        # open file and parse it
        with open(path, 'r') as f:
            for line in f:
                start, end, label = line.strip().split()
                start = float(start)
                end = float(end)
                annotation[Segment(start, end)] = label

        return annotation

    def scenes_outline(self, url=None, episode=None, **kwargs):
        return self._scenes(url=url, episode=episode)

    def scenes(self, url=None, episode=None, **kwargs):
        return self._scenes(url=url, episode=episode)

    # load name mapping
    def _get_mapping(self):
        path = resource_filename(self.__class__.__name__, 'data/mapping.txt')
        with open(path, 'r') as _:
            mapping = dict(line.split() for line in _.readlines())
        return mapping

    def transcript_www(self, url=None, episode=None, **kwargs):

        # load name mapping
        mapping = self._get_mapping()

        r = self.download_as_utf8(url)

        soup = BeautifulSoup(r)

        G = Transcription(episode=episode)
        t2 = TStart

        div = soup.find_all('div')
        transcript = ""

        for i in range(0, len(div)):
            if re.match("{'class': \['postbody'\]}", unicode(div[i].attrs)):
                transcript = div[i]

        for i in range(0, len(transcript.contents)):
            string = unicode(transcript.contents[i])
            if not re.match("\[(.*)\]", string):
                if re.match("(.*) : (.*)", string) and \
                   not re.match("(.*) by : (.*)", string):
                    ligne = re.split(' : ', transcript.contents[i])

                    # add /empty/ edge between previous and next annotations
                    t1 = t2
                    t2 = T()
                    G.add_edge(t1, t2)

                    # add next annotation
                    t1 = t2
                    t2 = T()

                    spk = ligne[0].lower().replace(' ', '_')

                    if re.match("(.*)_\(|\[(.*)\)|\]", spk):
                        match = re.match("(.*)_\(|\[(.*)\)|\]", spk)
                        spk = match.group(1)

                    spk = mapping.get(spk, spk)

                    if re.match("(.*)/(.*)", spk):
                        spks = spk.split('/')
                        if spks[0] in mapping:
                            spk = mapping.get(spks[0])
                            G.add_edge(t1, t2, speaker=spk, speech=ligne[1])
                        if spks[1] in mapping:
                            spk = mapping.get(spks[1])
                            G.add_edge(t1, t2, speaker=spk, speech=ligne[1])
                    else:
                        G.add_edge(t1, t2, speaker=spk, speech=ligne[1])

                elif (
                    re.match("(.*): (.*)", string)
                    and not re.match("Credit: (.*)", string)
                    and not re.match("(.*) by: (.*)", string)
                ):
                    ligne = re.split(': ', transcript.contents[i])

                    # add /empty/ edge between previous and next annotations
                    t1 = t2
                    t2 = T()
                    G.add_edge(t1, t2)

                    # add next annotation
                    t1 = t2
                    t2 = T()
                    spk = ligne[0].lower().replace(' ', '_')

                    if re.match("(.*)_\(|\[(.*)\)|\]", spk):
                        match = re.match("(.*)_\(|\[(.*)\)|\]", spk)
                        spk = match.group(1)
                    spk = mapping.get(spk, spk)

                    if re.match("(.*)/(.*)", spk):
                        spks = spk.split('/')
                        if spks[0] in mapping:
                            spk = mapping.get(spks[0])
                            G.add_edge(t1, t2, speaker=spk, speech=ligne[1])
                        if spks[1] in mapping:
                            spk = mapping.get(spks[1])
                            G.add_edge(t1, t2, speaker=spk, speech=ligne[1])
                    else:
                        G.add_edge(t1, t2, speaker=spk, speech=ligne[1])

        # add /empty/ edge between previous annotation and episode end
        t1 = t2
        t2 = TEnd
        G.add_edge(t1, t2)

        return G

    def transcript(self, url=None, episode=None, **kwargs):

        path = resource_filename(self.__class__.__name__, url)
        transcription = Transcription(episode=episode)

        # previous dialogue end time
        e_dialogue = None

        for line in self.iterlines(path):

            # ARYA_STARK I'm not a boy!
            # speaker = ARYA_STARK
            # speech = I'm not a boy!
            tokens = line.split()
            speaker = tokens[0].strip()
            speech = ' '.join(tokens[1:]).strip()

            # new dialogue
            _s_dialogue, _e_dialogue = T(), T()

            # connect dialogue with previous dialogue
            if e_dialogue is not None:
                transcription.add_edge(e_dialogue, _s_dialogue)

            transcription.add_edge(_s_dialogue, _e_dialogue,
                                   speaker=speaker, speech=speech)

            # keep track of previous dialogue end time
            e_dialogue = _e_dialogue

        return transcription

    def transcript_aligned(self, url=None, episode=None, **kwargs):
        path = resource_filename(self.__class__.__name__, url)
        return CTMParser().get_transcription(path)


    # def summary(self, url=None, episode=None, **kwargs):
    #     """
    #     Parameters
    #     ----------
    #     url : str, optional
    #         URL where resource is available
    #     episode : Episode, optional
    #         Episode for which resource should be downloaded
    #         Useful in case a same URL contains resources
    #         for multiple episodes.
    #
    #     Returns
    #     -------
    #     G : Transcription
    #     """
    #
    #     r = self.download_as_utf8(url)
    #     soup = BeautifulSoup(r)
    #
    #     G = Transcription(episode=episode)
    #     t1 = TStart
    #     t2 = T()
    #     G.add_edge(t1, t2)
    #     t5 = T()
    #
    #     sp = ""
    #     scene_location = ""
    #
    #     h3 = soup.find_all('h3')
    #     summary_tag = h3[1]
    #     ok = 1
    #     end = 0
    #
    #     for element in summary_tag.next_elements:
    #         if element.name == "h4" and ok == 1:
    #             if end == 1:
    #                 t3 = T()
    #                 G.add_edge(t2, t3, location=scene_location, summary=sp)
    #                 sp = ""
    #             end = 1
    #             scene_location = element.contents[0].text
    #         if element.name == "p" and ok == 1:
    #             sp = sp + " " + element.text
    #         if element.name == "h3":
    #             if ok == 1:
    #                 t3 = T()
    #                 G.add_edge(t2, t3)
    #                 t4 = T()
    #                 G.add_edge(t3, t4, location=scene_location, summary=sp)
    #                 G.add_edge(t4, t5)
    #             ok = 0
    #
    #     # add /empty/ edge between previous annotation and episode end
    #     t6 = TEnd
    #     G.add_edge(t5, t6)
    #
    #     return G

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
