from src import std, taiko, catch, mania
import os
import sys

with open(sys.argv[1],encoding='utf-8') as osu:
    content = osu.readlines()

# 0: Standard, 1: Taiko, 2: CTB, 3: Mania
gamemode = [int(i.split(':')[1]) for i in content if i.split(':')[0] == 'Mode'][0]

if gamemode == 0:
    print("mode: standard")
    std.randosu(sys.argv[1], content)
elif gamemode == 1:
    print("mode: taiko")
    taiko.randosu(sys.argv[1], content)
elif gamemode == 2:
    print("mode: catch")
    catch.randosu(sys.argv[1], content)
elif gamemode == 3:
    print("mode: mania")
    mania.randosu(sys.argv[1], content)