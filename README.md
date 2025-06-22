# Altered Beast (Arcade) Disassembly and Graphics Tools

Welcome to the Altered Beast (Sega System 16) arcade game disassembly project!  
This repository contains disassembled source code and a suite of Python scripts that analyze and regenerate original game backgrounds and in-game sprites for educational and preservation purposes.

## Introduction

Altered Beast is a classic 1988 arcade game developed by Sega for the System 16B hardware. This project aims to document, analyze, and help others understand how the game’s code and graphics work at a low level.  
All disassembly, code comments, and tooling are provided for **educational and research purposes only**.

## Features

- **A mostly commented 68000 disassembly** of the original game code
- **Python tools** for decoding, analyzing, and regenerating game graphics (backgrounds, sprites, etc.)
- The idea was to understand how and what it took to produce the game, how it stored the maps, and graphics in-game
> **Note:**  
> The Python scripts require access to the original arcade ROM files to function.  
> **No ROMs or copyrighted Sega assets are provided or distributed with this repository.**  
> You must supply your own legally obtained ROMs for data extraction or visualization.

## How to use

Inside this folder is a single batch file (windows only sorry everyone)
make-everything.bat If you run this.
You take a look inside I've added several comments to this, some of the Python scripts have optional parameters.
I'm sure they can be used for other Sega16 titles, just with a little bit of change as a lot of their code is duplicated, for instance, Golden Axe use almost identical code
The only difference would be the ROM locations for the tables.

## Legal & Copyright

- The original game, code, and graphics are copyright © Sega.
- All code, scripts, and commentary in this repository are provided **for non-commercial, educational, and research use only**.
- If you are the copyright holder or represent Sega and wish to request the removal of any material from this repository, please contact me (the maintainer) and I will comply immediately.

## Disclaimer

- This project is provided **as-is** with no warranty, express or implied.
- It is intended for study, academic, and preservation purposes.
- **No commercial use is permitted.**
- The use of Python scripts and tools in this repository requires original ROM files that you must supply.  
  These scripts **do not** include or distribute any copyrighted ROM content.

---

*Happy disassembling!  
For questions, issues, or takedown requests, please open an issue or contact the maintainer directly.*

## Python Requirements

To use the included Python scripts for graphics and data extraction, you’ll need:

- Python 3.x (https://python.org/)
- The following libraries:

```sh
pip install pillow numpy tqdm
```

## Shoutout 
Goes to https://github.com/bbbradsmith/binxelview
Perfect binary tool for looking at data, patterns, and maps even, you can discover a lot here.





