# Butano Extension Scripts

Scripts to enhance Butano, but don't necessarily fit within the Butano framework's repo

I am making a 15-30 hour game for the GBA using Butano, and since we have been building this project since late-2023, I have many scripts, tools, and pipelines I've built for our game. I am here to share these scripts to hopefully help reduce your dev and asset creation time.

In this repository there are currently scripts for:

- [Font Asset Generation](#font-assets)
  - Creates a Butano compatible font
  - Supports:
    - 'Construct 3' font spritesheets

## Preface

I will be assuming you have an existing Butano project with the typical directory structure:

```
my-butano-game/
├─ audio/
│  ├─ example.it
├─ dmg_audio/
│  ├─ example.s3m
├─ graphics/
│  ├─ example.bmp
│  ├─ example.json
├─ include/
│  ├─ example.hpp
├─ src/
│  ├─ example.cpp
```

Add this repo to your project by `cd`ing into the project and using Git Submodule:

```bash
git submodule add https://github.com/breadbored/butano-ext-scripts.git ext-scripts
```

This will add a subdirectory to your project

```
my-butano-game/
├─ ext-scripts/
│  ├─ README.md # this README
```

If you are cloning the repo as a fresh directory, or you are collaborating with other people who don't have the submodule pulled yet, you will need to run the following after a fresh clone/pull:

```bash
git submodule update --init --recursive
```

This will pull all the submodules so that you may use them.

Install the required packages with

```bash
pip install -r ext-scripts/requirements.txt
```

Confirm that you have the submodule by running this:

```bash
python ext-scripts/confirm.py
```

## Font Assets

[Please read the Preface before continuing!](#preface)

Now that you have added the repo as a submodule, let's create a new directory called `fonts/`

```
my-butano-game/
├─ fonts/
```

Add the following lines to your Makefile at the bottom of the other variables:

```Makefile
EXTTOOL     :=  $(MAKE) fonts
EXTSCRIPTS  :=  ext-scripts
EXTFONTS    :=  fonts

ifndef EXTSCRIPTSABS
	export EXTSCRIPTSABS	:=	$(realpath $(EXTSCRIPTS))
endif

include $(EXTSCRIPTSABS)/fonts.mak
```

Add the following line to the bottom of your Makefile

```Makefile
include $(EXTSCRIPTSABS)/commands.mak
```

Your Makefile should look something like this:

```Makefile
TARGET      :=  my-butano-game
BUILD       :=  build
# [...]
EXTTOOL     :=  $(MAKE) fonts
EXTSCRIPTS  :=  ext-scripts
EXTFONTS    :=  fonts

ifndef EXTSCRIPTSABS
	export EXTSCRIPTSABS	:=	$(realpath $(EXTSCRIPTS))
endif

include $(EXTSCRIPTSABS)/fonts.mak

ifndef LIBBUTANOABS
	export LIBBUTANOABS	:=	$(realpath $(LIBBUTANO))
endif

include $(LIBBUTANOABS)/butano.mak

include $(EXTSCRIPTSABS)/commands.mak
```

You can put Construct 3 compatible fonts ([such as this GREAT collection of pixel art fonts](https://itch.io/s/158296/40-pixel-fonts-for-40-dollars-thats-it-thats-the-sale)) into this directory using the following structure (where `arthur` is an example font name):

```
my-butano-game/
├─ fonts/
│  ├─ arthur/
│  │  ├─ arthur.png # the spritesheet of the font
│  │  ├─ arthur.txt # the Construct 3 definition file
```

Now, when you run `make`, it will build the font as an asset that you can use like any other font with

```cpp
#include "fonts/arthur_8x8_font.hpp"
```

## TODO:

- [x] Font generator
- [ ] PNG graphics support
- [ ] WAV compressor / resampler
- [ ] Aseprite extension for GBA indexed BMP export
- [ ] Github Actions pipeline

If any of these tools would be immediately helpful for you, please open an Issue and I will prioritize preparing the code and the guide for integrating in your project
