from source.PenguinJump.game import Game1
from os import path
import pygame


def maincast():
    g = Game1()
    # Load music
    pygame.mixer.music.load(path.join(g.sound_dir, "little march.ogg"))
    pygame.mixer.music.set_volume(.7)
    pygame.mixer.music.play(-1)

    g.logo_screen()
    while g.running:

        g.start_screen()  # Show the start screen
        g.play_again = True
        if not g.running:
            break
        elif g.select_cursor.selected == "OPTIONS":
            g.options_menu()
        else:
            while g.play_again and g.running:
                g.reset()
                g.gameover()
                # Reset title music
                pygame.mixer.music.set_volume(g.volume_mult)
                pygame.mixer.music.load(path.join(g.sound_dir, "little march.ogg"))
                pygame.mixer.music.play(-1)

    pygame.mixer.quit()
    
