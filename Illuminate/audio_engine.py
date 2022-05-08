# Jamie Pospishil
# Version 3.3
# 2019-04-08
# Audio Engine split from SFX Class

import pygame
import audio_sfx_player
from audio_sfx_player import SFX
import audio_music_player
from audio_music_player import Music

# Put Folder Paths here to test sounds
AllFolderPaths = ['Audio/Music', 'Audio/SFX/Player']
AllFileExtensions = ['.wav', '.mp3', '.ogg', '.xm', '.mod']
# Player
PlayerFolder = ["Audio/SFX/Player"]
PlayerExt = ['.wav']
# .ogg playback is weird on my machine, not sure if it's on my end or a pygame thing
# .mp3 might crash Linux
# .xm is untested
# .mod is untested

frequency = 48000
size = -16  # negative means unsigned
channels = 2  # stereo is 2
buffer = 1024


def initialize_audio_engine(m_frequency=frequency, m_size=size, m_channels=channels, m_buffer=buffer,
                            m_mixer_channels=SFX.mixer_channels,
                            m_reserved_channels=SFX.number_of_reserved_sound_channels):
    """
    Initializes Pygame, a Mixer, and sets the number of sound channels. This should be safe to call multiple times, but only needs to be called once.

    Parameters:
    :param m_frequency: Used for Mixer initialization. An integer. Usually something like 22050, 44100, or 48000
    :param m_size: Used for Mixer initialization. An integer (negative means unsigned). Usually something like -16 or -24
    :param m_channels: Used for Mixer initialization. The number of playback channels. Usually 2 for stereo.
    :param m_buffer: Used for Mixer initialization. A power of 2. Lower means less latency, higher means more stable. Usually something like 4096 or 512
    :param m_mixer_channels: Used to set the number of sound channels available for sound playback.
    :param m_reserved_channels: Used to reserve sound channels.
    Return:
    :return: None
    """
    pygame.mixer.pre_init(frequency=m_frequency, size=m_size, channels=m_channels, buffer=m_buffer)
    pygame.init()
    pygame.mixer.quit()
    pygame.mixer.init(frequency=m_frequency, size=m_size, channels=m_channels, buffer=m_buffer)
    pygame.mixer.set_num_channels(m_mixer_channels)
    pygame.mixer.set_reserved(m_reserved_channels)
