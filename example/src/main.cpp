/*
 * Copyright (c) 2020-2026 Gustavo Valiente gustavo.valiente@protonmail.com
 * zlib License, see LICENSE file.
 */

#include "bn_core.h"
#include "bn_math.h"
#include "bn_keypad.h"
#include "bn_display.h"
#include "bn_sprite_ptr.h"
#include "bn_bg_palettes.h"
#include "bn_sprite_text_generator.h"

#include "fonts/happy_16x16_font.hpp"
#include "fonts/kindergarden_32x32_font.hpp"

namespace
{
    constexpr bn::fixed text_y_inc = 32;
    constexpr bn::fixed text_y_limit = (bn::display::height() / 2) - text_y_inc;

        void happy_text_scene()
        {
            bn::sprite_text_generator text_generator(fonts::happy_16x16_sprite_font);
            text_generator.set_center_alignment();

            bn::vector<bn::sprite_ptr, 32> text_sprites;
            text_generator.generate(0, -text_y_limit, "Happy", text_sprites);
            text_generator.generate(0, text_y_limit, "PRESS START", text_sprites);

            while(! bn::keypad::start_pressed())
            {
                bn::core::update();
            }
        }

            void kindergarden_text_scene()
            {
                bn::sprite_text_generator text_generator(fonts::kindergarden_32x32_sprite_font);
                text_generator.set_center_alignment();

                bn::vector<bn::sprite_ptr, 32> text_sprites;
                text_generator.generate(0, -text_y_limit, "Kindergarden", text_sprites);
                text_generator.generate(0, text_y_limit, "PRESS START", text_sprites);

                while(! bn::keypad::start_pressed())
                {
                    bn::core::update();
                }
            }
}

int main()
{
    bn::core::init();

    bn::bg_palettes::set_transparent_color(bn::color(16, 16, 16));

    while(true)
    {
        happy_text_scene();
        bn::core::update();

        kindergarden_text_scene();
        bn::core::update();
    }
}
