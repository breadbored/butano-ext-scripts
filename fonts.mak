ifeq ($(strip $(PYTHON)),)
$(error "PYTHON not found")
endif
ifeq ($(strip $(BUILD)),)
$(error "BUILD not found")
endif
ifeq ($(strip $(EXTFONTS)),)
$(error "EXTFONTS not found")
endif

EXTSCRIPTS_DIR := $(dir $(lastword $(MAKEFILE_LIST)))
FONT_GRAPHICS := $(BUILD)/fonts/graphics
FONT_INCLUDES := $(BUILD)/fonts/include
GRAPHICS += $(FONT_GRAPHICS)
INCLUDES += $(FONT_INCLUDES)

all: convert

convert:
	@mkdir -p $(FONT_GRAPHICS) $(FONT_INCLUDES)
	@$(PYTHON) $(EXTSCRIPTS_DIR)fonts.py "$(EXTFONTS)" "$(FONT_GRAPHICS)" "$(FONT_INCLUDES)"
