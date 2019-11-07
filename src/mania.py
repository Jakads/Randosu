import os
import sys
from msvcrt import getch
from random import seed, randint, uniform
from time import time
from pathvalidate import sanitize_filename
from functions import choose, inputnum

def randosu(path, content):
    try:
        # CS = Keys
        keys = [int(i.split(':')[1]) for i in content if i.split(':')[0] == 'CircleSize'][0]
        
        # Generate the x-coordinates of each column
        col = [int(512*(2*column+1)/(2*keys)) for column in range(keys)]
        
        # Dictionary List for notes
        notes = []
        
        objindex = content.index('[HitObjects]\n')
        
        # Parse notes from the next row of [HitObjects] to EOF
        for c in content[objindex+1:]:
            # Regular Note: col,192,ms,1,0,0:0:0:0:
            # Long Note:    col,192,startms,128,0,endms:0:0:0:0:
            content_split = c.split(',')
            note_col = col.index(int(content_split[0]))
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
    
    # Tracking LastOccupied's ms
    lastms = 0
    
    # Checking if not placing jacks is impossible
    TotalOccupied = keys * [False]
    Impossible = False
    
    # Dictionary List tracking the end time of occupation
    # {col, endms}
    occtime = []
    
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
    
    # Chance of switching columns
    while True:
        switch = inputnum('chance of switching columns(%, default 100): ', 100)
        if switch > 100:
            switch = 100
        if switch <= 0:
            if Scatter:
                switch = 0
                break
            print("what's the point?")
        else:
            break
    
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
        # Copy Occupied if Scatter and it's the next notes
        if (i != 0) and Scatter:
            if n['ms'] > lastms:
                lastms = n['ms']
                k = 0
                for lo in Occupied:
                    LastOccupied[k] = lo
                    TotalOccupied[k] = lo
                    k += 1
    
        # If current ms > endms, Unoccupy the column
        # Doing this the first because the program gets stuck often
        for o in occtime[:]:
            if n['ms'] > o['endms']:
                occtime.remove(o)
                Occupied[o['col']] = False
        i+=1
        
    
        # If no switch, (and if scatter, if not lastoccupied,) keep the column
        if (uniform(0, 100) > switch) and not Occupied[n['col']] and (not Scatter or not LastOccupied[n['col']]):
            randcol = n['col']
        # If switch, Get an unoccupied column
        else:
            while True:
                randcol = randint(0, keys-1)
                if not Occupied[randcol]:
                    if Scatter:
                        # Checking if not placing jacks is impossible
                        Impossible = True
                        for j in TotalOccupied:
                            if not j:
                                Impossible = False
                        if not LastOccupied[randcol] or Impossible:
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
            
        # Occupy the column
        Occupied[randcol] = True
        TotalOccupied[randcol] = True
    
        
    with open(filename,'w',encoding='utf-8') as osu:
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