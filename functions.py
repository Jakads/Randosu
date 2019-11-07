import sys
from random import choices, shuffle
from msvcrt import getch

def intro():
    a = [c for c in 'The Ultimate Map Randomizer for all modes in osu']
    shuffle(a)
    introlist = [
        'The Ultimate Map Randomizer for all modes in osu!',
        ''.join(a) + '!',
        'random xd',
        'Maps usually become so underrated with this',
        '?',
        'New Mapping Meta 2020',
        'tbh some results actually look good enough to be ranked ngl'
        'hi',
        'yes',
        'epic',
        'The Ultmiate Map Radnomizer for all modes in osu!'
    ]
    introweight = [30] + [10] + [1] * (len(introlist) - 2)
    return choices(introlist, introweight)[0]

def crash():
    crashlist = [
        'Well... Shit.',
        'I saw it coming.',
        'lol rip xd',
        'Wait what?',
        'Get owned, idiot!',
        'The Ultimate Crash Report Generator, Rand(osu!)',
        'Yay... Yet another bug to fix.',
        'Why would you treat me like this?',
        'I hate myself.',
        'When you mix up the pattern too intensely',
        'damn',
        'h'
    ]
    return choices(crashlist)[0]

def choose():
    choice = getch().decode()
    while choice not in 'yYnN':
        choice = getch().decode()
        
    if choice in 'nN':
        return 0
        
    else:
        return 1

def exit(message):
    print(message)
    print('Press any key to exit.')
    getch()
    sys.exit()

def inputnum(message, default):
    while True:
        try:
            i = input(message)
            if i == '':
                i = default
            return float(i)
        except:
            print('Please insert a number.')