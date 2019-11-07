import os
import sys
from random import seed, randint, uniform
from time import time
from pathvalidate import sanitize_filename
from msvcrt import getch
from functions import inputnum

def randosu(path, content):
    try:
        # Dictionary List for notes
        notes = []
        
        # Dictionary List for other notes (Sliders, Spinners)
        othernotes = []
        
        objindex = content.index('[HitObjects]\n')
        
        # Parse notes from the next row of [HitObjects] to EOF
        for c in content[objindex+1:]:
            # Syntax: x, y, extra
            content_split = c.split(',')
        
            # Normal note is either 1 or 5(new combo)
            if int(content_split[3]) % 2 != 1:
                othernotes.append(c)
            
            else:
                note_extra1 = content_split[:4]
                note_type = content_split[4]
                note_extra2 = content_split[5:]
                notes.append({
                    'extra1': note_extra1,
                    'type': note_type,
                    'extra2': note_extra2
                })
    
    except:
        exit('Import failed. The .osu file is invalid.')
    
    # Random Seed input
    print('Import success.')
    randseed = input('Seed(optional): ')
    
    # If no seed is given, use current timestamp as the seed
    if randseed == '':
        randseed = int(time())
    seed(randseed)
    
    print("Kimagure=20%, Detarame=50%, Abekobe(Mirror)=100%")
    while True:
        switch = inputnum('Chance of Switching Colors(%, default 50): ', 50)
        if switch > 100:
            switch = 100
        if switch <= 0:
            print("What's the point?")
        else:
            break
    
    # Change difficulty & output file name
    for c in content:
        if c.startswith('Version:'):
            # Exclude '\n'
            diffname = c.split(':', 1)[1][:-1]
            index = content.index(c)
            
            content[index] = f'Version:Randomized({switch}%)_{diffname} (Seed:{randseed})\n'
            filename = f'{os.path.dirname(path)}\\rand({switch})_{randseed}_{sanitize_filename(diffname)}.osu'
    
    # Randomize position of the notes
    for n in notes:
        if uniform(0, 100) < switch:
            # 1: Normal, 2: Whistle, 4: Finish, 8: Clap
            hitsound = format(int(n["type"]) + 16, 'b')
            Kat = int(hitsound[1]) or int(hitsound[3])
            Big = int(hitsound[2])
    
            n["type"] = {
                #d -> k
                0: 2,
                #k -> d
                10: 0,
                #D -> K
                1: 6,
                #K -> D
                11: 4
            }.get(Kat * 10 + Big)
    
    with open(filename,'w',encoding='utf-8') as osu:
        for c in content[:objindex+1]:
            osu.write(c)
    
        for n in notes:
            osu.write(f'{",".join(n["extra1"])},{n["type"]},{",".join(n["extra2"])}')
    
        for n in othernotes:
            osu.write(n)
    
    print(f'\nSuccessfully created {filename}!')