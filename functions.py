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
        'Hope you\'re having a great day!',
        'you\'re here yet again to suffer',
        'imagine implementing machine learning into this',
        'Come on in! New map every single time!',
        'no u',
        'python is too slow for this and I kinda regret coding in it',
        'But what is... Random? *VSauce Music Plays*',
        'Now with 1 percent less bug!',
        '''
            According to all known laws
            of aviation,
            
              
            there is no way a bee
            should be able to fly.
            
              
            Its wings are too small to get
            its fat little body off the ground.
            
              
            The bee, of course, flies anyway
            
              
            because bees don't care
            what humans think is impossible.
            
              
            Yellow, black. Yellow, black.
            Yellow, black. Yellow, black.
            
              
            Ooh, black and yellow!
            Let's shake it up a little.
        ''',
        'owo',
        'uwu',
        'ok boomer',
        'I put way too much effort into the crash report',
        '!uso ni sedom lla rof rezimodnaR paM etamitlU ehT',
        'Running out of ideas'
    ]
    introweight = [100] + [5] + [1] * (len(introlist) - 2)
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
        'I am out of words.',
        '''
            According to all known laws
            of aviation,
            
              
            there is no way a bee
            should be able to fly.
            
              
            Its wings are too small to get
            its fat little body off the ground.
            
              
            The bee, of course, flies anyway
            
              
            because bees don't care
            what humans think is impossible.
            
              
            Yellow, black. Yellow, black.
            Yellow, black. Yellow, black.
            
              
            Ooh, black and yellow!
            Let's shake it up a little.
        ''',
        'I\'m not mad... I\'m just disappointed.',
        'You know I have feelings too, right?',
        'This is intentional. I can feel it in my guts. You did this.',
        'eh not a big deal',
        'ok boomer',
        'Well, this is awkward...',
        'AaaaaAAaaaAAAaaAAAAaAAAAA!!!!!'
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