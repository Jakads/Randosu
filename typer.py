from msvcrt import getch
import time
import sys
from time import sleep
from colorama import init, Fore, Back, Style
init()
def move (y, x):
    print("\033[%d;%dH" % (y, x))

money = 0
kps = 0

for i in range(20):
    print("#", end="")
    sys.stdout.flush()
    sleep(0.3)

while True:
    move(0,0)
    print(Fore.CYAN + str(money))
    getch()
    money += 1
    print("Aefghuarfgthnkiaern hgjea3rbnigteransbojk")
    sys.stdout.flush()