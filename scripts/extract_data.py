from pyannote.parser import MDTMParser
from pyannote.parser import UEMParser
from pyannote.core import Segment
from pyannote.core import Annotation
from pandas import read_table
from tqdm import tqdm
from glob import glob

voxceleb_dir = 'scripts/voxceleb1'
data_uem = 'VoxCeleb/data/voxceleb1.{subset}.uem'
data_mdtm = 'VoxCeleb/data/voxceleb1.{subset}.mdtm'

list_txt = '{voxceleb_dir}/list.txt'.format(voxceleb_dir=voxceleb_dir)
glob_exp = '{voxceleb_dir}/*/*.txt'.format(voxceleb_dir=voxceleb_dir)

uris = list(read_table(list_txt, names=['uri'], dtype={'uri': str}).uri)


def parse_txt(txt):
    lines = [line.strip() for line in open(txt, 'r').readlines()]
    speaker = lines[0].split('\t')[-1]
    uri = lines[1].split('\t')[-1]
    duration = float(lines[2].split('\t')[-1].split()[0])
    subset = lines[3].split('\t')[-1]
    annotation = Annotation(uri=uri, modality='speaker')
    for line in lines[5:]:
        start, end = line.split()
        segment = Segment(float(start), float(end))
        annotation[segment] = speaker
    annotated = annotation.get_timeline()
    return subset, uri, annotation, annotated


mdtm_fp = {}
uem_fp = {}

mdtm_writer = MDTMParser()
uem_writer = UEMParser()

mdtm_fp = {
    'dev': open(data_mdtm.format(subset='dev'), mode='w'),
    'test': open(data_mdtm.format(subset='test'), mode='w'),
}

uem_fp = {
    'dev': open(data_uem.format(subset='dev'), mode='w'),
    'test': open(data_uem.format(subset='test'), mode='w'),
}

for path_txt in tqdm(glob(glob_exp)):

    subset, uri, annotation, annoted = parse_txt(path_txt)

    mdtm_writer.write(annotation, f=mdtm_fp[subset])
    uem_writer.write(annoted, f=uem_fp[subset])

for _, fp in mdtm_fp.items():
    fp.close()

for _, fp in uem_fp.items():
    fp.close()
