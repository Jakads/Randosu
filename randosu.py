import time
start = time.time() # lol
from src import std, taiko, catch, mania
from msvcrt import getch
import os
import sys
import webbrowser
import requests
import tempfile
import ctypes
import traceback
from datetime import datetime
from tqdm import tqdm
from functions import intro, crash, choose, exit
from multiprocessing import Queue, Process, freeze_support

if __name__ == '__main__':
    # https://github.com/pyinstaller/pyinstaller/wiki/Recipe-Multiprocessing
    # damn..
    freeze_support()

    # Logging time in ms
    t = lambda: f'[{int((time.time() - start) * 1000)}] '
    
    class HelpImStuckException(Exception):
        def __init__(self, line, ms):
            self.line = self.ordinal(line)
            self.ms = ms
    
        def __str__(self):
            return f'stuck while randomizing {self.line} object at {self.ms}ms'
    
        def ordinal(self, num):
            if 11 <= num % 100 <= 13:
                suffix = "th"
    
            else:
                suffix = {
                    1: 'st',
                    2: 'nd',
                    3: 'rd'
                }.get(num % 10, 'th')
    
            return str(num) + suffix
    
    log = []
    
    version = '0.3.1'
    date = '2019-11-16'
    
    # Change window title
    ctypes.windll.kernel32.SetConsoleTitleW(f'Rand(osu!) v{version}')
    
    # Check if the code's run from .exe
    IsEXE = getattr(sys, 'frozen', False)
    
    # If exe, move to the exe's directory
    # If py, this is unnecessary as current dir is py's dir by default
    if IsEXE:
        os.chdir(os.path.dirname(sys.executable))
    
    currentdir = os.getcwd()
    
    print(f'Rand(osu!) v{version}')
    print(date)
    print(intro() + '\n')
    
    ### UPDATING ###
    # Add ':' to disallow user to view this message by dragging files
    # randosu.exe --:update abc.bat target.osu
    if len(sys.argv) > 1 and sys.argv[1] == '--:update':
        try:
            os.remove(sys.argv[2])
        except:
            print(f'Failed to remove the temporary batch file({sys.argv[2]}).')
            print('You are not supposed to see this message normally.')
            print('Please remove the file above manually.\n')
        
        print(f'Successfully updated to v{version}!')
        print('Would you like to check out the changelog? (Y/N)\n')
        if choose():
            webbrowser.open('https://github.com/jakads/Randosu/wiki/Changelog')
        
        # Deleting second element twice actually deletes second and third
        del sys.argv[1], sys.argv[1]
        
    try:
        log.append(t() + 'checking for update')
        # Fetching the latest version text from Github
        latest = requests.get('https://github.com/jakads/Randosu/raw/master/version.txt')
        latest.raise_for_status()
    
        if latest.text == version:
            log.append(t() + 'version = latest = ' + latest.text)
        
        else:
            log.append(t() + f'version = {version}, latest = {latest.text}')
            print(f'Update is available! (v{latest.text})')
            print('Would you like to download? (Y/N)')
    
            if not choose():
                print('Skipping the update.\n')
                log.append(t() + 'Update: No')
            
            else:
                log.append(t() + 'Update: Yes')
                print('Downloading . . .')
    
                # Target .exe
                # stream=True to show progress with tqdm
                exe = requests.get('https://github.com/jakads/Randosu/raw/master/Randosu.exe', stream=True)
                exe.raise_for_status()
    
                total = int(exe.headers.get('content-length'))
                progress = tqdm(total=total, unit='B', unit_scale=True, unit_divisor=1024, ncols=80)
    
                filename = os.path.basename(sys.executable)
    
                b = 0
    
                # Downloading 8KB chunks
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    tmppath = tmp.name
                    for chunk in exe.iter_content(8192):
                        if chunk:
                            progress.update(8192)
                            tmp.write(chunk)
                            b += 8192
                            log.append(t() + f'Download {b}B')
                
                progress.close()
                log.append(t() + 'download complete')
    
                # Writing temporary batch file
                log.append(t() + 'writing batch file')
                with tempfile.NamedTemporaryFile('w', encoding='utf-8', delete=False) as bat:
                    batpath = bat.name
                    bat.write('\n'.join([
                        '@echo off',
    
                        # In case of unicode filenames you need this
                        # Thank you google
                        '@chcp 65001 1> NUL 2> NUL',
    
                        # Remove original exe
                        # If ran from script, this will have no effect
                        f'del "{currentdir}\\{filename}"',
    
                        # Rename the downloaded file then move
                        f'rename "{tmppath}" "{filename}"',
                        f'move /y "{os.path.dirname(tmppath)}\\{filename}" "{currentdir}\\{filename}"',
    
                        'cls',
                        # Executing the updated exe
                        f'"{currentdir}\\{filename}" --:update {batpath}.bat {sys.argv[1] if len(sys.argv)>1 else ""}'
                    ]))
                log.append(t() + 'batch file written')
                    
                # Rename tmp file to make it have .bat extension
                os.rename(batpath, batpath + '.bat')
                log.append(t() + 'executing batch file')
                os.startfile(batpath + '.bat')
                sys.exit()
    
    except Exception as e:
        print(f'Connection to GitHub failed: {e}\n')
        log.append(t() + 'exception while downloading: ' + e)
    
    if len(sys.argv) == 1:
        exit('Open an .osu file with this program (drag the file in) to randomize!')
    
    if len(sys.argv) > 2:
        exit('Please drag in a single file.')
    
    if os.path.splitext(sys.argv[1])[1].lower() != '.osu':
        exit('Please drag in an .osu file.')
    
    
    ### RANDOMIZING ###
    try:
        log.append(t() + 'importing ' + sys.argv[1])
        with open(sys.argv[1], encoding='utf-8') as osu:
            content = osu.readlines()
        
        try:
            # 0: Standard, 1: Taiko, 2: CTB, 3: Mania
            gamemode = [int(i.split(':')[1]) for i in content if i.split(':')[0] == 'Mode'][0]
            log.append(t() + f'gamemode: {gamemode}')
        
        except:
            exit('Import failed. The .osu file is invalid.')
            
        q = Queue()
        target = {0: std.random, 1: taiko.random, 2: catch.random, 3: mania.random}
        mode = {0: "osu!standard", 1: "osu!taiko", 2: "osu!catch", 3: "osu!mania"}
    
        print('Mode: ' + mode.get(gamemode))
        fn = sys.stdin.fileno()
        proc = Process(target=target.get(gamemode), args=(q, fn, sys.argv[1], content))
        # https://stackoverflow.com/questions/7489967
    
        proc.start()
        count = 0
        ignore = 0
        Randomization = False
        objms = 0
        objindex = 0
    
        while True:
            try:
                # If randomization hasn't started yet, just get messages
                if not Randomization:
                    msg = q.get()
                # Once randomization starts, set a time limit of 5 seconds
                else:
                    msg = q.get(timeout=5)
    
                # If message has been sent, append to log list
                if msg != None:
                    log.append(t() + msg)

                    # Get objindex from message
                    if msg.startswith('objindex = '):
                        objindex = int(msg[11:])
    
                    # If message is "== Randomization Start ==", start a time limit
                    if msg == '== Randomization Start ==':
                        Randomization = True

                    # Get current index and 
                    if msg.startswith('@'):
                        objms = int(msg[1:-2])

                    # Get current object index and ms
                    if '@' in msg and Randomization:
                        objindex = int(msg.split('@')[0])
                        objms = int(msg.split('@')[1])
    
                    # If message is "done", break from the loop
                    if msg == "done":
                        proc.terminate()
                        q.close()
                        q.join_thread()
                        break
    
            # If no message has been sent for 5 seconds however...
            except: 
                proc.terminate()
                q.close()
                q.join_thread()
                raise HelpImStuckException(objindex, objms)
    
        exit('Press F5 in osu! to try out the result!')
    
    ### GENERATING CRASHLOG ###
    except Exception as e:
        print(f'\n\n\nFATAL ERROR: {repr(e)}\n')
        traceback.print_exc()
        crashlog = f'CrashLog_{datetime.now().strftime("%Y%m%d%H%M%S")}.log'
        with open(crashlog,mode='w',encoding='utf-8') as c:
            c.write(crash())
            c.write(f'\n\nTarget File: {sys.argv[1]}\n')
            c.write('If you would like to tell the dev about this issue, please attach the file above with this crash report.\n')
            c.write('DO NOT EDIT ANYTHING WRITTEN HERE.\n\n')
            c.write(traceback.format_exc())
            c.write('\n\nFull Log:\n\n')
            c.write('\n'.join(log))
        webbrowser.open('https://github.com/jakads/Randosu/issues')
        print(f'\nThe crashlog has been saved as {crashlog}.')
        exit('Please tell the dev about this!')