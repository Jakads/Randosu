import os
import sys
from msvcrt import getch
from random import seed, randint, uniform
from time import time
from pathvalidate import sanitize_filename

def randosu(path, content):
    # Dictionary List for notes
    notes = []
    
    # Change Stack Leniency to 0
    for c in content:
        if c.startswith('StackLeniency:'):
            content[content.index(c)] = 'StackLeniency:0\n'
            break
    
    objindex = content.index('[HitObjects]\n')
    
    # Parse notes from the next row of [HitObjects] to EOF
    for c in content[objindex+1:]:
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
    
    # Random Seed input
    print('read success')
    randseed = input('seed(optional): ')

    # If no seed is given, use current timestamp as the seed
    if randseed == '':
        randseed = int(time())
    seed(randseed)
    
    print('True Random? (Y/N)')
    while True:
        answer = getch().decode()
        if answer in 'yYnN':
            break
    TrueRandom = True if answer in 'yY' else False
    
    if not TrueRandom:
        while True:
            try:
                min = input('min scale factor(default 0.5): ')
                if min == '':
                    min = 0.5
                min = float(min)
    
                max = input('max scale factor(default 2.0): ')
                if max == '':
                    max = 2.0
                max = float(max)
                break
            except:
                print('number plz')
    
        # I bet someone would try this so
        if min > max:
            tmp = min
            min = max
            max = tmp
    
    while True:
        try:
            red = input('chance of red anchors(%, default 25): ')
            if red == '':
                red = 25
            red = float(red)
            break
        except:
            print('number plz')
    
    if red > 100:
        red = 100
    if red < 0:
        red = 0
    
    # Change difficulty & output file name
    for c in content:
        if c.startswith('Version:'):
            # Exclude '\n'
            diffname = c.split(':', 1)[1][:-1]
            index = content.index(c)
    
            rand = f"truerand({red})" if TrueRandom else f"rand({min}~{max},{red})"
            Rand = f"TrueRandomized(Red:{red}%)" if TrueRandom else f"Randomized({min}~{max}x, Red:{red}%)"
            
            content[index] = f'Version:{Rand}_{diffname} (Seed:{randseed})\n'
            filename = f'{os.path.dirname(path)}\\{rand}_{randseed}_{sanitize_filename(diffname)}.osu'
    
    i=0
    randnotes = []
    
    # Randomize position of the notes
    for n in notes:
        # Distance should be lower than set
        while True:
            if (i == 0) or TrueRandom:
                randx = randint(0, 512)
                break
    
            # Add 0~10 for chaos
            diffx = n['x'] - notes[i-1]['x'] + uniform(0, 10)
    
            factor = uniform(min, max)
    
            if randint(0, 1):
                randx = randnotes[i-1]['x'] + int(diffx * factor)
            else:
                randx = randnotes[i-1]['x'] - int(diffx * factor)
    
            # If factor is too high, corner the object
            if abs(int(diffx * factor)) > 1200:
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
        i+=1
    
        
    with open(filename,'w',encoding='utf-8') as osu:
        for c in content[:objindex+1]:
            osu.write(c)
    
        for n in randnotes:
            osu.write(f'{n["x"]},192,{n["ms"]},{",".join(n["extra"])}')
    
    print('done')
    getch()