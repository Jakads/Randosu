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
        'tbh some results actually look good enough to be ranked ngl',
        'hi',
        'yes',
        'epic',
        'More visual layouts coming soon:tm:',
        'Unrelated to Randoseru, I swear',
        'Selecting from osu!client feature when?',
        'It might not seem random, but it is as random as it can be (Gambler\'s Fallacy)',
        'The Ultimate Map Shittifier for all modes in osu!',
        'Results are only for your viewing pleasure',
        'I am not responsible for any shockingly shitty patterns this might generate',
        'I am desperately looking for help in some upcoming features, please contact me if you are interested',
        'I should have coded this in a different language lol',
        'real gamer moment',
        'Aren\'t you getting tired of this boring white text on a boring black screen?',
        'delet this',
        'Hope you\'re having a great day!'
    ]
    introweight = [50] + [5] + [1] * (len(introlist) - 2)
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
        'h',
        'the fuck',
        'I told you to not do this...',
        'I knew this was a bad idea...',
        'This must be just a bad dream.',
        'am i retarded',
        'bruh',
        'ew this map sucks, that\'s why i crashed',
        'bruh moment',
        'I am out of words.'
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