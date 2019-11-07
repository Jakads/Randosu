# Rand(osu!)

Randomizes patterns in any maps. Supports all modes.\
Written in Python 3.7\
Tested only in Windows, normal functionality on the other OS's not guaranteed.

## How to use

Drag an .osu file into randosu.py / randosu.exe and follow the instructions.

## How to use like a ***GAMER***

1. **osu!taiko Mirror Mod**\
Set *Chance of Switching Colors* to **100%** and you'll have a "Mirror" mode in Taiko.
2. **I Despise Jacks in osu!mania**\
**Enable** *Scatter* and set *Chance of Switching Columns* to **0%** to keep the original pattern AND replace as many jacks as possible.
3. **Auto-map**\
Place notes randomly on the screen but on the beat, and then run this program! :D

## Arguments

### **Seed**

*Default: Current Timestamp*\
Seed is used to initialize a random number generator. That means the same seed will create the same .osu file if used with the same arguments.\
If left blank, Rand(osu!) will use the current timestamp (current time in seconds counting from 1970-01-01 00:00:00) as the seed.

### osu!standard & osu!catch

* **True Random**
  * *Recommended: Off*
  * Rand(osu!) uses original map as a reference so that it won't create an absolute mess. Details are written below.
  * This option will ignore all that and create a truly chaotic masterpiece.

* **Min Scale Factor & Max Scale Factor**
  * *Default: 0.8x ~ 1.5x*
  * Rand(osu!) calculates the distance between the objects as a reference, multiplies a random number to it, and then use the result to place the next object.
  * These arguments will specify the random number's range.

* **Chance of Red Anchors**
  * *Default: 25%*
  * Rand(osu!) will first read all the slider curve points as normal anchors. It will then change some of the points to a red one, which will add to the chaos.
  * This argument specifies the chance of changing a curve point into a red one.

### osu!taiko

* **Chance of Switching Colors**
  * *Default: 50%*
  * Rand(osu!) will keep the size of all notes and only change the color of some.
  * This argument controls the chance of changing given note's color.
  * In official taiko games, the chances are:
    * Abekobe(あべこべ): 100%
    * Detarame(でたらめ): 50%
    * Kimagure(きまぐれ): 20%

### osu!mania

* **Scatter**
  * *Recommended: On*
  * In Lunatic Rave 2, there's a special option called Scatter, which is just like S-Random, except it avoids jacks at all costs.
  * This works the exact same in Rand(osu!). It will avoid the stupid jacks anywhere possible.
  * Bare in mind that all the arcade games supporting S-Random does not support this.

* **Chance of Switching Columns**
  * *Default: 100%*
  * Rand(osu!) will displace notes to other available columns.
  * This argument specifies the chance of changing the column of a given note.

## Result File Names / Difficulty Names

Randomized .osu files will be created right where your original .osu file is. Here's what the names of the generated files mean.

* **osu!standard & osu!catch**
  * True Random Off
    * Difficulty name: Randomized(*Min Scale Factor*~*Max Scale Factor*, Red:*Chance of Red Anchors*)\_*Seed*_*Original Difficulty Name*
    * File name: rand(*Min Scale Factor*~*Max Scale Factor*,*Chance of Red Anchors*)\_*Seed*_*Original Difficulty Name*.osu
  * True Random On
    * Difficulty name: TrueRandomized(Red:*Chance of Red Anchors*)\_*Seed*_*Original Difficulty Name*
    * File name: truerand(*Chance of Red Anchors*)\_*Seed*_*Original Difficulty Name*.osu
* **osu!taiko**
  * Difficulty name: Randomized(*Chance of Switching Colors*%)\_*Seed*_*Original Difficulty Name*
  * File name: rand(*Chance of Switching Colors*)\_*Seed*_*Original Difficulty Name*.osu
* **osu!mania**
  * Scatter Off
    * Difficulty name: Randomized(*Chance of Switching Columns*%)\_*Seed*_*Original Difficulty Name*
    * File name: rand(*Chance of Switching Columns*)\_*Seed*_*Original Difficulty Name*.osu
  * Scatter On
    * Difficulty name: Scattered(*Chance of Switching Columns*%)\_*Seed*_*Original Difficulty Name*
    * File name: scat(*Chance of Switching Columns*)\_*Seed*_*Original Difficulty Name*.osu

## TODO

* Borrow some elements from Malody2osu
  * Auto-update - will release .exe of Rand(osu!) once this is complete
  * Crashlog
