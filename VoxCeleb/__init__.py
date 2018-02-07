#!/usr/bin/env python
# encoding: utf-8

# The MIT License (MIT)

# Copyright (c) 2017-2018 CNRS

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

import pandas as pd
import os.path as op
from pyannote.core import Segment, Timeline, Annotation
from pyannote.database import Database
from pyannote.database.protocol import SpeakerVerificationProtocol
from pyannote.database.protocol import SpeakerIdentificationProtocol


class VerificationVoxCeleb1(SpeakerVerificationProtocol):

    def _xxx_iter(self, subset):

        data_dir = op.join(op.dirname(op.realpath(__file__)), 'data')
        data_csv = op.join(data_dir, 'voxceleb1.csv')

        # segment                          uri                      start end  speaker      verification identification
        # A.J._Buckley/1zcIwhmdeo4_0000001 A.J._Buckley/1zcIwhmdeo4 14.7  22.8 A.J._Buckley dev          trn

        data = pd.read_csv(data_csv, index_col=['segment'])
        data = data.groupby('verification').get_group(subset)

        for uri, datum in data.iterrows():

            annotation = Annotation(uri=uri)
            segment = Segment(0., datum.end - datum.start)
            annotation[segment] = datum.speaker

            annotated = annotation.get_timeline()

            current_file = {
                'uri': uri,
                'database': 'VoxCeleb',
                'annotation': annotation,
                'annotated': annotated,
            }

            yield current_file

    def trn_iter(self):
        raise NotImplementedError(
            'This protocol does not define a training set. '
            'Use developement set instead.')

    def dev_iter(self):
        return self._xxx_iter('dev')

    def tst_iter(self):
        return self._xxx_iter('tst')

    def trn_enrol_iter(self):
        raise NotImplementedError(
            'This protocol does not define a training set.')

    def dev_enrol_iter(self):
        raise NotImplementedError(
            'This protocol does not define trials on the development set.')

    def tst_enrol_iter(self):

        data_dir = op.join(op.dirname(op.realpath(__file__)), 'data')
        data_csv = op.join(data_dir, 'voxceleb1.csv')
        data = pd.read_csv(data_csv, index_col=['segment'])

        trial_csv = op.join(data_dir, 'voxceleb1.verification.test.csv')
        trials = pd.read_csv(trial_csv)

        for model_id in trials['enrolment'].unique():

            try:
                row = data.ix[model_id]
            except KeyError as e:
                # file_id = model_id.split('/')[1][:-8]
                # msg = '{file_id} marked as duplicate in VoxCeleb 1.1'
                # warnings.warn(msg.format(file_id=file_id))
                continue

            uri = model_id
            segment = Segment(0., row.end - row.start)
            current_enrolment = {
                'database': 'VoxCeleb',
                'uri': uri,
                'model_id': model_id,
                'enrol_with': Timeline(uri=uri, segments=[segment]),
            }

            yield current_enrolment

    def trn_try_iter(self):
        raise NotImplementedError(
            'This protocol does not define a training set.')

    def dev_try_iter(self):
        raise NotImplementedError(
            'This protocol does not define trials on the development set.')

    def tst_try_iter(self):

        data_dir = op.join(op.dirname(op.realpath(__file__)), 'data')
        data_csv = op.join(data_dir, 'voxceleb1.csv')
        data = pd.read_csv(data_csv, index_col=['segment'])

        trial_csv = op.join(data_dir, 'voxceleb1.verification.test.csv')
        trials = pd.read_csv(trial_csv)

        for _, trial in trials.iterrows():

            model_id = trial.enrolment

            try:
                _ = data.ix[model_id]
            except KeyError as e:
                # file_id = model_id.split('/')[1][:-8]
                # msg = '{file_id} marked as duplicate in VoxCeleb 1.1'
                # warnings.warn(msg.format(file_id=file_id))
                continue

            try:
                row = data.ix[trial.test]
            except KeyError as e:
                # file_id = trial.test.split('/')[1][:-8]
                # msg = '{file_id} marked as duplicate in VoxCeleb 1.1'
                # warnings.warn(msg.format(file_id=file_id))
                continue

            uri = trial.test
            segment = Segment(0., row.end - row.start)
            reference = trial.trial

            current_trial = {
                'database': 'VoxCeleb',
                'uri': uri,
                'try_with': Timeline(uri=uri, segments=[segment]),
                'model_id': model_id,
                'reference': bool(reference),
            }

            yield current_trial


class VerificationVoxCeleb1_Whole(SpeakerVerificationProtocol):

    def _xxx_iter(self, subset):

        data_dir = op.join(op.dirname(op.realpath(__file__)), 'data')
        data_csv = op.join(data_dir, 'voxceleb1.csv')
        data = pd.read_csv(data_csv, index_col=['segment'])
        data = data.groupby('verification').get_group(subset)

        for uri, rows in data.groupby('uri'):
            annotation = Annotation(uri=uri)
            for row in rows.itertuples():
                segment = Segment(row.start, row.end)
                annotation[segment] = row.speaker
            annotated = annotation.get_timeline()

            current_file = {
                'uri': uri,
                'database': 'VoxCeleb',
                'annotation': annotation,
                'annotated': annotated,
            }

            yield current_file

    def trn_iter(self):
        raise NotImplementedError(
            'This protocol does not define a training set. '
            'Use developement set instead.')

    def dev_iter(self):
        return self._xxx_iter('dev')

    def tst_iter(self):
        return self._xxx_iter('tst')

    def trn_enrol_iter(self):
        raise NotImplementedError(
            'This protocol does not define a training set.')

    def dev_enrol_iter(self):
        raise NotImplementedError(
            'This protocol does not define trials on the development set.')

    def tst_enrol_iter(self):

        data_dir = op.join(op.dirname(op.realpath(__file__)), 'data')
        data_csv = op.join(data_dir, 'voxceleb1.csv')
        data = pd.read_csv(data_csv, index_col=['segment'])

        trial_csv = op.join(data_dir, 'voxceleb1.verification.test.csv')
        trials = pd.read_csv(trial_csv)

        for model_id in trials['enrolment'].unique():

            try:
                row = data.ix[model_id]
            except KeyError as e:
                # file_id = model_id.split('/')[1][:-8]
                # msg = '{file_id} marked as duplicate in VoxCeleb 1.1'
                # warnings.warn(msg.format(file_id=file_id))
                continue

            uri = row.uri
            segment = Segment(row.start, row.end)
            current_enrolment = {
                'database': 'VoxCeleb',
                'uri': uri,
                'model_id': model_id,
                'enrol_with': Timeline(uri=uri, segments=[segment]),
            }

            yield current_enrolment

    def trn_try_iter(self):
        raise NotImplementedError(
            'This protocol does not define a training set.')

    def dev_try_iter(self):
        raise NotImplementedError(
            'This protocol does not define trials on the development set.')

    def tst_try_iter(self):

        data_dir = op.join(op.dirname(op.realpath(__file__)), 'data')
        data_csv = op.join(data_dir, 'voxceleb1.csv')
        data = pd.read_csv(data_csv, index_col=['segment'])

        trial_csv = op.join(data_dir, 'voxceleb1.verification.test.csv')
        trials = pd.read_csv(trial_csv)

        for trial in trials.itertuples():

            model_id = trial.enrolment

            try:
                _ = data.ix[model_id]
            except KeyError as e:
                # file_id = model_id.split('/')[1][:-8]
                # msg = '{file_id} marked as duplicate in VoxCeleb 1.1'
                # warnings.warn(msg.format(file_id=file_id))
                continue

            try:
                row = data.ix[trial.test]
            except KeyError as e:
                # file_id = trial.test.split('/')[1][:-8]
                # msg = '{file_id} marked as duplicate in VoxCeleb 1.1'
                # warnings.warn(msg.format(file_id=file_id))
                continue

            uri = row.uri
            segment = Segment(row.start, row.end)
            reference = row.trial

            current_trial = {
                'database': 'VoxCeleb',
                'uri': uri,
                'try_with': Timeline(uri=uri, segments=[segment]),
                'model_id': model_id,
                'reference': bool(reference),
            }

            yield current_trial

class IdentificationVoxCeleb1(SpeakerIdentificationProtocol):

    def trn_iter(self):

        data_dir = op.join(op.dirname(op.realpath(__file__)), 'data')
        data_csv = op.join(data_dir, 'voxceleb1.csv')
        data = pd.read_csv(data_csv, index_col=['segment'])
        data = data.groupby('identification').get_group('trn')

        for uri, datum in data.iterrows():

            annotation = Annotation(uri=uri)
            segment = Segment(0., datum.end - datum.start)
            annotation[segment] = datum.speaker

            annotated = annotation.get_timeline()

            current_file = {
                'uri': uri,
                'database': 'VoxCeleb',
                'annotation': annotation,
                'annotated': annotated,
            }

            yield current_file

    def dev_iter(self):
        raise NotImplementedError(
            'This protocol does not define a development set.')

    def tst_iter(self):
        raise NotImplementedError(
            'This protocol does not define a test set.')

    def common_enrol_iter(self):

        data_dir = op.join(op.dirname(op.realpath(__file__)), 'data')
        data_csv = op.join(data_dir, 'voxceleb1.csv')
        data = pd.read_csv(data_csv, index_col=['segment'])

        data = data.groupby('identification').get_group('trn')

        for model_id, model_rows in data.groupby('speaker'):
            uris = []
            enrol_with = []

            for uri, row in model_rows.iterrows():
                uris.append(uri)
                segment = Segment(0., row.end - row.start)
                enrol_with.append(Timeline(uri=uri, segments=[segment]))

            current_enrolment = {
                'database': 'VoxCeleb',
                'model_id': model_id,
                'uri': uris,
                'enrol_with': enrol_with
            }

            yield current_enrolment

    def trn_enrol_iter(self):
        raise NotImplementedError(
            'This protocol does not define trials on the training set.')

    def dev_enrol_iter(self):
        return self.common_enrol_iter()

    def tst_enrol_iter(self):
        return self.common_enrol_iter()

    def _xxx_try_iter(self, subset):

        data_dir = op.join(op.dirname(op.realpath(__file__)), 'data')
        data_csv = op.join(data_dir, 'voxceleb1.csv')
        data = pd.read_csv(data_csv, index_col=['segment'])

        data = data.groupby('identification').get_group(subset)

        for uri, trial in data.iterrows():

            reference = trial.speaker
            segment = Segment(0., trial.end - trial.start)

            current_trial = {
                'database': 'VoxCeleb',
                'uri': uri,
                'try_with': Timeline(uri=uri, segments=[segment]),
                'reference': reference,
            }

            yield current_trial

    def trn_try_iter(self):
        raise NotImplementedError(
            'This protocol does not define trials on the training set.')

    def dev_try_iter(self):
        return self._xxx_try_iter('dev')

    def tst_try_iter(self):
        return self._xxx_try_iter('tst')



class IdentificationVoxCeleb1_Whole(SpeakerIdentificationProtocol):

    def trn_iter(self):

        data_dir = op.join(op.dirname(op.realpath(__file__)), 'data')
        data_csv = op.join(data_dir, 'voxceleb1.csv')
        data = pd.read_csv(data_csv, index_col=['segment'])
        data = data.groupby('identification').get_group('trn')

        for uri, rows in data.groupby('uri'):
            annotation = Annotation(uri=uri)
            for row in rows.itertuples():
                segment = Segment(row.start, row.end)
                annotation[segment] = row.speaker
            annotated = annotation.get_timeline()

            current_file = {
                'uri': uri,
                'database': 'VoxCeleb',
                'annotation': annotation,
                'annotated': annotated,
            }

            yield current_file

    def dev_iter(self):
        raise NotImplementedError(
            'This protocol does not define a development set.')

    def tst_iter(self):
        raise NotImplementedError(
            'This protocol does not define a test set.')

    def common_enrol_iter(self):

        data_dir = op.join(op.dirname(op.realpath(__file__)), 'data')
        data_csv = op.join(data_dir, 'voxceleb1.csv')
        data = pd.read_csv(data_csv, index_col=['segment'])

        data = data.groupby('identification').get_group('trn')

        for model_id, model_rows in data.groupby('speaker'):
            uris = []
            enrol_with = []
            for uri, rows in model_rows.groupby('uri'):
                uris.append(uri)
                segments = []
                for row in rows.itertuples():
                    segments.append(Segment(row.start, row.end))
                enrol_with.append(Timeline(uri=uri, segments=segments))

            current_enrolment = {
                'database': 'VoxCeleb',
                'model_id': model_id,
                'uri': uris,
                'enrol_with': enrol_with
            }

            yield current_enrolment

    def trn_enrol_iter(self):
        raise NotImplementedError(
            'This protocol does not define trials on the training set.')

    def dev_enrol_iter(self):
        return self.common_enrol_iter()

    def tst_enrol_iter(self):
        return self.common_enrol_iter()

    def _xxx_try_iter(self, subset):

        data_dir = op.join(op.dirname(op.realpath(__file__)), 'data')
        data_csv = op.join(data_dir, 'voxceleb1.csv')
        data = pd.read_csv(data_csv, index_col=['segment'])

        data = data.groupby('identification').get_group(subset)

        for trial in data.itertuples():

            reference = trial.speaker
            uri = trial.uri
            segment = Segment(trial.start, trial.end)

            current_trial = {
                'database': 'VoxCeleb',
                'uri': uri,
                'try_with': Timeline(uri=uri, segments=[segment]),
                'reference': reference,
            }

            yield current_trial

    def trn_try_iter(self):
        raise NotImplementedError(
            'This protocol does not define trials on the training set.')

    def dev_try_iter(self):
        return self._xxx_try_iter('dev')

    def tst_try_iter(self):
        return self._xxx_try_iter('tst')


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
            'SpeakerVerification', 'VoxCeleb1_Whole', VerificationVoxCeleb1_Whole)

        self.register_protocol(
            'SpeakerVerification', 'VoxCeleb1', VerificationVoxCeleb1)

        self.register_protocol(
            'SpeakerIdentification', 'VoxCeleb1_Whole', IdentificationVoxCeleb1_Whole)

        self.register_protocol(
            'SpeakerIdentification', 'VoxCeleb1', IdentificationVoxCeleb1)
