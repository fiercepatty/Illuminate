# background music testing

# https://www.pygame.org/docs/ref/music.html#pygame.mixer.music.play

import pygame

class Music:
    """ Class for background music and music choice """
    def __init__(self, playlist):
        self.playlist = playlist
        self.playing_music = playlist
        self.volume = 0.5
        self.music_paused = False
        self.in_menu = False

    def start_music(self):
        """ Will start the music (before the game loop)"""
        pygame.mixer.music.load(self.playing_music[0])
        pygame.mixer.music.play()

    def start_music_loop(self):
        """ Plays first playlist file in a loop. JDP """
        pygame.mixer.music.load(self.playing_music[0])
        pygame.mixer.music.play(-1)

    def stop_music(self):
        """ Will stop the music """
        pygame.mixer.music.stop()

    def inc_volume(self):
        """ Will increase volume of music"""
        if self.volume != 1:
            self.volume = self.volume + 0.005
            pygame.mixer.music.set_volume(self.volume)

    def dec_volume(self):
        """ Will decrease volume of music """
        if self.volume != 0:
            self.volume = self.volume - 0.005
            pygame.mixer.music.set_volume(self.volume)

    def pause_music(self):
        """ Will pause the music"""
        if not self.music_paused:
            pygame.mixer.music.pause()
            self.music_paused = True

    def unpause_music(self):
        """ Will unpause the music"""
        if self.music_paused:
            pygame.mixer.music.unpause()
            self.music_paused = False

    def choose_song(self, song_number):
        """ CLets the user choose a song """
        pygame.mixer.music.stop()
        pygame.mixer.music.load(self.playlist[song_number - 1])
        pygame.mixer.music.play()

    def play_music(self, in_menu=False):
        """ Will play the songs in the playlist in loop while the game is playing """
        if not pygame.mixer.music.get_busy() and not in_menu:
            self.playing_music = self.playing_music[1:] + [self.playing_music[0]]
            pygame.mixer.music.load(self.playing_music[0])
            pygame.mixer.music.play()

    def fade_music(self, time=100):
        """ Will fade the music out by the time given (in milliseconds) """
        pygame.mixer.music.fadeout(time)


if __name__ == '__main__':
    import pygame

    pygame.mixer.init()
    pygame.init()

    ds = pygame.display.set_mode((800, 600))

    songs = ["Audio/Music/Battleship.ogg",
             "Audio/Music/Not Giving Up.ogg",
             "Audio/Music/Test Song.ogg"]
    Music = Music(songs)

    fps = pygame.time.Clock()

    menu = False

    Music.start_music()

    running = True
    while running:

        keys = pygame.key.get_pressed()
        pygame.event.pump()

        if keys[pygame.K_p]:
            Music.pause_music()

        if keys[pygame.K_u]:
            Music.unpause_music()

        if keys[pygame.K_ESCAPE]:
            break

        if keys[pygame.K_UP]:
            Music.inc_volume()

        if keys[pygame.K_DOWN]:
            Music.dec_volume()

        if keys[pygame.K_m]:
            # Music.play_music(True)
            Music.stop_music()
            print("menu")
            menu = True

        while menu:
            keys = pygame.key.get_pressed()
            pygame.event.pump()
            if keys[pygame.K_n]:
                menu = False
            if keys[pygame.K_1]:
                Music.choose_song(1)

            if keys[pygame.K_2]:
                Music.choose_song(2)

            if keys[pygame.K_3]:
                Music.choose_song(3)

            if keys[pygame.K_ESCAPE]:
                running = False
                break

        Music.play_music()

        fps.tick(60)

    Music.stop_music()
    pygame.display.quit()
    pygame.quit()
