from player import Ui_MainWindow
from playlists_dialog import Ui_Dialog as PlaylistD
from add_music_dialog import Ui_Dialog as AddMusicD
from databases.Database import Database, Playlist

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QFileDialog

from pyglet import media

import os

from typing import Union, List


class Player:
    def __init__(self):
        self.music_list = []
        self.is_playing = False
        self.current_music = 0
        self.paths = []

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

    def queue(self, music: Union[List[str], str]):
        if isinstance(music, str):
            self.music_list.append([media.load(music), None])
            self.paths.append(music)
        else:
            self.music_list += [[media.load(path), None] for path in music if os.path.exists(path)]
            self.paths += music

    def clear(self):
        self.music_list[self.current_music][1].pause()
        self.music_list.clear()


class MyWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.player = Player()

        self.previous.clicked.connect(self.player.previous)
        self.next.clicked.connect(self.player.next)
        self.play.clicked.connect(self.player.stop)
        self.playlists.clicked.connect(self.open_playlists_dialog)
        self.add_music.clicked.connect(self.add_new_track)

        self.database = Database()

        with open("config", encoding="utf8") as file:
            try:
                self.current_playlist = Playlist(file.read(), self.database)
                self.music_list.addItems(self.current_playlist.get_formatted_tracks())
                self.player.queue(self.current_playlist.get_paths())
            except Exception as ex:
                print(ex)

    def queue(self, music: Union[List[str], str]):
        self.player.queue(music)

    def open_playlists_dialog(self):
        dialog = PlaylistDialog(self.database)
        dialog.exec_()

        if dialog.is_ok:
            self.player.clear()
            if dialog.playlistsList.currentText() == "Новый плейлист":
                self.database.create_playlist(dialog.lineEdit)
            else:
                self.player.queue(dialog.selected_playlist.get_paths())
                self.music_list.addItems(dialog.selected_playlist.get_formatted_tracks())
                # print(dialog.selected_playlist)
            self.current_playlist = dialog.selected_playlist

    def add_new_track(self):
        dialog = MusicDialog()
        dialog.exec_()
        if dialog.is_ok:
            self.current_playlist.add_track(dialog.name.text(), dialog.chosen_path)
            self.music_list.addItem(dialog.name.text())
            self.queue(dialog.chosen_path)


class PlaylistDialog(QDialog, PlaylistD):
    def __init__(self, database):
        super().__init__()
        self.setupUi(self)

        self.is_ok = False

        self.ok_button.clicked.connect(self.ok_clicked)
        self.cancel_button.clicked.connect(self.close)

        self.playlistsList.currentIndexChanged.connect(self.on_playlist_changed)
        self.on_playlist_changed(0)
        temp = database.get_all_tables()
        self.playlistsList.addItems([i[0] for i in temp if i[0] != "sqlite_sequence"])

        self.selected_playlist = None
        self.database = database

    def on_playlist_changed(self, index):
        cur_text = self.playlistsList.currentText()
        self.music_list.clear()
        if cur_text == "Новый плейлист":
            self.lineEdit.setEnabled(True)
        else:
            self.lineEdit.setEnabled(False)
            self.selected_playlist = Playlist(cur_text, self.database)
            self.music_list.addItems(self.selected_playlist.get_formatted_tracks())

    def ok_clicked(self):
        self.is_ok = True
        self.close()


class MusicDialog(QDialog, AddMusicD):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.is_ok = False

        self.ok_button.clicked.connect(self.ok_clicked)
        self.cancel_button.clicked.connect(self.close)
        self.choose_button.clicked.connect(self.choose_path)

        self.chosen_path = ""

    def ok_clicked(self):
        self.is_ok = True
        self.close()

    def choose_path(self):
        path = QFileDialog.getOpenFileName(self, "Выбрать музыку", "", "Музыка (*.wav, *.mp3)")[0]
        print(path)
        self.chosen_path = path
        self.choosen_path.setText(path)


def excepthook(exctype, value, traceback):
    print(exctype, value, traceback)
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    # ex.queue(["Foo Fighters - The Pretender (Cover by RADIO TAPOK На русском).mp3",
    #           "ruapporangespace_RADIO_TAPOK_-_Deutschland_Rammstein_na_russkom_63540073.mp3"])
    sys.excepthook = excepthook
    ex.show()
    sys.exit(app.exec_())
