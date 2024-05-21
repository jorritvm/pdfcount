import os
import os.path
import sys

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from pyprojroot import here
import PyPDF2
import pandas as pd

from resources.uipy.gui import *


class MainWindow(QMainWindow, Ui_pdfcount):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setupSlots()
        self.setAcceptDrops(True)
        self.setupTable()

    def setupTable(self):
        """ Modify the central table layout """
        self.tblFiles.clear()
        self.tblFiles.setRowCount(0)
        self.tblFiles.setColumnCount(4)
        self.tblFiles.setHorizontalHeaderLabels(['File', 'Size', 'Pages', 'Cumul'])
        self.tblFiles.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)  # stretch files column

    def setupSlots(self):
        """ Connect the buttons to the callback functions """
        self.btnWipe.clicked.connect(self.setupTable)
        self.btnCount.clicked.connect(self.countPages)
        self.btnSave.clicked.connect(self.saveCount)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        """ Hand of dropping of selected file onto central table widget """
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        for f in files:
            self.addFileToTable(f)

    def addFileToTable(self, f):
        """ Add a file to the table (f is a file path)"""
        if not is_pdf(f):
            return

        r = self.tblFiles.rowCount()
        self.tblFiles.setRowCount(r + 1)
        self.tblFiles.setItem(r, 0, FileItem(f))
        self.tblFiles.setItem(r, 1, QTableWidgetItem(get_size(f)))
        self.tblFiles.setItem(r, 2, QTableWidgetItem(""))
        self.tblFiles.setItem(r, 3, QTableWidgetItem(""))

    def countPages(self):
        """ Count the number of pages in the desired pdfs """
        count_total = 0
        for i in range(self.tblFiles.rowCount()):
            if self.tblFiles.item(i, 2).text() == "":
                # first time counting this file, open it and count it
                with open(self.tblFiles.item(i, 0).f, 'rb') as file:
                    pdfReader = PyPDF2.PdfReader(file)
                    count = len(pdfReader.pages)
                    self.tblFiles.item(i, 2).setText(str(count))
                count_total = count_total + count
            else:
                # file already counted, just take previous value
                count_total = count_total + int(self.tblFiles.item(i, 2).text())
            # add cumulative sum to line as well
            self.tblFiles.item(i, 3).setText(str(count_total))

    def saveCount(self):
        pass


class FileItem(QTableWidgetItem):
    def __init__(self, f):
        super().__init__(os.path.basename(f))
        self.f = f


def get_size(path):
    size = os.path.getsize(path)
    if size < 1024:
        return f"{size} bytes"
    elif size < pow(1024, 2):
        return f"{round(size/1024, 2)} KB"
    elif size < pow(1024, 3):
        return f"{round(size/(pow(1024,2)), 2)} MB"
    elif size < pow(1024, 4):
        return f"{round(size/(pow(1024,3)), 2)} GB"


def is_pdf(f):
    file_name, file_extension = os.path.splitext(f)
    return file_extension.lower() == ".pdf"


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(here('doc/pdf.ico'))))
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec_())