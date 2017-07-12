#!/usr/bin/env python
# encoding: utf-8

# The MIT License (MIT)

# Copyright (c) 2017 CNRS

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# AUTHORS
# Hervé BREDIN - http://herve.niderb.fr


from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


import os.path as op
from pyannote.database import Database
from pyannote.database.protocol import SpeakerDiarizationProtocol
from pyannote.parser import MDTMParser
from pyannote.parser import UEMParser


class VoxCeleb1(SpeakerDiarizationProtocol):
    """VoxCeleb1 protocol """

    def trn_iter(self):
        for _ in []:
            yield

    def xxx_iter(self, xxx):

        data_dir = op.join(op.dirname(op.realpath(__file__)), 'data')

        annotation = MDTMParser().read(
            op.join(data_dir, 'voxceleb1.{xxx}.mdtm'.format(xxx=xxx)))

        annotated = UEMParser().read(
            op.join(data_dir, 'voxceleb1.{xxx}.uem'.format(xxx=xxx)))

        for uri in sorted(annotation.uris):
            yield {
                'database': 'VoxCeleb',
                'uri': uri,
                'annotation': annotation(uri),
                'annotated': annotated(uri),
            }

    def dev_iter(self):
        return self.xxx_iter('dev')

    def tst_iter(self):
        return self.xxx_iter('test')

class VoxCeleb(Database):
    """VoxCeleb: a large-scale speaker identification dataset

Citation
========
@InProceedings{Nagrani17,
  author       = "Nagrani, A. and Chung, J.~S. and Zisserman, A.",
  title        = "VoxCeleb: a large-scale speaker identification dataset",
  booktitle    = "INTERSPEECH",
  year         = "2017",
}

Webpage
=======
http://www.robots.ox.ac.uk/~vgg/data/voxceleb/

    """
    def __init__(self, preprocessors={}, **kwargs):
        super(VoxCeleb, self).__init__(preprocessors=preprocessors, **kwargs)

        self.register_protocol(
            'SpeakerDiarization', 'VoxCeleb1', VoxCeleb1)
