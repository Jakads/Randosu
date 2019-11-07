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


version = '0.0.0'
date = '2019-11-08'

# Change window title
ctypes.windll.kernel32.SetConsoleTitleW(f'Rand(osu!) v{version}')

# Check if the code's run from .exe
IsEXE = getattr(sys, 'frozen', False)

# If exe, move to the exe's directory
# If py, this is unnecessary as current dir is py's dir by default
if IsEXE:
    os.chdir(os.path.dirname(sys.executable))

print(f'Rand(osu!) v{version}')
print(date)
print(intro() + '\n')

### UPDATING ###
# Add ':' to disallow user to view this message by dragging files
# randosu.exe --:update abc.bat target.osu
if len(sys.argv) > 1 and sys.argv[1] == '--:update':
    if os.path.isfile(sys.argv[2]):
        os.remove(sys.argv[2])
    else:
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
    # Fetching the latest version text from Github
    latest = requests.get('https://github.com/jakads/Randosu/raw/master/version.txt')
    latest.raise_for_status()
    
    if latest.text != version:
        print(f'Update is available! (v{latest.text})')
        print('Would you like to download? (Y/N)')

        if not choose():
            print('Skipping the update.\n')
        
        else:
            print('Downloading . . .')

            # Target .exe
            # stream=True to show progress with tqdm
            exe = requests.get('https://github.com/jakads/Randosu/raw/master/Randosu.exe', stream=True)
            exe.raise_for_status()

            total = int(exe.headers.get('content-length'))
            progress = tqdm(total=total, unit='B', unit_scale=True, unit_divisor=1024, ncols=80)

            filename = os.path.basename(sys.executable)

            # Downloading 8KB chunks
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmppath = tmp.name
                for chunk in exe.iter_content(8192):
                    if chunk:
                        progress.update(8192)
                        tmp.write(chunk)
            
            progress.close()

            # Writing temporary batch file
            with tempfile.NamedTemporaryFile('w', delete=False) as bat:
                batpath = bat.name
                bat.write('\n'.join([
                    '@echo off',
                    'Applying update . . .'

                    # Waiting for potentially unfinished download
                    'timeout /t 1 /nobreak >nul',

                    # Remove original exe
                    # If ran from script, this will have no effect
                    f'del "{filename}"',

                    # Rename the downloaded file then move
                    f'rename "{tmppath}" "{filename}"'
                    f'move /y "{os.path.dirname(tmppath)}\\{filename}" "{filename}"',

                    'cls',
                    # Executing the updated exe
                    f'"{filename}" --:update {batpath}.bat {sys.argv[1] if len(sys.argv)>1 else ""}'
                ]))
                
                # Rename tmp file to make it have .bat extension
                os.rename(batpath, batpath + '.bat')

                sys.exit()

except Exception as e:
    print(f'Connection to GitHub failed: {e}\n')

if len(sys.argv) == 1:
    exit('Open an .osu file with this program (drag the file in) to randomize!')

if len(sys.argv) > 2:
    exit('Please drag in a single file.')

if os.path.splitext(sys.argv[1])[1].lower() != '.osu':
    exit('Please drag in an .osu file.')


### RANDOMIZING ###
try:
    with open(sys.argv[1], encoding='utf-8') as osu:
        content = osu.readlines()
    
    try:
        # 0: Standard, 1: Taiko, 2: CTB, 3: Mania
        gamemode = [int(i.split(':')[1]) for i in content if i.split(':')[0] == 'Mode'][0]
    
    except:
        exit('Import failed. The .osu file is invalid.')
    
    if gamemode == 0:
        print("Mode: standard")
        std.randosu(sys.argv[1], content)
    elif gamemode == 1:
        print("Mode: taiko")
        taiko.randosu(sys.argv[1], content)
    elif gamemode == 2:
        print("Mode: catch")
        catch.randosu(sys.argv[1], content)
    elif gamemode == 3:
        print("Mode: mania")
        mania.randosu(sys.argv[1], content)
    else:
        print("Mode: unknown")
        exit("This is intentional... Right?")

    exit('Press F5 on osu! to try out the result!')

### GENERATING CRASHLOG ###
except Exception as e:
    print(f'\n\n\nFATAL ERROR: {repr(e)}\n')
    traceback.print_exc()
    crashlog = f'CrashLog_{datetime.now().strftime("%Y%m%d%H%M%S")}.log'
    with open(crashlog,mode='w',encoding='utf-8') as c:
        c.write(crash())
        c.write(f'Target File: {sys.argv[1]}\n')
        c.write('If you would like to tell the dev about this issue, please attach the file above with this crash report.\n')
        c.write('DO NOT EDIT ANYTHING WRITTEN HERE.\n\n')
        c.write(traceback.format_exc())
    webbrowser.open('https://github.com/jakads/Randosu/issues')
    print(f'\nThe crash log has been saved as {crashlog}.')
    exit('Please tell the dev about this!')