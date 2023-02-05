import sys
import os
#os.system("apt install fluidsynth")
import json
import secrets
import copy
import gradio as gr
import TMIDI

from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from itertools import islice, accumulate

from pprint import pprint

import tqdm.auto
from tqdm import auto
#from midi2audio import FluidSynth
from IPython.display import display, Javascript, HTML, Audio

# only for plotting pianoroll
import pretty_midi
import librosa.display
import matplotlib.pyplot as plt


print('Loading the Karaoke model. Please wait...')
data = TMIDI.Tegridy_Any_Pickle_File_Loader('Karaoke-English-Full')

print('Done!')
print('Prepping data...')

kar_ev_f = data[2]

kar = []
karaoke = []

for k in auto.tqdm(kar_ev_f):
  k.sort(reverse=False, key=lambda x: x[1])
  for kk in k:
    
    if kk[0] == 'note' or kk[0] == 'text_event':
      kar.append(kk)

kar_words = []
for o in auto.tqdm(kar):
  if o[0] != 'note':
    kar_words.append(str(o[2]).lower())

print('Done! Enjoy! :)')

def TextToMusic(lyrics):
  text = list(lyrics.split("."))
  randomize_words_matching = True
  song = []

  words_lst = ''

  print('=' * 100)

  print('Deep-Muse Text to Music Generator')
  print('Starting up...')

  print('=' * 100)

  for t in auto.tqdm(text):
    txt = t.lower().split(' ')
    
    kar_words_split = list(TMIDI.Tegridy_List_Slicer(kar_words, len(txt)))
    
    ratings = []

    for k in kar_words_split:
      ratings.append(fuzz.ratio(txt, k))
    
    if randomize_words_matching:
      
      try:
        ind = ratings.index(secrets.choice([max(ratings)-5, max(ratings)-4, max(ratings)-3, max(ratings)-2, max(ratings)-1, max(ratings)]))
      except:
        ind = ratings.index(max(ratings))
    
    else:
      ind = ratings.index(max(ratings))

    words_list = kar_words_split[ind]
    pos = ind * len(txt)
    

    print(words_list)

    words_lst += ' '.join(words_list) + chr(10)

    c = 0
    for i in range(len(kar)):
      if kar[i][0] != 'note':
        if c == pos:
          idx = i
          break

      if kar[i][0] != 'note':
        c += 1
  
    c = 0
    for i in range(idx, len(kar)):
      if kar[i][0] != 'note':
        if c == len(txt):
          break

      if kar[i][0] == 'note':
        song.append(kar[i])

      if kar[i][0] != 'note':
        c += 1
        song.append(kar[i])

  so = [y for y in song if len(y) > 3]
  if so != []: sigs = TMIDI.Tegridy_MIDI_Signature(so, so)

  print('=' * 100)

  print(sigs[0])

  print('=' * 100)

  song1 = []
  p = song[0]
  p[1] = 0
  time = 0

  song.sort(reverse=False, key=lambda x: x[1])

  for i in range(len(song)-1):

      ss = copy.deepcopy(song[i])
      if song[i][1] != p[1]:
        
        if abs(song[i][1] - p[1]) > 1000:
          time += 300
        else:
          time += abs(song[i][1] - p[1])

        ss[1] = time 
        song1.append(ss)
        
        p = copy.deepcopy(song[i])
      else:
        
        ss[1] = time
        song1.append(ss)
        
        p = copy.deepcopy(song[i])

  pprint(words_lst, compact=True)
  print('=' * 100)
  TMIDI.Tegridy_SONG_to_MIDI_Converter(song1, output_file_name='deep-muse-Output-MIDI')
  fname = 'deep-muse-Output-MIDI'

  fn = os.path.basename(fname + '.mid')
  fn1 = fn.split('.')[0]
  print('Playing and plotting composition...')

  pm = pretty_midi.PrettyMIDI(fname + '.mid')

  # Retrieve piano roll of the MIDI file
  piano_roll = pm.get_piano_roll()

  plt.figure(figsize=(14, 5))
  librosa.display.specshow(piano_roll, x_axis='time', y_axis='cqt_note', fmin=1, hop_length=160, sr=16000, cmap=plt.cm.hot)
  plt.title('Composition: ' + fn1)
  plt.savefig('my_plot.png')
  print('Synthesizing the last output MIDI. Please stand-by... ')
  #FluidSynth("/usr/share/sounds/sf2/FluidR3_GM.sf2", 16000).midi_to_audio(str(fname + '.mid'), str(fname + '.wav'))
  Audio(str(fname + '.wav'), rate=16000)

  return fname + '.wav','my_plot.png'

demo = gr.Interface(
    fn=TextToMusic, 
    inputs=[gr.inputs.Textbox(label='Enter Prompt')],
    outputs=["audio","image"],
    examples=[["I love you very very much.I can not live without you.You always present on my mind.I often think about you.I am all out of love I am so lost without you."]],
    title="Lyrics Text To Music",
    )
demo.launch(debug=True)