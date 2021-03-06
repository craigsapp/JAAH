import os
from subprocess import call
import json
import argparse
from pychord_tools.common_utils import json_to_lab
from pychord_tools import path_db

utils_path = os.path.dirname(os.path.realpath(__file__))
eval_dir = "evaluation"
data_root = os.environ['JAZZ_HARMONY_DATA_ROOT']
if not os.path.exists(eval_dir):
    os.mkdir(eval_dir)

parser = argparse.ArgumentParser(description='Sonify chord annotations.')

parser.add_argument('--dd5', '-d', action='store_const', const=True, help='drop fifth in dominant chord')
parser.add_argument('--correction', '-c', type=float, default=0.075,
                    help='Greater numbers attenuates chords sound. Lower numbers make '
                         'it louder. Default value is 0.075.')
parser.add_argument('infile', type=argparse.FileType('r'), help='json input file')

args = parser.parse_args()

infile = args.infile.name
print(infile)

if args.dd5:
    dd5 = '1'
else:
    dd5 = '0'

with open(infile) as json_file:
    audiofile = path_db.get_audio_path(json.load(json_file)['mbid'])

if audiofile is None:
    print("No relation to audio file is specified in DB files referred by PYCHORD_TOOLS_PATH_DB_FILES")
    exit(-1)

audio_basename = os.path.basename(audiofile)
audio_name, audio_ext = os.path.splitext(audio_basename)

basename = os.path.basename(infile)
name, ext = os.path.splitext(basename)
labfile = os.path.join(eval_dir, name + ".lab")
resultfile = os.path.join(eval_dir, name + ".wav")
json_to_lab('chords', infile, labfile)
sonifyCommand =\
    "sonify('" + labfile.replace("'", "''") +\
    "', '" + audiofile.replace("'", "''") +\
    "', '" + resultfile.replace("'", "''") +\
    "', " + str(args.correction) +\
    ", " + dd5 + "); quit"
call([
    'matlab',
    '-nodesktop',
    '-nosplash',
    '-nojvm',
    '-r',
    sonifyCommand
])

print("Sonification is written to ", resultfile)
