# VoxCeleb plugin for pyannote.database

This package provides an implementation of the speaker verification and speaker identification protocols used in the `VoxCeleb` paper.

Actual VGGVox models can be obtained from the [authors](https://github.com/a-nagrani/VGGVox) of the original paper.

## Citation

Please cite the following reference if your research relies on the `VoxCeleb` dataset:

```bibtex
@InProceedings{VoxCeleb,
  author = {Nagrani, A. and Chung, J.~S. and Zisserman, A.},
  title = {{VoxCeleb: a large-scale speaker identification dataset}},
  booktitle = {{Interspeech 2017, 18th Annual Conference of the International Speech Communication Association}},
  year = {2017},
  month = {August},
  address = {Stockholm, Sweden},
  url = {http://www.robots.ox.ac.uk/~vgg/data/voxceleb/},
}
```

Please cite the following references if your research relies on this package. This is where the whole `pyannote.database` framework was first introduced:

```bibtex
@inproceedings{pyannote.metrics,
  author = {Herv\'e Bredin},
  title = {{pyannote.metrics: a toolkit for reproducible evaluation, diagnostic, and error analysis of speaker diarization systems}},
  booktitle = {{Interspeech 2017, 18th Annual Conference of the International Speech Communication Association}},
  year = {2017},
  month = {August},
  address = {Stockholm, Sweden},
  url = {http://pyannote.github.io/pyannote-metrics},
}
```

## Installation

```bash
$ pip install pyannote.db.voxceleb
```

## Usage

### Speaker verification protocol


```python
>>> from pyannote.database import get_protocol
>>> protocol = get_protocol('VoxCeleb.SpeakerVerification.VoxCeleb1')
```

First, one can use `protocol.development` generator to train the background model.

```python
>>> for training_file in protocol.development():
...
...    uri = training_file['uri']
...    print('Current filename is {0}.'.format(uri))
...
...    # "who speaks when" as a pyannote.core.Annotation instance
...    annotation = training_file['annotation']
...    for segment, _, speaker in annotation.itertracks(yield_label=True):
...        print('{0} speaks between t={1:.1f}s and t={2:.1f}s.'.format(
...            speaker, segment.start, segment.end))
...    
...    break  # this should obviously be replaced
...           # by the actual background training
```
```
Current filename is A.J._Buckley/1zcIwhmdeo4_0000001.
A.J._Buckley speaks between t=0.0s and t=8.1s.
```

Then, one should use `protocol.test_enrolment` generator to enrol speakers:

```python
>>> models = {}  # dictionary meant to store all enrolments
>>> for enrolment in protocol.test_enrolment():
...
...    # unique model identifier
...    model_id = enrolment['model_id']
...
...    uri = enrolment['uri']
...    print('Current filename is {0}.'.format(uri))
...
...    # enrolment segment as a pyannote.core.Timeline instance
...    timeline = enrolment['enrol_with']
...    for segment in timeline:
...        print('Use speech between t={0:.1f}s and t={1:.1f}s for enrolment.'.format(segment.start, segment.end))
...    
...    # enrol_func should return the actual model
...    models[model_id] = enrol_func(uri, timeline)
...   
...    break  # one should obviously iterate over all enrolments
```

```
Current filename is Eartha_Kitt/x6uYqmx31kE_0000001.
Use speech between t=0.0s and t=5.7s for enrolment.
```

Finally, `protocol.test_trial` generator provides the list of trials:

```python
>>> for trial in protocol.test_trial():
...
...    uri = trial['uri']
...    print('Current filename is {0}.'.format(uri))
...
...    # trial segment as a pyannote.core.Timeline instance
...    timeline = trial['try_with']
...    for segment in timeline:
...        print('Use speech between t={0:.1f}s and t={1:.1f}s for trial.'.format(segment.start, segment.end))
...
...    model_id = trial['model_id']
...    model = models[model_id]
...    print('Compare to model "{0}".'.format(model_id))
...
...    # True for target trials, False for non target trials
...    reference = trial['reference']
...    print('This is a {0} trial.'.format('target' if reference else 'non-target'))
...    
...    score = try_func(uri, segment, model)
...
...    break  # one should obviously iterate over all trials
```

```
Current filename is Eartha_Kitt/8jEAjG6SegY_0000008.
Use speech between t=0.0s and t=6.8s for trial.
Compare to model "Eartha_Kitt/x6uYqmx31kE_0000001".
This is a target trial.
```

### Speaker identification protocol

The speaker identification protocol on `VoxCeleb1` is initialized as follows:

```python
>>> from pyannote.database import get_protocol
>>> protocol = get_protocol('VoxCeleb.SpeakerIdentification.VoxCeleb1')
```

First, one can use `protocol.train` generator to iterate over the training set:

```python
>>> for training_file in protocol.train():
...
...    uri = training_file['uri']
...    print('Current filename is {0}.'.format(uri))
...
...    # "who speaks when" as a pyannote.core.Annotation instance
...    annotation = training_file['annotation']
...    for segment, _, speaker in annotation.itertracks(yield_label=True):
...        print('{0} speaks between t={1:.1f}s and t={2:.1f}s.'.format(
...            speaker, segment.start, segment.end))
...    
...    break  # this should obviously be replaced
...           # by the actual training
```
```
Current filename is A.J._Buckley/1zcIwhmdeo4_0000001.
A.J._Buckley speaks between t=0.0s and t=8.1s.
```

The test set can be iterated over using the `protocol.test_trial` generator:

```python
>>> for trial in protocol.test_trial():
...
...    uri = trial['uri']
...    print('Current filename is {0}.'.format(uri))
...
...    # trial segment as a pyannote.core.Timeline instance
...    timeline = trial['try_with']
...    for segment in timeline:
...        print('Use speech between t={0:.1f}s and t={1:.1f}s for trial.'.format(segment.start, segment.end))
...
...    reference = trial['reference']
...    print('The expected output is "{0}".'.format(reference))
...
...    decision = try_func(uri, segment)
...
...    break  # one should obviously iterate over all trials
```
```
Current filename is A.J._Buckley/Y8hIVOBuels_0000001.
Use speech between t=0.0s and t=4.6s for trial.
The expected output is "A.J._Buckley".
```

A validation set is also available.  One can simply replace `test_trial` by `development_trial`.
