import sys
import random
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QPushButton, QApplication
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import ast
import numpy as np
import re
import os
import ctypes

from RSAEncry import Encryption
from emotions import display

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

matplotlib.use("Qt5Agg")


class Canvas(FigureCanvas):
    def __init__(self):
        self.fig = Figure()  # linewidth=1
        FigureCanvas.__init__(self, self.fig)
        self.axes = self.fig.add_subplot(111)

    def plot(self, x, y, title, xlabel, ylabel):
        self.axes.plot(x, y)
        self.axes.set_title(title)
        self.axes.set_xlabel(xlabel)
        self.axes.set_ylabel(ylabel)
        self.axes.grid()
        self.draw()

    def plotline(self, x, y, fmt):
        self.axes.plot(x, y, fmt)
        self.draw()

    def reset(self):
        self.fig.clear()
        self.axes = self.fig.add_subplot(111)


class MALDialog(QDialog):
    def __init__(self, key, cipher_text):
        super().__init__()
        self.key = key
        self.cipher_text = cipher_text
        self.rsa = Encryption()

        # ==================================================
        # figure-1: wave
        self.plotMAL = Canvas()

        # ==================================================
        # put figures into layout
        layoutPaintCol = QVBoxLayout()
        layoutPaintCol.addWidget(self.plotMAL)

        # ==================================================
        # parameters
        layoutPara = QHBoxLayout()

        self.labelEmo = QLabel('Please wait...\nYou can press "Q" on your keyboard to close the camera.')
        self.labelEmo.setFont(QFont('Arial', 12))
        layoutPara.addWidget(self.labelEmo)
        layoutPara.addStretch(0)

        # ==================================================
        # top layout
        layoutTop = QVBoxLayout(self)
        layoutTop.addLayout(layoutPaintCol)
        layoutTop.addLayout(layoutPara)
        if cipher_text != '':
            self.plot(self.key, self.cipher_text)

        self.resize(800, 300)
        self.setWindowTitle('MAL(Mental Arousal Level)')

        self.move(900, 100)

    def plot(self, key, cipher_text):
        plaintext = self.rsa.rsa_long_decrypt(cipher_text, key['private'].decode())
        data = ast.literal_eval(plaintext)
        self.xdata = data['xdata']
        self.ydata = data['ydata']
        self.age = data['age']
        self.gender = data['gender']
        self.OCC = data['OCC']
        self.MHR = data['MHR']
        self.plotMAL.reset()
        HRmin = self.MHR
        l = self.OCC
        HRmax = 220 - self.age

        if len(self.xdata) > 1:
            x = list(range(len(self.xdata)))[1:]
            y = []
            a = 0.0003
            for i in range(1, len(self.xdata)):
                HR_ = HRmin + (self.ydata[i - 1] - HRmin) * pow(np.e, -a * l)
                AHR = self.ydata[i] - HR_
                AHR_ = abs(AHR) / (HRmax - HRmin)
                y.append(np.sign(AHR) * (1 - pow(np.e, -AHR_) / (1 - pow(np.e, -1))))
            if os.path.exists('emotion.txt'):
                with open('emotion.txt', 'r') as f:
                    emotion = f.read()
                if y[-1] > 0.5 or y[-1] < -0.3:
                    self.labelEmo.setText(
                        'You are ' + emotion + '.\nYou can press "Q" on your keyboard to close the camera.')
                else:
                    self.labelEmo.setText('You are Neutral.\nYou can press "Q" on your keyboard to close the camera.')
            else:
                self.labelEmo.setText('Please wait...\nYou can press "Q" on your keyboard to close the camera.')
            self.plotMAL.plot(x, y, 'MAL(Mental Arousal Level)', 't(s)', 'MAL')
            self.plotMAL.plotline(x, [0] * len(x), 'r-')
            self.plotMAL.plotline(x, [-0.3] * len(x), 'g--')
            self.plotMAL.plotline(x, [0.5] * len(x), 'g--')


class Dialog(QtWidgets.QDialog):
    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(self,
                                               'Warning',
                                               "Do you want to exit?",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


class HeartRateDialog(Dialog):
    def __init__(self):
        super().__init__()
        self.n_data = 60
        self.xdata = list(range(self.n_data))
        self.ydata = [random.randint(60, 70) for i in range(self.n_data)]
        self.icon = QIcon('igem.png')
        self.rsa = Encryption()
        self.key = self.rsa.getKey()
        self.cipher_text = ''

        self.help_text = '''
        Please enter an Age, the range is greater than 0.
        Please enter Gender, you can only enter 0 or 1, 
        representing biological sex male and biological sex 
        female respectively.
        Please enter an Overall Cardiovascular Condition 
        in the range 0 to 1.
        Please enter a Minimum Heart Rate, the range is 
        in the range 35 to 100.
        Please select one of Overall Cardiovascular Condition 
        and Minimum Heart Rate to enter, if both are entered, 
        only the cardiovascular level is valid, because 
        cardiovascular level and minimum heart rate can be 
        converted to each other.
        '''
        # ==================================================
        # parameters
        layoutPara = QHBoxLayout()

        self.labelAge = QLabel('Age:')
        self.lineeditAge = QLineEdit()
        layoutPara.addWidget(self.labelAge)
        layoutPara.addWidget(self.lineeditAge)
        layoutPara.addStretch(1)

        self.labelGender = QLabel('Gender:')
        self.lineeditGender = QLineEdit()
        layoutPara.addWidget(self.labelGender)
        layoutPara.addWidget(self.lineeditGender)
        layoutPara.addStretch(1)

        self.labelOCC = QLabel('Overall Cardiova-\nscular Condition:')
        self.lineeditOCC = QLineEdit()
        layoutPara.addWidget(self.labelOCC)
        layoutPara.addWidget(self.lineeditOCC)
        layoutPara.addStretch(1)

        self.labelMHR = QLabel('Minimum \nHeart Rate:')
        self.lineeditMHR = QLineEdit()
        layoutPara.addWidget(self.labelMHR)
        layoutPara.addWidget(self.lineeditMHR)
        layoutPara.addStretch(1)

        # ==================================================
        # figure-1: Heart Rate
        self.plotHR = Canvas()

        # ==================================================
        # put figures into layout
        layoutPaintCol = QVBoxLayout()
        layoutPaintCol.addWidget(self.plotHR)

        # ==================================================
        # buttons
        self.buttonStop = QPushButton('Stop')
        self.buttonStop.clicked.connect(self.stopTimer)
        self.buttonStop.setDisabled(True)
        self.buttonStart = QPushButton('Start')
        self.buttonStart.clicked.connect(self.privacy)
        self.buttonHelp = QPushButton('Help')
        self.buttonHelp.clicked.connect(lambda: self.Note(self.help_text, 'Help', 540, 400))
        layoutStartStop = QHBoxLayout()
        layoutStartStop.addStretch(1)
        layoutStartStop.addWidget(self.buttonStart)
        layoutStartStop.addWidget(self.buttonStop)
        layoutStartStop.addWidget(self.buttonHelp)

        # ==================================================
        # top layout
        layoutTop = QVBoxLayout(self)
        layoutTop.addLayout(layoutPara)
        layoutTop.addLayout(layoutPaintCol)
        layoutTop.addLayout(layoutStartStop)

        self.blank()

        self.resize(800, 600)
        self.setWindowTitle('Heart Rate')
        self.setWindowIcon(self.icon)

        self.Note(self.help_text, 'Help', 540, 400)

        # Setup a timer to trigger the redraw by calling update_plot.
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update)
        self.maldialog = MALDialog(self.key, self.cipher_text)
        self.maldialog.setWindowModality(Qt.ApplicationModal)
        self.timer.timeout.connect(lambda: self.maldialog.plot(self.key, self.cipher_text))

    def privacy(self):
        if self.warning():
            pricacydialog = QDialog()
            pricacydialog.setGeometry(500, 500, 540, 200)
            gridlayout = QGridLayout()
            pricacydialog.setLayout(gridlayout)
            privacy = '''
            Please confirm whether to allow camera permission.
            The entered personal information will be encrypted 
            and stored locally, and will be deleted at the end 
            of the program.
            '''
            pricacydialog.labelPrivacy = QLabel(privacy, pricacydialog)
            pricacydialog.labelPrivacy.setFont(QFont('Arial', 12))
            gridlayout.addWidget(pricacydialog.labelPrivacy, 0, 0)

            pricacydialog.buttonyes = QPushButton('Accept', pricacydialog)
            pricacydialog.buttonyes.clicked.connect(pricacydialog.close)
            pricacydialog.buttonyes.clicked.connect(self.startTimer)

            gridlayout.addWidget(pricacydialog.buttonyes, 1, 0)

            pricacydialog.buttonno = QPushButton('Refuse', pricacydialog)
            pricacydialog.buttonno.clicked.connect(pricacydialog.close)
            gridlayout.addWidget(pricacydialog.buttonno, 1, 1)

            pricacydialog.setWindowTitle('Privacy Protection Announcement')
            pricacydialog.setWindowIcon(self.icon)
            pricacydialog.setWindowModality(Qt.ApplicationModal)
            pricacydialog.show()
            pricacydialog.exec_()

    def startTimer(self):
        self.buttonStart.setDisabled(True)
        self.buttonStop.setDisabled(False)
        self.plot()
        self.timer.start()
        self.maldialog.show()
        display()
        self.maldialog.exec_()

    def is_number(self, num):
        pattern = re.compile(r'^[-+]?[-0-9]\d*\.\d*|[-+]?\.?[0-9]\d*$')
        result = pattern.match(num)
        if result:
            return True
        else:
            return False

    def warning(self):
        textAge = self.lineeditAge.text()
        textGender = self.lineeditGender.text()
        textOCC = self.lineeditOCC.text()
        textMHR = self.lineeditMHR.text()
        msg = ''
        if not (self.is_number(textAge) and float(textAge) > 0):
            msg += '\n' + self.help_text.split('\n')[1]
        if textGender != '1' and textGender != '0':
            msg += '\n' + '\n'.join(self.help_text.split('\n')[2:5])
        if not (self.is_number(textOCC) and 0 < float(textOCC) <= 1) and textMHR == '':
            msg += '\n' + '\n'.join(self.help_text.split('\n')[5:7])
        if not (self.is_number(textMHR) and 35 <= float(textMHR) <= 100) and textOCC == '':
            msg += '\n' + '\n'.join(self.help_text.split('\n')[7:9])

        if textOCC == '' and textMHR == '':
            msg += '\n' + '\n'.join(self.help_text.split('\n')[9:])

        if msg != '':
            self.Note(msg, 'Warning', 540, 28 * len(msg.split('\n')))
            return False
        else:
            return True

    def stopTimer(self):
        self.buttonStop.setDisabled(True)
        self.buttonStart.setDisabled(False)
        self.timer.stop()
        self.maldialog.close()

    def Note(self, msg, title, x, y):
        notedialog = QDialog()
        notedialog.resize(x, y)

        notedialog.labelNote = QLabel(msg, notedialog)
        notedialog.labelNote.setFont(QFont('Arial', 12))
        notedialog.labelNote.move(0, 10)

        notedialog.setWindowTitle(title)
        notedialog.setWindowIcon(self.icon)
        notedialog.setWindowModality(Qt.ApplicationModal)
        notedialog.show()
        notedialog.exec_()

    def update(self):
        self.plot()

    def blank(self):
        self.plotHR.reset()
        x = list(range(self.n_data))
        y = [0] * self.n_data
        self.plotHR.plot(x, y, 'Heart Rate', 't(s)', 'beats')

    def plot(self):
        self.plotHR.reset()
        x = self.xdata
        y = self.ydata[1:] + [random.randint(60, 70)]
        self.ydata = y
        # print(y[-1])
        OCC = 0
        MHR = 0

        if self.lineeditOCC.text() != '':
            OCC = float(self.lineeditOCC.text())
            MHR = 35 / OCC + 5 * float(self.lineeditGender.text())
        elif self.lineeditOCC.text() == '' and self.lineeditMHR.text() != '':
            MHR = float(self.lineeditMHR.text())
            OCC = 35 / (MHR - 5 * float(self.lineeditGender.text()))

        data = {'xdata': self.xdata,
                'ydata': self.ydata,
                'age': float(self.lineeditAge.text()),
                'gender': float(self.lineeditGender.text()),
                'OCC': OCC,
                'MHR': MHR}

        # encrypt
        self.cipher_text = self.rsa.rsa_long_encrypt(str(data), self.key['public'].decode())

        self.plotHR.plot(x, y, 'Heart Rate', 't(s)', 'beats')
        self.plotHR.plotline(x, [MHR] * len(x), 'r--')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    test = HeartRateDialog()
    test.show()
    sys.exit(app.exec_())
