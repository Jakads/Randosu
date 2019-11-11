import os
import sys
from msvcrt import getch
from random import seed, randint, uniform
from time import time
from pathvalidate import sanitize_filename
from functions import choose, inputnum, exit

def random(q, fn, path, content):
    sys.stdin = os.fdopen(fn)

    try:
        # Dictionary List for notes
        notes = []
        
        # Change Stack Leniency to 0
        for c in content:
            if c.startswith('StackLeniency:'):
                q.put(f'replaced StackLeniency on line {content.index(c)+1}')
                content[content.index(c)] = 'StackLeniency:0\n'
                break
        
        objindex = content.index('[HitObjects]\n')
        q.put(f'objindex = {objindex}')
        
        # Parse notes from the next row of [HitObjects] to EOF
        k = 0
        for c in content[objindex+1:]:
            # Ignore comments and blanks
            if c.startswith('//') or c == '\n':
                continue
            
            # Syntax: x, y, extra
            content_split = c.split(',')
            note_x = int(content_split[0])
            note_ms = int(content_split[2])
            note_extra = content_split[3:]
            notes.append({
                'x': note_x,
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
    
    print('True Random? (Y/N)')
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
    
    i = 0
    randnotes = []

    q.put('== Randomization Start ==')
    
    # Randomize position of the notes
    for n in notes:
        q.put(f'{i+1}@{n["ms"]}')
        # Distance should be lower than set
        while True:
            if (i == 0) or TrueRandom:
                randx = randint(0, 512)
                break
    
            # Add 0~10 for chaos
            diffx = n['x'] - notes[i-1]['x'] + uniform(0, 10)
    
            factor = uniform(minsf, maxsf)
    
            if randint(0, 1):
                randx = randnotes[i-1]['x'] + int(diffx * factor)
            else:
                randx = randnotes[i-1]['x'] - int(diffx * factor)
    
            # If factor is too high, corner the object, but only if it's truly impossible
            prevx = randnotes[i-1]['x']
            if abs(diffx) * minsf > max(prevx, 512-prevx):
                if randx < 0:
                    randx = 0
                if randx > 512:
                    randx = 512
    
            if 0 <= randx <= 512:
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
                'ms': n['ms'],
                'extra': n['extra']
            })
        i += 1
        q.put(f'x={randx}, diffx={diffx}, nextdistance={notes[i+1]["x"] - notes[i]["x"] if i < len(notes) - 1 else ""}')
    
        
    q.put(f'exporting to {filename}:')
    with open(filename,'w',encoding='utf-8') as osu:
        for c in content[:objindex+1]:
            osu.write(c)
            q.put(c)
    
        for n in randnotes:
            osu.write(f'{n["x"]},192,{n["ms"]},{",".join(n["extra"])}')
            q.put(','.join(n))
    
    print(f'\nSuccessfully created {filename}!')

    q.put('done')