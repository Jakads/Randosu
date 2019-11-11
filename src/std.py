import os
import sys
from msvcrt import getch
from random import seed, randint, uniform, choice
from time import time
from math import sin, cos, pi
from pathvalidate import sanitize_filename
from functions import choose, inputnum, exit

def random(q, fn, path, content):
    sys.stdin = os.fdopen(fn)

    try:
        # Dictionary List for notes
        notes = []

        # Dictionary List for BPMs
        bpms = []
        
        # Change Stack Leniency to 0
        for c in content:
            if c.startswith('StackLeniency:'):
                q.put(f'replaced StackLeniency on line {content.index(c)+1}')
                content[content.index(c)] = 'StackLeniency:0\n'
                break

        bpmindex = content.index('[TimingPoints]\n')
        q.put(f'bpmindex = {bpmindex}')
        
        objindex = content.index('[HitObjects]\n')
        q.put(f'objindex = {objindex}')

        # Parse BPMs from the next row of [TimingPoints] to [HitObjects]
        k = 0
        for c in content[bpmindex+1:objindex]:
            # BPM Points: ms,60000/BPM,[],[],[],[],1,[]
            # 60000/BPM = ms per beat
            content_split = c.split(',')
            
            # Ignore comments and others
            if c.startswith('//') or len(content_split) != 8:
                continue

            if content_split[6] == '1':
                bpms.append({
                    # {ms, mpb}
                    'ms': float(content_split[0]),
                    'mpb': float(content_split[1])
                })
                k += 1
                q.put(f'append to bpms ({k}@{content_split[0]})')

        q.put(f'bpms import success')

        # Parse notes from the next row of [HitObjects] to EOF
        k = 0
        for c in content[objindex+1:]:
            # Ignore comments and blanks
            if c.startswith('//') or c == '\n':
                continue
            
            # Syntax: x, y, extra
            content_split = c.split(',')
            note_x = int(content_split[0])
            note_y = int(content_split[1])
            note_ms = int(content_split[2])
            note_extra = content_split[3:]
            notes.append({
                'x': note_x,
                'y': note_y,
                'ms': note_ms,
                'extra': note_extra,
                'isSlider': len(content_split) > 7
            })
            k += 1
            q.put(f'append to notes ({k}@{note_ms})')

        q.put(f'notes import success')

    except:
        exit('Import failed. The .osu file is invalid.')
    
    # Random Seed input
    print('Import success.')

    randseed = input('Seed(optional): ')
    
    # If no seed is given, use current timestamp as the seed
    if randseed == '':
        q.put('no seed given')
        randseed = int(time())
    seed(randseed)
    q.put(f'seed = {randseed}')
    
    print('Enable True Random? (Y/N)')
    TrueRandom = True if choose() else False
    q.put(f'TrueRandom = {TrueRandom}')
    
    if not TrueRandom:
        minsf = inputnum('Min Scale Factor(Default: 0.8): ', 0.8)
        maxsf = inputnum('Max Scale Factor(Default: 1.5): ', 1.5)
    
        # I bet someone would try this so
        if minsf > maxsf:
            tmp = minsf
            minsf = maxsf
            maxsf = tmp

        q.put(f'minsf = {minsf}, maxsf = {maxsf}')
    
    red = inputnum('Chance of Red Anchors(%, default 25): ', 25)
    
    if red > 100:
        red = 100
    if red < 0:
        red = 0

    q.put(f'red = {red}')
    
    # Change difficulty & output file name
    for c in content:
        if c.startswith('Version:'):
            # Exclude '\n'
            diffname = c.split(':', 1)[1][:-1]
            index = content.index(c)

            q.put(f'replaced Version on line {content.index(c)+1}')
    
            rand = f"truerand({red})" if TrueRandom else f"rand({minsf}~{maxsf},{red})"
            Rand = f"TrueRandomized(Red:{red}%)" if TrueRandom else f"Randomized({minsf}~{maxsf}x, Red:{red}%)"

            content[index] = f'Version:{Rand}_{diffname} (Seed:{randseed})\n'
            filename = f'{os.path.dirname(path)}\\{rand}_{randseed}_{sanitize_filename(diffname)}.osu'
            break
    
    randnotes = []
    i = 0
    rad = 0
    d = lambda x, y: (x ** 2 + y ** 2) ** 0.5

    q.put('== Randomization Start ==')

    # Randomize position of the notes
    for n in notes:
        q.put(f'{i+1}@{n["ms"]}')
        # Distance should be lower than set
        while True:
            if (i == 0) or TrueRandom:
                randx = randint(0, 512)
                randy = randint(0, 384)
                break

            # Get current ms per beat
            mpb = -1

            for b in bpms:
                if n['ms'] < b['ms']:
                    mpb = bpms[bpms.index(b)-1]['mpb']
                    break
        
            if mpb == -1:
                mpb = bpms[-1]['mpb']
    
            # Add 0~10 for chaos
            diffx = n['x'] - notes[i-1]['x'] + uniform(0, 10)
            diffy = n['y'] - notes[i-1]['y'] + uniform(0, 10)
            diffms = n['ms'] - notes[i-1]['ms']

            distance = d(diffx, diffy)
    
            # rad is closer to pi if diffms is bigger, peak = 1/2 snap
            rad += pi * uniform(0, min(1, (2 * diffms / mpb) ** 1.5)) * choice([1, -1])
            factor = uniform(minsf, maxsf)
    
            randx = randnotes[i-1]['x'] + int(distance * factor * cos(rad))
            randy = randnotes[i-1]['y'] + int(distance * factor * sin(rad))
    
            # If factor is too high, corner the object, but only if it's truly impossible
            prevx = randnotes[i-1]['x']
            prevy = randnotes[i-1]['y']
            if distance * minsf > max(d(prevx, prevy), d(512-prevx, prevy), d(prevx, 384-prevy), d(512-prevx, 384-prevy)):
                if randx < 0:
                    randx = 0
                if randx > 512:
                    randx = 512
                if randy < 0:
                    randy = 0
                if randy > 384:
                    randy = 384
    
            if (0 <= randx <= 512) and (0 <= randy <= 384):
                break
            
        # if slider:
        if n['isSlider']:
            # Getting curve points
            point = n['extra'][2].split('|')
            curve = [point[0]]
    
            # Randomize curve points
            for k in range(len(point)-1):
                curvex = randint(0, 512)
                curvey = randint(0, 384)
                curve.append(f'{curvex}:{curvey}')
    
                # Red Anchors
                # Always end with normal curve point to prevent slider ending too early
                if uniform(0, 100) < red and k != len(point) - 2:
                    curve.append(f'{curvex}:{curvey}')
    
            n['extra'][2] = '|'.join(curve)
    
        randnotes.append({
                'x': randx,
                'y': randy,
                'ms': n['ms'],
                'extra': n['extra']
            })
        i += 1
        q.put(f'x={randx}, y={randy}, rad={rad}, nextdistance={d(notes[i+1]["x"] - notes[i]["x"], notes[i+1]["y"] - notes[i]["y"]) if i < len(notes) - 1 else ""}')

    q.put(f'exporting to {filename}:')
    with open(filename,'w',encoding='utf-8') as osu:
        for c in content[:objindex+1]:
            osu.write(c)
            q.put(c)
    
        for n in randnotes:
            osu.write(f'{n["x"]},{n["y"]},{n["ms"]},{",".join(n["extra"])}')
            q.put(','.join(n))
    
    print(f'\nSuccessfully created {filename}!')
    
    q.put('done')