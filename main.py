from player import Ui_MainWindow
from playlists_dialog import Ui_Dialog

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog

from pyglet import media

import os

from typing import Union


class Player:
    def __init__(self):
        self.music_list = []
        self.is_playing = False
        self.current_music = 0

    def previous(self):
        self.stop()
        self.music_list[self.current_music][0].seek(0)
        self.current_music = (self.current_music - 1) % len(self.music_list)
        self.stop()

    def next(self):
        self.stop()
        self.music_list[self.current_music][0].seek(0)
        self.current_music = (self.current_music + 1) % len(self.music_list)
        self.stop()

    def stop(self):
        if self.is_playing:
            self.music_list[self.current_music][1].pause()
            self.is_playing = False
        else:
            self.music_list[self.current_music][1] = self.music_list[self.current_music][0].play()
            self.is_playing = True

    def init_music(self, music_paths: list):
        self.music_list = [[media.load(path), None] for path in music_paths if os.path.isfile(path)]

    def queue(self, music: Union[list, str]):
        if isinstance(music, str):
            self.music_list.append(media.load(music))
        else:
            self.init_music(music)


class MyWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.player = Player()

        self.previous.clicked.connect(self.player.previous)
        self.next.clicked.connect(self.player.next)
        self.play.clicked.connect(self.player.stop)
        self.playlists.clicked.connect(self.open_playlists_dialog)

    def queue(self, music: Union[list, str]):
        self.player.queue(music)
# Дальше мусор)

    def open_playlists_dialog(self):
        self.dialog = Temp()
        self.dialog.exec_()


class Temp(QDialog, Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.ok_button.clicked.connect(self.ok_clicked)
        self.playlistsList.currentIndexChanged.connect(self.on_playlist_changed)
        self.on_playlist_changed(0)

    def on_playlist_changed(self, index):
        cur_text = self.playlistsList.currentText()
        if cur_text == "Новый плейлист":
            self.lineEdit.setEnabled(True)
        else:
            self.lineEdit.setEnabled(False)

    def ok_clicked(self):
        pass


def excepthook(exctype, value, traceback):
    print(exctype, value, traceback)
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.queue(["Foo Fighters - The Pretender (Cover by RADIO TAPOK На русском).mp3",
              "ruapporangespace_RADIO_TAPOK_-_Deutschland_Rammstein_na_russkom_63540073.mp3"])
    sys.excepthook = excepthook
    ex.show()
    sys.exit(app.exec_())
