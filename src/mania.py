import os
import sys
from msvcrt import getch
from random import seed, randint, uniform, shuffle, choice
from time import time
from pathvalidate import sanitize_filename
from functions import choose, inputnum, exit
from math import ceil

def random(q, fn, path, content):
    sys.stdin = os.fdopen(fn)
    
    try:
        # CS = Keys
        keys = [int(i.split(':')[1]) for i in content if i.split(':')[0] == 'CircleSize'][0]
        print(f'Keys: {keys}')
        q.put(f'keys = {keys}')
        
        # Generate the x-coordinates of each column
        colrange = [512*column/keys for column in range(keys+1)]
        
        # Dictionary List for BPMs
        bpms = []

        # Dictionary List for notes
        notes = []

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

            # Regular Note: col,192,ms,1,0,0:0:0:0:
            # Long Note:    col,192,startms,128,0,endms:0:0:0:0:
            content_split = c.split(',')
            note_colvalue = int(content_split[0])
            for i in range(keys):
                if colrange[i] < note_colvalue <= colrange[i+1]:
                    note_col = i
                    break
            if note_colvalue == 0:
                note_col = 0
            note_ms = int(content_split[2])
            note_LN = True if int(content_split[3])/128 >= 1 else False
            # 132 is LN too, for example (128(LN) + 4(New Combo))
        
            if note_LN:
                note_endms = int(content_split[5].split(':')[0])

                # Copy everything except col as "extra"
                # This includes everything about hitsounds
                # {col, ms, endms, extra}
                notes.append({
                    'col': note_col,
                    'ms': note_ms,
                    'endms': note_endms,
                    'extra': content_split[1:]
                })
        
            else:
                # {col, ms, extra}
                notes.append({
                    'col': note_col,
                    'ms': note_ms,
                    'extra': content_split[1:]
                })
            k += 1
            q.put(f'append to notes ({k}@{note_ms})')

        q.put(f'notes import success')
        
        # Sort by ms
        # https://stackoverflow.com/questions/72899
        notes = sorted(notes, key=lambda k: k['ms'])
    
    except:
        exit('Import failed. The .osu file is invalid.')
    
    randnotes = []
    
    # Dictionary List tracking the end time of occupation
    # {col, endms}
    occtime = []

    # Dictionary List tracking the end time of occupation for the last 1/{snap} snap
    # {col, endms}
    occsnaptime = []
    
    # Random Seed input
    print('Import success.')
    randseed = input('Seed(optional): ')

    # If no seed is given, use current timestamp as the seed
    if randseed == '':
        q.put('no seed given')
        randseed = int(time())
    seed(randseed)
    q.put(f'seed = {randseed}')
    
    # Scatter
    print('Enable Scatter? (minimum jacks) (Y/N)')
    Scatter = True if choose() else False
    q.put(f'Scatter = {Scatter}')

    if Scatter:
        print('16th Beat = 1/4 Snap, 24th Beat = 1/6 Snap, ...')
        while True:
            snap = inputnum('Avoid Jacks "x" and Shorter (default 1/4): 1/', 4)
            if int(snap) == snap:
                snap = int(snap)
                break
            print('Please insert a natural number.')
        q.put(f'snap = {snap}')
    
    # Proportion of switching columns
    while True:
        switch = inputnum('Proportion of Switching Columns(%, default 100): ', 100)
        if switch > 100:
            switch = 100
        if switch <= 0:
            if Scatter:
                switch = 0
                break
            print("What's the point?")
        else:
            break
    q.put(f'switch = {switch}')

    switchnum = int(len(notes) * (switch / 100))
    # Generate switch bool list according to the proportion
    Switch = [False] * len(notes)
    switchindex = list(range(len(notes)))
    shuffle(switchindex)
    for i in switchindex[:switchnum]:
        Switch[i] = True
    
    # Change difficulty & output file name
    for c in content:
        if c.startswith('Version:'):
            # Exclude '\n'
            diffname = c.split(':', 1)[1][:-1]
    
            q.put(f'replaced Version on line {content.index(c)+1}')

            Rand = "Randomized" if not Scatter else "Scattered"
            rand = "rand" if not Scatter else "scat"
            Snaptext = f", No 1/{snap} Jacks" if Scatter else ""
            snaptext = f",{snap}" if Scatter else ""

            content[content.index(c)] = f'Version:{Rand}({switch}%{Snaptext})_{diffname} (Seed:{randseed})\n'
            filename = f'{os.path.dirname(path)}\\{rand}({switch}{snaptext})_{randseed}_{sanitize_filename(diffname)}.osu'
            break
    
    i = 0

    q.put('== Randomization Start ==')
        
    # Int, Boolean List for checking the previous occupation (used for Scatter)
    # Defaults to [False, False, ..., False]
    LastOccupied = keys * [False]
        
    # Tracking LastOccupied's ms
    lastms = 0
    
    # Randomize position of the notes
    for n in notes:
        q.put(f'{i+1}@{n["ms"]}')
        
        # Boolean List for checking if the column is occupied or not
        # Defaults to [False, False, ..., False]
        Occupied = keys * [False]
    
        # Int, Boolean List for checking the previous occupation for the last 1/{snap} snap (used for Scatter)
        # Defaults to [False, False, ..., False]
        LastSnapOccupied = keys * [False]

        # Get current ms per beat
        mpb = -1

        for b in bpms:
            if n['ms'] < b['ms']:
                mpb = bpms[bpms.index(b)-1]['mpb']
                break
        
        if mpb == -1:
            mpb = bpms[-1]['mpb']
            
        # Copy Occupied if Scatter and it's the next notes
        if (i != 0) and Scatter:
            # +5 just in case of unsnapped notes
            if n['ms'] > lastms + 5:
                lastms = n['ms']
                LastOccupied = keys * [False]
                for o in occtime[:]:
                    LastOccupied[o['col']] = True
    
        # If current ms > endms, Unoccupy the column
        # Doing this the first because the program gets stuck often
        # Also occupy the column meanwhile
        for o in occtime[:]:
            if n['ms'] > o['endms']:
                occtime.remove(o)
        for o in occtime[:]:
            Occupied[o['col']] = True

        for o in occsnaptime[:]:
            if n['ms'] > o['endms']:
                occsnaptime.remove(o)
        for o in occsnaptime[:]:
            LastSnapOccupied[o['col']] = True
        
        # If no switch, (and if scatter, if not LastSnapOccupied,) keep the column
        if not Switch[i] and not Occupied[n['col']] and (not Scatter or not LastSnapOccupied[n['col']]):
            randcol = n['col']
        # If switch, Get an unoccupied column
        else:
            # leftcol: not Occupied, possible columns
            # goodcol: not Occupied AND not LastOccupied, desired columns
            # bestcol: not Occupied AND not LastSnapOccupied, most desired columns
            bestcol = []
            goodcol = []
            leftcol = []

            for j in range(keys):
                if not Occupied[j]:
                    leftcol.append(j)
                    if not LastSnapOccupied[j]:
                        bestcol.append(j)
                    if not LastOccupied[j]:
                        goodcol.append(j)

            if len(bestcol) > 0 and Scatter:
                randcol = choice(bestcol)
            
            else:
                if len(goodcol) > 0 and Scatter:
                    randcol = choice(goodcol)
                
                else:
                    if len(leftcol) > 0:
                        randcol = choice(leftcol)
                    
                    else:
                        randcol = randint(0, keys-1)

        occsnaptime.append({
            'col': randcol,
            # Getting the ceil value just in case of an unsnapped note
            'endms': n['ms'] + ceil(mpb / snap) if Scatter else n['ms']
        })
        
        # if LN:
        if 'endms' in n:
            randnotes.append({
                'col': randcol,
                'ms': n['ms'],
                'endms': n['endms'],
                'extra': n['extra']
            })
            occtime.append({
                'col': randcol,
                'endms': n['endms']
            })
        
        # if regular note:
        else:
            randnotes.append({
                'col': randcol,
                'ms': n['ms'],
                'extra': n['extra']
            })
            occtime.append({
                'col': randcol,
                'endms': n['ms']
            })

        i += 1
        
        q.put(f'{randcol} | best={bestcol}, good={goodcol}, left={leftcol}')
    
    q.put(f'exporting to {filename}:')
    with open(filename,'w',encoding='utf-8') as osu:
        col = [int(512*(2*column+1)/(2*keys)) for column in range(keys)]

        for c in content[:objindex+1]:
            osu.write(c)
            q.put(c)
    
        for n in randnotes:
            q.put(','.join(n))
            # if LN:
            if 'endms' in n:
                osu.write(f'{col[n["col"]]},{",".join(n["extra"])}\n')
            
            # if regular note:
            else:
                osu.write(f'{col[n["col"]]},{",".join(n["extra"])}\n')
    
    print(f'\nSuccessfully created {filename}!')
    
    q.put('done')