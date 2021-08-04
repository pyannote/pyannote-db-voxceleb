#!/usr/bin/env python
# encoding: utf-8

# The MIT License (MIT)

# Copyright (c) 2017-2020 CNRS

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

__version__ = get_versions()["version"]
del get_versions

from itertools import chain
import pandas as pd
from pathlib import Path
from pyannote.core import Segment, Timeline, Annotation
from pyannote.database import Database
from pyannote.database.protocol import SpeakerVerificationProtocol


class Base(SpeakerVerificationProtocol):
    def xxx_iter(self, voxceleb, subset):
        """Iterate on VoxCeleb files

        Each file is yielded as a dictionary with the following keys:

        ['uri'] (`str`)
            Unique file identifier.


        Parameters
        ----------
        voxceleb : {1, 2}
            VoxCeleb1 or VoxCeleb2
        subset : {'dev', 'tst'}
            Developement or test subset.
        """

        # load durations
        path = Path(__file__).parent / "data"
        path = path / f"vox{voxceleb:d}_{subset}_duration.txt.gz"
        content = pd.read_table(
            path, names=["uri", "duration"], index_col="uri", delim_whitespace=True
        )

        for uri, duration in content.itertuples():

            speaker = uri.split("/")[0]
            segment = Segment(0, duration)

            annotation = Annotation(uri=uri)
            annotation[segment] = speaker

            annotated = Timeline(segments=[segment], uri=uri)

            current_file = {
                "uri": uri,
                "database": "VoxCeleb",
                "annotation": annotation,
                "annotated": annotated,
            }

            yield current_file

    def train_iter(self):
        raise NotImplementedError("This protocol does not define a training set.")

    def development_iter(self):
        raise NotImplementedError("This protocol does not define a development set.")

    def test_iter(self):
        raise NotImplementedError("This protocol does not define a test set.")

    def xxx_try_iter(self, protocol):

        # load all VoxCeleb1 durations (dev AND tst)
        path = Path(__file__).parent / "data" / "vox1_dev_duration.txt.gz"
        dev = pd.read_table(
            path, names=["uri", "duration"], index_col="uri", delim_whitespace=True
        )

        path = Path(__file__).parent / "data" / "vox1_tst_duration.txt.gz"
        tst = pd.read_table(
            path, names=["uri", "duration"], index_col="uri", delim_whitespace=True
        )

        durations = dev.append(tst)

        # load tests
        path = Path(__file__).parent / "data" / f"verif_{protocol}.txt.gz"
        trials = pd.read_table(
            path, delim_whitespace=True, names=["reference", "file1", "file2"]
        )
        trials.sort_values("file1", inplace=True)

        for _, reference, file1, file2 in trials.itertuples():

            uri1 = file1[:-4]
            duration1 = durations.loc[uri1].item()
            segment1 = Segment(0, duration1)

            uri2 = file2[:-4]
            duration2 = durations.loc[uri2].item()
            segment2 = Segment(0, duration2)

            current_trial = {
                "reference": reference,
                "file1": {
                    "database": "VoxCeleb",
                    "uri": uri1,
                    "try_with": Timeline(segments=[segment1], uri=uri1),
                },
                "file2": {
                    "database": "VoxCeleb",
                    "uri": uri2,
                    "try_with": Timeline(segments=[segment2], uri=uri2),
                },
            }

            yield current_trial

    def train_trial_iter(self):
        raise NotImplementedError(
            "This protocol does not define trials on the training set."
        )

    def development_trial_iter(self):
        raise NotImplementedError(
            "This protocol does not define trials on the development set."
        )

    def test_trial_iter(self):
        raise NotImplementedError(
            "This protocol does not define trials on the test set."
        )


class VoxCeleb1(Base):
    def train_iter(self):
        return self.xxx_iter(1, "dev")

    def test_iter(self):
        return self.xxx_iter(1, "tst")

    def test_trial_iter(self):
        return self.xxx_try_iter("original")


class VoxCeleb1_TrueID(VoxCeleb1):
    def train_iter(self):

        path = Path(__file__).parent / "data" / "vox1_identities.txt.gz"
        identities = pd.read_table(
            path, names=["klass", "speaker"], delim_whitespace=True, index_col=["klass"]
        )

        mapping = {klass: speaker for klass, speaker in identities.itertuples()}

        for current_file in super().train_iter():
            current_file["annotation"].rename_labels(mapping, copy=False)
            yield current_file


class VoxCeleb1_X(VoxCeleb1):
    """Same as VoxCeleb1 except a subset of the training set speakers is
    kept to build an actual developement set.
    """

    def train_iter(self):
        return self.xxx_iter(1, "xtrn")

    def development_iter(self):
        return self.xxx_iter(1, "xdev")

    def development_trial_iter(self):
        return self.xxx_try_iter("x")


class Debug(VoxCeleb1_X):
    def train_iter(self):
        for f, file in enumerate(super().train_iter()):
            if f % 1000 == 0:
                yield file

    def development_trial_iter(self):
        for t, trial in enumerate(super().development_trial_iter()):
            if t < 100:
                yield trial
            else:
                break

    def test_trial_iter(self):
        for t, trial in enumerate(super().test_trial_iter()):
            if t < 100:
                yield trial
            else:
                break


class VoxCeleb2(Base):
    def train_iter(self):
        return self.xxx_iter(2, "dev")

    def test_iter(self):
        return self.xxx_iter(2, "tst")

    def test_trial_iter(self):
        return self.xxx_try_iter("original")


class VoxCeleb2_Exhaustive(Base):
    def train_iter(self):
        return self.xxx_iter(2, "dev")

    def test_iter(self):
        return self.xxx_iter(2, "tst")

    def test_trial_iter(self):
        return self.xxx_try_iter("exhaustive")


class VoxCeleb2_Hard(Base):
    def train_iter(self):
        return self.xxx_iter(2, "dev")

    def test_iter(self):
        return self.xxx_iter(2, "tst")

    def test_trial_iter(self):
        return self.xxx_try_iter("hard")


class VoxCeleb_X(VoxCeleb1_X):
    def train_iter(self):
        for file in self.xxx_iter(1, "xtrn"):
            yield file
        for file in self.xxx_iter(2, "dev"):
            yield file


class VoxCeleb(Database):
    """VoxCeleb

    References
    ----------
    A. Nagrani, J. S. Chung, A. Zisserman. "VoxCeleb: a large-scale speaker
    identification dataset". Interspeech 2017.

    J. S. Chung, A. Nagrani, A. Zisserman. "VoxCeleb2: Deep Speaker
    Recognition". Interspeech 2018.

    http://www.robots.ox.ac.uk/~vgg/data/voxceleb/
    """

    def __init__(self, **kwargs):
        super(VoxCeleb, self).__init__(**kwargs)

        self.register_protocol("SpeakerVerification", "Debug", Debug)

        self.register_protocol("SpeakerVerification", "VoxCeleb1", VoxCeleb1)

        self.register_protocol(
            "SpeakerVerification", "VoxCeleb1_TrueID", VoxCeleb1_TrueID
        )

        self.register_protocol("SpeakerVerification", "VoxCeleb1_X", VoxCeleb1_X)

        self.register_protocol("SpeakerVerification", "VoxCeleb2", VoxCeleb2)

        self.register_protocol(
            "SpeakerVerification", "Exhaustive", VoxCeleb2_Exhaustive
        )

        self.register_protocol("SpeakerVerification", "Hard", VoxCeleb2_Hard)

        self.register_protocol("SpeakerVerification", "VoxCeleb_X", VoxCeleb_X)
