#!/usr/bin/python3

import os
import sys
import functools

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from midi import *
from PyQt5.QtWidgets import QApplication, QWidget, QGroupBox, QRadioButton, QGridLayout, QFileDialog, QVBoxLayout, \
    QComboBox, QPushButton, QHBoxLayout, QLineEdit, QLabel, QMainWindow, QSpinBox, QCheckBox, QMessageBox


class GeneratorWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        # Riff related data initialization
        self.file = None
        self.selected_scale = Scale.MAJOR_SCALE
        self.selected_root = NoteValue.A
        self.allowed_rhythm = {
            NoteLength.WHOLE: True, NoteLength.HALF: True, NoteLength.QUARTER: True,
            NoteLength.EIGHTH: True, NoteLength.SIXTEENTH: True, NoteLength.TH32: True,
            NoteLength.TH64: True
        }
        self.number_of_notes = None
        self.use_specific_scale = False

        # UI setup
        self.setGeometry(150, 100, 700, 300)
        self.setWindowIcon(QIcon('Icon.ico'))

        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignTop)

        widget = QWidget()
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)

        self.setup_ui()
        self.show()
        self.setFocus()

    def setup_ui(self):
        self.setup_file_path()
        self.setup_scale()
        self.setup_number_of_notes()
        self.setup_rhythm()

        generate_button = QPushButton()
        generate_button.setText("Generate Riff!")
        generate_button.clicked.connect(self.generate)

        self.main_layout.addWidget(generate_button)

    def setup_file_path(self):
        file_layout = QVBoxLayout()
        file_selection_layout = QHBoxLayout()

        file_path_display = QLineEdit()
        file_path_display.setText(os.path.realpath("/home/"+os.environ.get('USER')))
        file_path_display.editingFinished.connect(functools.partial(self.filepath_changed, file_path_display))
        select_file_button = QPushButton("Select File")
        select_file_button.clicked.connect(functools.partial(self.choose_file, file_path_display))

        file_path_label = QLabel()
        file_path_label.setText("Path:")

        file_selection_layout.addWidget(file_path_display)
        file_selection_layout.addWidget(select_file_button)

        file_layout.addWidget(file_path_label)
        file_layout.addLayout(file_selection_layout)

        self.main_layout.addLayout(file_layout)

    def setup_scale(self):
        # Create a group of radio buttons
        scale_group_box = QGroupBox()
        scale_group_box.setTitle("Use specific scale")
        scale_group_box.setCheckable(True)
        scale_group_box.setChecked(False)
        scale_group_box.toggled.connect(self.use_scale)

        scale_group_box_layout = QVBoxLayout()
        grid_layout = QGridLayout()

        natural_minor_radio = QRadioButton("Natural Minor")
        natural_minor_radio.toggled.connect(functools.partial(self.scale_changed, Scale.NATURAL_MINOR_SCALE))

        harmonic_minor_radio = QRadioButton("Harmonic Minor")
        harmonic_minor_radio.toggled.connect(functools.partial(self.scale_changed, Scale.HARMONIC_MINOR_SCALE))

        major_radio = QRadioButton("Major")
        major_radio.toggled.connect(functools.partial(self.scale_changed, Scale.MAJOR_SCALE))

        minor_pentatonic_radio = QRadioButton("Minor Pentatonic")
        minor_pentatonic_radio.toggled.connect(functools.partial(self.scale_changed, Scale.MINOR_PENTATONIC_SCALE))

        major_pentatonic_radio = QRadioButton("Major Pentatonic")
        major_pentatonic_radio.toggled.connect(functools.partial(self.scale_changed, Scale.MAJOR_PENTATONIC_SCALE))

        major_radio.setChecked(True)

        combo_box = QComboBox()
        combo_box.addItems(['A', 'B♭', 'B', 'C', 'D♭', 'D', 'E♭', 'E', 'F', 'G♭', 'G', 'A♭'])
        combo_box.activated.connect(self.root_changed)

        grid_layout.addWidget(natural_minor_radio, 1, 0)
        grid_layout.addWidget(harmonic_minor_radio, 1, 1)
        grid_layout.addWidget(major_radio, 0, 0)
        grid_layout.addWidget(minor_pentatonic_radio, 1, 2)
        grid_layout.addWidget(major_pentatonic_radio, 0, 1)

        scale_group_box_layout.addLayout(grid_layout)
        scale_group_box_layout.addWidget(combo_box)

        scale_group_box.setLayout(scale_group_box_layout)

        self.main_layout.addWidget(scale_group_box)

    def setup_number_of_notes(self):
        number_group_box = QGroupBox()
        number_group_box.setTitle("Use specific number of notes")
        number_group_box.setCheckable(True)
        number_group_box.setChecked(False)
        number_group_box_layout = QVBoxLayout()
        number_of_notes = QSpinBox()
        number_of_notes.setMinimum(1)
        number_of_notes.setMaximum(8161)
        number_of_notes.setValue(1)
        number_of_notes.valueChanged.connect(self.number_of_notes_changed)

        number_group_box_layout.addWidget(number_of_notes)
        number_group_box.setLayout(number_group_box_layout)

        self.main_layout.addWidget(number_group_box)

    def setup_rhythm(self):
        rythm_group_box = QGroupBox()
        rythm_group_box.setTitle("Restrain rhythm possibilities")
        rythm_group_box.setCheckable(True)
        rythm_group_box.setChecked(False)
        rythm_group_box_layout = QGridLayout()

        whole_box = QCheckBox("Hole note (𝅝  )")
        whole_box.setChecked(True)
        whole_box.stateChanged.connect(functools.partial(self.rhythm_changed, NoteLength.WHOLE))

        half_box = QCheckBox("Half note (𝅗𝅥  )")
        half_box.setChecked(True)
        half_box.stateChanged.connect(functools.partial(self.rhythm_changed, NoteLength.HALF))

        quarter_box = QCheckBox("Quarter note (♩)")
        quarter_box.setChecked(True)
        quarter_box.stateChanged.connect(functools.partial(self.rhythm_changed, NoteLength.QUARTER))

        eighth_box = QCheckBox("Eighth note (♪)")
        eighth_box.setChecked(True)
        eighth_box.stateChanged.connect(functools.partial(self.rhythm_changed, NoteLength.EIGHTH))

        sixteenth_box = QCheckBox("Sixteenth note (𝅘𝅥𝅯   )")
        sixteenth_box.setChecked(True)
        sixteenth_box.stateChanged.connect(functools.partial(self.rhythm_changed, NoteLength.SIXTEENTH))

        th32_box = QCheckBox("Thirty second note (𝅘𝅥𝅰   )")
        th32_box.setChecked(True)
        th32_box.stateChanged.connect(functools.partial(self.rhythm_changed, NoteLength.TH32))

        th64_box = QCheckBox("Sixty fourth note (𝅘𝅥𝅱   )")
        th64_box.setChecked(True)
        th64_box.stateChanged.connect(functools.partial(self.rhythm_changed, NoteLength.TH64))

        rythm_group_box_layout.addWidget(whole_box, 0, 0)
        rythm_group_box_layout.addWidget(half_box, 0, 1)
        rythm_group_box_layout.addWidget(quarter_box, 1, 0)
        rythm_group_box_layout.addWidget(eighth_box, 1, 1)
        rythm_group_box_layout.addWidget(sixteenth_box, 1, 2)
        rythm_group_box_layout.addWidget(th32_box, 2, 0)
        rythm_group_box_layout.addWidget(th64_box, 2, 1)

        rythm_group_box.setLayout(rythm_group_box_layout)

        self.main_layout.addWidget(rythm_group_box)

    def choose_file(self, file_path_display: QLineEdit):
        # File picker
        file_dialog = QFileDialog(self)
        file_dialog.setDirectory(os.path.realpath('.'))
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setNameFilter("MIDI Files (*.mid) ;; All Files (*)")
        file_dialog.setWindowModality(Qt.ApplicationModal)
        if file_dialog.exec_():
            filenames = file_dialog.selectedFiles()
            self.file = filenames[0]
            file_path_display.setText(self.file)

    def filepath_changed(self, file_edit: QLineEdit):
        self.file = file_edit.text()
        print(self.file)

    def use_scale(self, boolean: bool):
        self.use_specific_scale = boolean

    def scale_changed(self, new_scale: Scale):
        self.selected_scale = new_scale

    def root_changed(self, root_index: int):
        self.selected_root = NoteValue(root_index + 0x39)

    def number_of_notes_changed(self, number: int):
        self.number_of_notes = number

    def rhythm_changed(self, note: NoteLength, status: int):
        self.allowed_rhythm[note] = True if status == 2 else False

    def generate(self):
        if not self.file:
            alert = QMessageBox()
            alert.setIcon(QMessageBox.Critical)
            alert.setText("You must specify a file!")
            alert.setWindowTitle("Error")
            alert.setStandardButtons(QMessageBox.Close)
            alert.exec_()
            return
        try:
            file = open(self.file, "wb", buffering=1)
        except PermissionError:
            alert = QMessageBox()
            alert.setIcon(QMessageBox.Critical)
            alert.setText("You do not have permission to write in {}".format(self.file[:self.file.rfind('/')+1]))
            alert.setWindowTitle("Error opening file")
            alert.setStandardButtons(QMessageBox.Close)
            alert.exec_()
            return
        riff = Riff(scale=self.selected_scale if self.use_specific_scale else None,
                    root=self.selected_root if self.use_specific_scale else None, number_notes=self.number_of_notes,
                    allowed_rhythm=[length for length in self.allowed_rhythm.keys() if self.allowed_rhythm[length]])
        riff.populate()
        try:
            write(riff, file)
            file.close()
            alert = QMessageBox()
            alert.setIcon(QMessageBox.Information)
            alert.setText("The MIDI file has correcty been generated")
            alert.setWindowTitle("Confirmation")
            alert.setStandardButtons(QMessageBox.Ok)
            open_in_musescore_button = QPushButton()
            open_in_musescore_button.setText("Open in MuseScore")
            alert.addButton(open_in_musescore_button, QMessageBox.YesRole)
            alert.exec_()
            if alert.clickedButton() == open_in_musescore_button:
                os.system('musescore3 {} &'.format(self.file))
        except MIDIWritingError as e:
            alert = QMessageBox()
            alert.setIcon(QMessageBox.Critical)
            alert.setText("An error occurred while writing the MIDI file")
            alert.setInformativeText(str(e))
            alert.setWindowTitle("Critical Error")
            alert.setStandardButtons(QMessageBox.Close)
            alert.exec_()
        except Exception as e:
            alert = QMessageBox()
            alert.setIcon(QMessageBox.Critical)
            alert.setText("An error occurred while writing the MIDI file")
            alert.setInformativeText(str(e))
            alert.setWindowTitle("Critical Error")
            alert.setStandardButtons(QMessageBox.Close)
            alert.exec_()
        finally:
            file.close()


def window():
    app = QApplication(sys.argv)
    w = QWidget()

    # Create a group of radio buttons
    group_box = QGroupBox()
    group_box.setTitle("Use specific scale")
    group_box.setCheckable(True)
    group_box.setChecked(False)

    group_box_layout = QVBoxLayout()

    grid_layout = QGridLayout()
    radio1 = QRadioButton("Natural Minor")
    radio2 = QRadioButton("Harmonic Minor")
    radio3 = QRadioButton("Major")
    radio4 = QRadioButton("Minor Pentatonic")
    radio5 = QRadioButton("Major Pentatonic")
    grid_layout.addWidget(radio1, 1, 0)
    grid_layout.addWidget(radio2, 1, 1)
    grid_layout.addWidget(radio3, 0, 0)
    grid_layout.addWidget(radio4, 1, 2)
    grid_layout.addWidget(radio5, 0, 1)

    radio3.setChecked(True)

    group_box_layout.addLayout(grid_layout)
    combo_box = QComboBox()
    combo_box.addItems(['A', 'B♭', 'B', 'C', 'D♭', 'D', 'E♭', 'E', 'F', 'G♭', 'G', 'A♭'])
    group_box_layout.addWidget(combo_box)

    group_box.setLayout(group_box_layout)

    main_layout = QVBoxLayout()
    main_layout.addWidget(group_box)
    button = QPushButton()
    button.setText("Select File")
    button.clicked.connect(choose_file)
    main_layout.addWidget(button)
    w.setLayout(main_layout)
    w.setGeometry(100, 100, 500, 400)
    w.setWindowTitle("MIDI Riff Generator")
    w.show()
    app.exec_()


def choose_file():
    # File picker
    file_dialog = QFileDialog()
    file_dialog.setAcceptMode(QFileDialog.AcceptSave)
    file_dialog.setOptions(QFileDialog.Option() | QFileDialog.DontUseNativeDialog)
    file_dialog.setNameFilter("MIDI Files (*.mid) ;; All Files (*)")
    if file_dialog.exec_():
        file_dialog.setFocus(True)
        filenames = file_dialog.selectedFiles()
        file = open(filenames[0], "w")
        file.close()


if __name__ == '__main__':
    # window()
    app = QApplication(sys.argv)
    window = GeneratorWindow()
    app.exec_()
