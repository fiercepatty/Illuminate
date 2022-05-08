# Jamie Pospishil
# Version 3.6
# 2019-04-08

import pygame
import glob
import os

debug = False


class SFX:
    mixer_channels = 16
    # starting with 16 for mixer_channels, this can be increased if we need to
    number_of_reserved_sound_channels = 2
    # channels 0 - 1 are reserved for possible future use

    # channels_used will hold onto what channels each instance is using
    channels_used = []
    # adds reserved channels to used list
    for i in range(number_of_reserved_sound_channels):
        channels_used.append(i)

    last_channel_used = -1

    def __init__(self, folder_path, file_ext):
        self.sound_play_info = []
        self.sound_file_name = []
        self.sound_channel = []
        self.last_local_used = -1
        self.channels_used = []
        if debug == True:
            self.blep = []
        # self.sound_dictionary = {}
        for ext in range(len(file_ext)):
            for path in range(len(folder_path)):
                self.load_folder(folder_path[path], file_ext[ext])

    def __del__(self):
        for i in self.channels_used:
            SFX.channels_used.remove(i)

    def play(self, sound_passed):
        # if self.sound_file_name.__contains__(soundPassed):
        sound_index = self.sound_file_name.index(sound_passed)
        sound = self.sound_play_info[sound_index]
        if isinstance(sound, pygame.mixer.Sound):
            if debug == True:
                print("Channel", self.blep[sound_index], self.sound_file_name[sound_index],
                      self.sound_play_info[sound_index], self.sound_channel[sound_index])
            self.sound_channel[sound_index].play(sound)
        else:
            pygame.mixer.music.load(sound)
            pygame.mixer.music.play(0)

    # def play_test(self, sound_passed):
    #   sound_to_play = self.sound_dictionary_list[sound_passed]
    #  sound_to_play["channel"].play(sound_to_play["play_info"])

    def setVolume(self, sound_passed, value):
        sound_channel = self.sound_channel[self.sound_file_name.index(sound_passed)]
        if debug:
            print("volume of ", sound_passed, " is ", sound_channel.get_volume())
        sound_channel.set_volume(value)
        if debug:
            print("volume of ", sound_passed, " is ", sound_channel.get_volume())

    def playIfNotBusy(self, sound_passed):
        # if self.sound_file_name.__contains__(soundPassed):
        sound_index = self.sound_file_name.index(sound_passed)
        if not self.sound_channel[sound_index].get_busy():
            sound = self.sound_play_info[sound_index]
            if isinstance(sound, pygame.mixer.Sound):
                if debug == True:
                    print("Channel", self.blep[sound_index], self.sound_file_name[sound_index],
                          self.sound_play_info[sound_index], self.sound_channel[sound_index])
                self.sound_channel[sound_index].play(sound)
            else:
                pygame.mixer.music.load(sound)
                pygame.mixer.music.play(0)

    @staticmethod
    def stop_music():
        """
        Stops playback of the music track. Will not error if there is not a music track.
        :return: None
        """
        pygame.mixer.music.stop()

    @staticmethod
    def stop_sound(sound):
        """
        Stops playback of the specified sound. Will not error if passed an incorrect object.
        If you want to stop ALL sound, call this and stop_music().
        :param sound: The pygame.mixer.Sound object to stop.
        :return: None.
        """
        if isinstance(sound, pygame.mixer.Sound):
            pygame.mixer.Sound.stop(sound)

    def load_folder(self, folder_path, extension):
        """
        Takes all the files from the specified path (folder), does pygame.mixer.Sound(file) on them,
        and then puts them into a list.
        :param folder_path: The relative path of the folder.
        Ex. 'SFX'
        Ex. "SFX/Character"
        :param extension: A file extension. Pygame works best with .wav files.
        By default, this is .wav
        Ex. '.wav'
        :return: A list of Pygame sounds.
        Ex. SFX = loadSoundFolder('SFX', '.wav')
        """
        # https://stackoverflow.com/questions/18262293/how-to-open-every-file-in-a-folder/18262324#18262324

        for filename in glob.glob(os.path.join(folder_path, "*" + extension)):
            path_len = len(folder_path)
            # file_len = len(filename) - path_len - len(extension)
            file_len = len(filename) - path_len
            prefix_len = 0  # remove 001_filename ?
            if extension == ".wav" or extension == ".ogg":
                if "Music" in folder_path:
                    append_str = filename[path_len + 1:(path_len + file_len)]
                    self.sound_file_name.append(append_str)
                    self.sound_play_info.append(filename)
                    self.sound_channel.append(-2)
                    if debug == True:
                        self.blep.append(-2)

                    sound_dictionary = {
                        "type": "Music",
                        "filename": append_str,
                        "play_info": filename
                    }
                    # self.sound_dictionary_list.append(sound_dictionary)
                else:
                    local_channel = int(filename[path_len + 1:path_len + 4], 10)
                    append_str = filename[path_len + 1 + prefix_len:(path_len + file_len)]
                    self.sound_file_name.append(append_str)
                    self.sound_play_info.append(pygame.mixer.Sound(filename))

                    if self.last_local_used == -1:
                        self.last_local_used = local_channel
                        done = False
                        i = SFX.number_of_reserved_sound_channels
                        while not done:
                            if i == SFX.mixer_channels:
                                SFX.mixer_channels *= 2
                                pygame.mixer.set_num_channels(SFX.mixer_channels)
                            if i not in SFX.channels_used:
                                if debug == True:
                                    self.blep.append(i)
                                self.sound_channel.append(pygame.mixer.Channel(i))
                                SFX.channels_used.append(i)
                                self.channels_used.append(i)
                                SFX.last_channel_used = i
                                done = True
                            i += 1

                    elif self.last_local_used == local_channel:
                        self.sound_channel.append(pygame.mixer.Channel(SFX.last_channel_used))
                        if debug == True:
                            self.blep.append(SFX.last_channel_used)

                    else:
                        self.last_local_used = local_channel
                        done = False
                        i = SFX.number_of_reserved_sound_channels
                        while not done:
                            if i == SFX.mixer_channels:
                                SFX.mixer_channels *= 2
                                pygame.mixer.set_num_channels(SFX.mixer_channels)
                            if i not in SFX.channels_used:
                                if debug == True:
                                    self.blep.append(i)
                                self.sound_channel.append(pygame.mixer.Channel(i))
                                SFX.channels_used.append(i)
                                self.channels_used.append(i)
                                SFX.last_channel_used = i
                                done = True
                            i += 1

                    # sound_dictionary[]
            #            sound_dictionary = {
            #               "filename": append_str,
            #              "type": "SFX",
            #             "play_info": filename,
            #            "channel": pygame.mixer.Channel(append_channel)
            #       }
            # self.sound_dictionary_list.append(sound_dictionary)
            elif extension == '.mp3' or extension == ".xm" or extension == ".mod":
                append_str = filename[path_len + 1:(path_len + file_len)]
                self.sound_file_name.append(append_str)
                self.sound_play_info.append(filename)
                self.sound_channel.append(-3)
                self.blep.append(-3)
                sound_dictionary = {
                    "type": "SFX_M",
                    "filename": append_str,
                    "play_info": filename,
                }
                # self.sound_dictionary_list.append(sound_dictionary)

    def load_filenames(self, folder_path, extension):
        """
        Takes all the files from the specified path (folder) and puts their filenames into a list.
        :param folder_path: The file path.
        Ex. "SFX"
        Ex. 'SFX/Character'
        Ex. 'SFX\\Character' # If you want to use backslashes, you have to use 2 because it's an escape character.
        :param extension: A file extension.
        Ex. ".wav"
        :return: A list of strings. The path will precede the filename in brackets.
        Ex. SFX = loadSoundFolder("SFX/Character", ".wav")
        print(SFX[0])   # [SFX] filename.wav
        """
        # https://stackoverflow.com/questions/18262293/how-to-open-every-file-in-a-folder/18262324#18262324
        for filename in glob.glob(os.path.join(folder_path, "*" + extension)):
            if extension == ".wav" or extension == ".ogg":
                if "Music" in folder_path:
                    self.sound_play_info.append(
                        filename.strip(folder_path + "\\").strip(folder_path + "/"))
                else:
                    self.sound_play_info.append(
                        filename.strip(folder_path + "\\").strip(folder_path + "/"))
            elif extension == '.mp3' or extension == ".xm" or extension == ".mod":
                self.sound_play_info.append(filename.strip(folder_path + "\\").strip(folder_path + "/"))

    @staticmethod
    def load_filenames_soundboard(folder_path, extension):
        """
        Takes all the files from the specified path (folder) and puts their filenames into a list.
        :param folder_path: The file path.
        Ex. "SFX"
        Ex. 'SFX/Character'
        Ex. 'SFX\\Character' # If you want to use backslashes, you have to use 2 because it's an escape character.
        :param extension: A file extension.
        Ex. ".wav"
        :return: A list of strings. The path will precede the filename in brackets.
        Ex. SFX = loadSoundFolder("SFX/Character", ".wav")
        print(SFX[0])   # [SFX] filename.wav
        """
        # https://stackoverflow.com/questions/18262293/how-to-open-every-file-in-a-folder/18262324#18262324
        return_list = []
        for filename in glob.glob(os.path.join(folder_path, "*" + extension)):
            if extension == ".wav" or extension == ".ogg":
                if "Music" in folder_path:
                    return_list.append(
                        "[" + folder_path + "] " + filename.strip(folder_path + "\\").strip(folder_path + "/"))
                else:
                    return_list.append(
                        "[" + folder_path + "] " + filename.strip(folder_path + "\\").strip(folder_path + "/"))
            elif extension == '.mp3' or extension == ".xm" or extension == ".mod":
                return_list.append(
                    "[" + folder_path + "] " + filename.strip(folder_path + "\\").strip(folder_path + "/"))
        return return_list


# SoundBoard Code
if __name__ == "__main__":
    # Put Folder Paths here to test sounds
    AllFolderPaths = ['Audio/Music', 'Audio/SFX/Player']
    AllFileExtensions = ['.wav', '.mp3', '.ogg', '.xm', '.mod']

    # pygame.mixer.pre_init(frequency=48000, size=-16, channels=2, buffer=4096)
    pygame.init()
    pygame.mixer.init(frequency=48000, size=-16, channels=2, buffer=4096)
    pygame.mixer.set_num_channels(SFX.mixer_channels)
    pygame.mixer.set_reserved(SFX.number_of_reserved_sound_channels)

    soundboard = SFX(AllFolderPaths, AllFileExtensions)
    myClock = pygame.time.Clock()
    fontConsolas = pygame.font.SysFont("Consolas", 12)

    # LAYOUT STUFF
    screenW = 1280
    screenH = 720
    numCol = 4
    numRow = 8
    # LAYOUT STUFF

    screenRes = (screenW, screenH)
    screen = pygame.display.set_mode(screenRes)
    screenSurf = pygame.Surface(screenRes, pygame.SRCALPHA)

    colBorder = screenH // 50
    rowBorder = colBorder
    totalColBorder = colBorder * (numCol + 1)
    totalRowBorder = rowBorder * (numRow + 1)

    boxWidth = (screenW - totalColBorder) // numCol
    boxHeight = (screenH - totalRowBorder) // numRow

    boxCoords = []
    boxID = []
    for i in range(numCol):
        for j in range(numRow):
            boxCoords.append([i, j])
            boxID.append((j + i * numCol))

    running = True
    mouseClick = [0, 1]
    currentSound = 0
    while running:
        screenSurf.fill((0, 0, 0, 0))
        myClock.tick_busy_loop(60)
        myEvents = pygame.event.get()
        # myKeys = pygame.key.get_pressed()
        mousePress = pygame.mouse.get_pressed()
        mousePos = pygame.mouse.get_pos()

        if not mousePress[0]:
            mouseClick[0] = False
        if not mousePress[1]:
            mouseClick[1] = False

        for event in myEvents:
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    break

        for i in range(len(boxID)):
            outerX = boxCoords[i][0] * (boxWidth + colBorder) + colBorder
            outerY = boxCoords[i][1] * (boxHeight + rowBorder) + rowBorder
            innerX = boxCoords[i][0] * (boxWidth + colBorder) + 2 * colBorder
            innerY = boxCoords[i][1] * (boxHeight + rowBorder) + 2 * rowBorder
            innerWidth = boxWidth - 2 * colBorder
            innerHeight = boxHeight - 2 * rowBorder

            outerColor = [127, 127, 127, 191]
            innerColor = [191, 127, 127, 191]
            if outerX <= mousePos[0] <= (outerX + boxWidth):
                if outerY <= mousePos[1] <= (outerY + boxHeight):
                    outerColor = [255, 255, 191, 191]
                    if mousePress[0]:
                        innerColor = [127, 127, 191, 255]
                        if i < len(soundboard.sound_play_info) and not mouseClick[0]:
                            # soundboard.stop_music()
                            # soundboard.stop_sound(soundboard.sound_play_info[currentSound])
                            soundboard.play(soundboard.sound_file_name[i])
                            currentSound = i
                            mouseClick[0] = True

            pygame.draw.rect(screenSurf, outerColor, (outerX, outerY, boxWidth, boxHeight))
            pygame.draw.rect(screenSurf, innerColor, (innerX, innerY, innerWidth, innerHeight))
            if i < len(soundboard.sound_file_name):
                text = fontConsolas.render("{}".format("[" + (str(i)) + "]" + soundboard.sound_file_name[i]), False,
                                           (255, 255, 255))
                screenSurf.blit(text, (innerX + colBorder // 2, innerY + (innerHeight // 2 - rowBorder // 2)))

        screen.blit(screenSurf, (0, 0, screenW, screenH))
        pygame.display.update()

    pygame.quit()
