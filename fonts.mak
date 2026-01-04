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
FONT_GRAPHICS := graphics/fonts
FONT_INCLUDES := include/fonts
GRAPHICS := $(FONT_GRAPHICS) $(GRAPHICS)
INCLUDES := $(FONT_INCLUDES) $(INCLUDES)
