import os
import sys
from random import seed, randint, uniform, shuffle
from time import time
from pathvalidate import sanitize_filename
from msvcrt import getch
from functions import choose, inputnum, exit

def random(q, fn, path, content):
    sys.stdin = os.fdopen(fn)
    
    try:
        # Dictionary List for notes
        notes = []
        
        # Dictionary List for other notes (Sliders, Spinners)
        othernotes = []
        
        objindex = content.index('[HitObjects]\n')
        q.put(f'objindex = {objindex}')
        
        # Parse notes from the next row of [HitObjects] to EOF
        k = 0
        kk = 0
        for c in content[objindex+1:]:
            # Ignore comments and blanks
            if c.startswith('//') or c == '\n':
                continue
            
            # Syntax: x, y, extra
            content_split = c.split(',')
            note_ms = int(content_split[2])

        
            # Normal note is either 1 or 5(new combo)
            if int(content_split[3]) % 2 != 1:
                othernotes.append(c)
                k += 1
                q.put(f'append to othernotes ({k}@{note_ms})')
            
            else:
                note_extra1 = content_split[:4]
                note_type = content_split[4]
                note_extra2 = content_split[5:]
                notes.append({
                    'extra1': note_extra1,
                    'type': note_type,
                    'extra2': note_extra2,
                    'ms': note_ms
                })
                kk += 1
                q.put(f'append to notes ({kk}@{note_ms})')

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
        print("Kimagure=20%, Detarame=50%, Abekobe(Mirror)=100%")
        while True:
            switch = inputnum('Proportion of Switching Colors(%, default 50): ', 50)
            if switch > 100:
                switch = 100
            if switch <= 0:
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
            index = content.index(c)
    
            q.put(f'replaced Version on line {content.index(c)+1}')

            rand = f"truerand" if TrueRandom else f"rand({switch})"
            Rand = f"TrueRandomized" if TrueRandom else f"Randomized({switch}%)"
            
            content[index] = f'Version:{Rand}_{diffname} (Seed:{randseed})\n'
            filename = f'{os.path.dirname(path)}\\{rand}_{randseed}_{sanitize_filename(diffname)}.osu'
            break

    i = 0

    q.put('== Randomization Start ==')
    
    # Randomize position of the notes
    for n in notes:
        # Check TrueRandom first to prevent undefined variable
        if TrueRandom or Switch[i]:
            q.put(f'{i+1}@{n["ms"]}')
            # 1: Normal, 2: Whistle, 4: Finish, 8: Clap
            hitsound = format(int(n['type']) + 16, 'b')
            Kat = bool(int(hitsound[1]) or int(hitsound[3]))
            Big = bool(int(hitsound[2]))
            notedict = {
                0: 'd',
                10: 'k',
                1: 'D',
                11: 'K'
            }
            before = notedict.get(Kat * 10 + Big)
    
            if not TrueRandom:
                n['type'] = {
                    #d -> k
                    'd': 2,
                    #k -> d
                    'k': 0,
                    #D -> K
                    'D': 6,
                    #K -> D
                    'K': 4
                }.get(before)

                after = notedict.get((not Kat) * 10 + Big)

            else:
                Kat = randint(0, 1)

                # d=0, k=2, D=4, K=6
                n['type'] = 2 * Kat + 4 * Big

                after = notedict.get(Kat * 10 + Big)
                
            q.put(f'{before} -> {after}')
        
        i += 1
    
    q.put(f'exporting to {filename}:')
    with open(filename,'w',encoding='utf-8') as osu:
        for c in content[:objindex+1]:
            osu.write(c)
            q.put(c)
    
        for n in notes:
            osu.write(f'{",".join(n["extra1"])},{n["type"]},{",".join(n["extra2"])}')
            q.put(','.join(n))
    
        for n in othernotes:
            osu.write(n)
            q.put(n)
    
    print(f'\nSuccessfully created {filename}!')
    
    q.put('done')