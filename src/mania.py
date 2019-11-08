import os
import sys
from msvcrt import getch
from random import seed, randint, uniform, shuffle, choice
from time import time
from pathvalidate import sanitize_filename
from functions import choose, inputnum, exit
from math import ceil

def randosu(path, content):
    try:
        # CS = Keys
        keys = [int(i.split(':')[1]) for i in content if i.split(':')[0] == 'CircleSize'][0]
        
        # Generate the x-coordinates of each column
        colrange = [512*column/keys for column in range(keys+1)]
        
        # Dictionary List for BPMs
        bpms = []

        # Dictionary List for notes
        notes = []

        bpmindex = content.index('[TimingPoints]\n')
        
        objindex = content.index('[HitObjects]\n')

        # Parse BPMs from the next row of [TimingPoints] to [HitObjects]
        for c in content[bpmindex+1:objindex]:
            # BPM Points: ms,60000/BPM,[],[],[],[],1,[]
            # 60000/BPM = ms per beat
            content_split = c.split(',')
            if content_split[6] == '1':
                bpms.append({
                    # {ms, mpb}
                    'ms': content_split[0],
                    'mpb': float(content_split[1])
                })

        # Parse notes from the next row of [HitObjects] to EOF
        for c in content[objindex+1:]:
            # Regular Note: col,192,ms,1,0,0:0:0:0:
            # Long Note:    col,192,startms,128,0,endms:0:0:0:0:
            content_split = c.split(',')
            note_colvalue = int(content_split[0])
            print(note_colvalue, end=' ')
            for i in range(keys):
                if colrange[i] < note_colvalue <= colrange[i+1]:
                    note_col = i
                    print(note_col)
                    break
            if note_colvalue == 0:
                note_col = 0
            note_ms = int(content_split[2])
            note_LN = True if int(content_split[3])/128 >= 1 else False
            # 132 is LN too, for example (128(LN) + 4(New Combo))
        
            if note_LN:
                note_endms = int(content_split[5].split(':')[0])
        
                # {col, ms, endms}
                notes.append({
                    'col': note_col,
                    'ms': note_ms,
                    'endms': note_endms
                })
        
            else:
                # {col, ms}
                notes.append({
                    'col': note_col,
                    'ms': note_ms
                })
        
        # Sort by ms
        # https://stackoverflow.com/questions/72899
        notes = sorted(notes, key=lambda k: k['ms'])
    
    except:
        exit('Import failed. The .osu file is invalid.')
    
    randnotes = []
    
    # Boolean List for checking if the column is occupied or not
    # Defaults to [False, False, ..., False]
    Occupied = keys * [False]
    
    # Int, Boolean List for checking the previous occupation (used for Scatter)
    # Defaults to [False, False, ..., False]
    LastOccupied = keys * [False]

    # Int, Boolean List for checking the previous occupation for the last 16th beat (used for Scatter)
    # Defaults to [False, False, ..., False]
    Last16Occupied = keys * [False]
    
    # Tracking LastOccupied's ms
    lastms = 0
    
    # Checking if not placing jacks is impossible
    Impossible = False
    
    # Dictionary List tracking the end time of occupation
    # {col, endms}
    occtime = []

    # Dictionary List tracking the end time of occupation for the last 16th beat
    # {col, endms}
    occ16time = []
    
    # Random Seed input
    print('Import success.')
    randseed = input('Seed(optional): ')

    # If no seed is given, use current timestamp as the seed
    if randseed == '':
        randseed = int(time())
    seed(randseed)
    
    # Scatter
    print('Enable Scatter? (minimum jacks) (Y/N)')
    Scatter = True if choose() else False
    
    # Proportion of switching columns
    while True:
        switch = inputnum('Proportion of Switching Columns(%, default 100): ', 100)
        if switch > 100:
            switch = 100
        if switch <= 0:
            if Scatter:
                switch = 0
                break
            print("what's the point?")
        else:
            break

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
    
            Rand = "Randomized" if not Scatter else "Scattered"
            rand = "rand" if not Scatter else "scat"

            content[content.index(c)] = f'Version:{Rand}({switch}%)_{diffname} (Seed:{randseed})\n'
            filename = f'{os.path.dirname(path)}\\{rand}({switch})_{randseed}_{sanitize_filename(diffname)}.osu'
    
    i=0
    
    # Randomize position of the notes
    for n in notes:
        # Get current ms per beat
        mpb = -1

        for b in bpms:
            if n['ms'] < b['ms']:
                mpb = bpms[bpms.index(b)-1]['mpb']
        
        if mpb == -1:
            mpb = bpms[-1]['mpb']
            
        # Copy Occupied if Scatter and it's the next notes
        if (i != 0) and Scatter:
            if n['ms'] > lastms:
                lastms = n['ms']
                k = 0
                for lo in Occupied:
                    LastOccupied[k] = lo
                    k += 1
    
        # If current ms > endms, Unoccupy the column
        # Doing this the first because the program gets stuck often
        for o in occtime[:]:
            if n['ms'] > o['endms']:
                occtime.remove(o)
                Occupied[o['col']] = False

        for o in occ16time[:]:
            if n['ms'] > o['endms']:
                occ16time.remove(o)
                Last16Occupied[o['col']] = False
        
        # If no switch, (and if scatter, if not last16occupied,) keep the column
        if not Switch[i] and not Occupied[n['col']] and (not Scatter or not Last16Occupied[n['col']]):
            randcol = n['col']
        # If switch, Get an unoccupied column
        else:
            while True:
                randcol = randint(0, keys-1)
                if not Occupied[randcol]:
                    if Scatter:
                        if not Last16Occupied[randcol]:
                            break

                        # Checking if ignoring 16th jack is impossible
                        # Keep Impossible True if all Occupied and Last16Occupied is True
                        Impossible = True
                        for j in range(keys):
                            if not Occupied[j] or not Last16Occupied[j]:
                                Impossible = False

                        # If it is not impossible, just try again
                        # If impossible however, prioritize not LastOccupied column
                        if Impossible:
                            # Check if every column is LastOccupied (e.g. Chords with all keys)
                            # leftcol: not Occupied, possible columns
                            # goodcol: not Occupied AND not LastOccupied, desired columns
                            leftcol = []
                            goodcol = []
                            for j in range(keys):
                                if not Occupied[j]:
                                    leftcol.append(j)
                                    if not LastOccupied[j]:
                                        goodcol.append(j)
                                        Impossible = False

                            if not Impossible:
                                randcol = choice(goodcol)
                            
                            else:
                                randcol = choice(leftcol)
                            
                            break
                    else:
                        break
        
        # if LN:
        if 'endms' in n:
            randnotes.append({
                'col': randcol,
                'ms': n['ms'],
                'endms': n['endms']
            })
            occtime.append({
                'col': randcol,
                'endms': n['endms']
            })
            occ16time.append({
                'col': randcol,
                # Getting the ceil value just in case
                'endms': n['endms'] + ceil(mpb / 4)
            })
        
        # if regular note:
        else:
            randnotes.append({
                'col': randcol,
                'ms': n['ms']
            })
            occtime.append({
                'col': randcol,
                'endms': n['ms']
            })
            occ16time.append({
                'col': randcol,
                # Getting the ceil value just in case
                'endms': n['ms'] + ceil(mpb / 4)
            })
            
        # Occupy the column
        Occupied[randcol] = True
        Last16Occupied[randcol] = True

        i += 1
    
        
    with open(filename,'w',encoding='utf-8') as osu:
        col = [int(512*(2*column+1)/(2*keys)) for column in range(keys)]

        for c in content[:objindex+1]:
            osu.write(c)
    
        for n in randnotes:
            # if LN:
            if 'endms' in n:
                osu.write(f'{col[n["col"]]},192,{n["ms"]},128,0,{n["endms"]}\n')
            
            # if regular note:
            else:
                osu.write(f'{col[n["col"]]},192,{n["ms"]},1,0\n')
    
    print(f'\nSuccessfully created {filename}!')