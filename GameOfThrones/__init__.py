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

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


from tvd import Plugin
import re
import urllib3
from bs4 import BeautifulSoup
from tvd import TFloating, TStart, TEnd, AnnotationGraph


class GameOfThrones(Plugin):

    def outline(self, url=None, episode=None, **kwargs):
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
        G : AnnotationGraph
        """

        http = urllib3.PoolManager()
        r = http.request('GET', url)
        soup = BeautifulSoup(r.data)
        h2 = soup.find_all('h2')
        sp = ""
        i = 0
        outline = {}


        for element in h2[0].next_elements:
            if element.name == 'p':
                if outline.get(i) == "----":
                    sp = element.text
                else :
                    sp = outline.get(i) + " " + element.text
                outline.update({i:sp})
            if element.name == 'h2':
                i = i + 1
                sp = "----"
                outline.update({i:sp})


        G = AnnotationGraph(episode=episode)
        t2 = TStart()

        i = 1
        while outline.get(i):
            # add /empty/ edge between previous and next annotations
            t1 = t2
            t2 = TFloating()
            G.add_annotation(t1, t2, {})

            # add next annotation
            t1 = t2
            t2 = TFloating()
            G.add_annotation(t1, t2, {'scene': outline.get(i)})

            i = i + 1

        # add /empty/ edge between previous annotation and episode end
        t1 = t2
        t2 = TEnd()
        G.add_annotation(t1, t2, {})

        return G

    def summary(self, url=None, episode=None, **kwargs):
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
        G : AnnotationGraph
        """

        http = urllib3.PoolManager()
        r = http.request('GET', url)
        soup = BeautifulSoup(r.data)

        G = AnnotationGraph(episode=episode)
        t1 = TStart()
        t2 = TFloating()
        G.add_annotation(t1, t2, {})

        sp = ""
        scene_location = ""

        h3 = soup.find_all('h3')
        summary_tag = h3[1]
        ok = 1
        end = 0

        for element in summary_tag.next_elements:
            if element.name == "h4" and ok == 1:
                if end == 1:
                    t3 = TFloating()
                    G.add_annotation(t2, t3, {'location': scene_location, 'summary': sp})
                    sp = ""
                end = 1
                scene_location = element.contents[0].text
            if element.name == "p" and ok == 1:
                sp = sp + " " + element.text
            if element.name == "h3":
                if ok == 1:
                    t3 = TFloating()
                    G.add_annotation(t2, t3, {'location': scene_location, 'summary': sp})
                ok = 0

        # add /empty/ edge between previous annotation and episode end
        t4 = TEnd()
        G.add_annotation(t3, t4, {})

        return G

    def manual_transcript(self, url=None, episode=None, **kwargs):

        http = urllib3.PoolManager()
        r = http.request('GET', url)
        soup = BeautifulSoup(r.data)

        G = AnnotationGraph()
        t2 = TStart()

        div = soup.find_all('div')
        transcript = ""

        for i in range(0,len(div)):
            if re.match("{'class': \['postbody'\]}", unicode(div[i].attrs)):
                transcript = div[i]

        transcription = 0
        for i in range(0,len(transcript.contents)):
            string = unicode(transcript.contents[i])
            if re.match("(.*) : (.*)", string):
                ligne = re.split(' : ', transcript.contents[i])

                # add /empty/ edge between previous and next annotations
                t1 = t2
                t2 = TFloating()
                G.add_annotation(t1, t2, {})

                # add next annotation
                t1 = t2
                t2 = TFloating()
                G.add_annotation(t1, t2, {'speaker': ligne[0], 'speech': ligne[1]})

            elif re.match("(.*): (.*)", string) and not re.match("Credit: (.*)", string):
                ligne = re.split(': ', transcript.contents[i])

                # add /empty/ edge between previous and next annotations
                t1 = t2
                t2 = TFloating()
                G.add_annotation(t1, t2, {})

                # add next annotation
                t1 = t2
                t2 = TFloating()
                G.add_annotation(t1, t2, {'speaker': ligne[0], 'speech': ligne[1]})

        # add /empty/ edge between previous annotation and episode end
        t1 = t2
        t2 = TEnd()
        G.add_annotation(t1, t2, {})

        return G
