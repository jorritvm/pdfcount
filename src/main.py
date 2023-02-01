from PyQt5.QtWidgets import *
import PyPDF2

import os
import os.path
import sys

from resources.uipy.gui import *


class MainWindow(QMainWindow, Ui_pdfcount):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setupSlots()
        self.setAcceptDrops(True)
        self.setupTable()

    def setupTable(self):
        self.tblFiles.clear()
        self.tblFiles.setRowCount(0);
        self.tblFiles.setColumnCount(3);
        self.tblFiles.setHorizontalHeaderLabels(['File', 'Size', 'Pages'])
        self.tblFiles.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch) # stretch files column

    def setupSlots(self):
        self.btnWipe.clicked.connect(self.setupTable)
        self.btnCount.clicked.connect(self.countPages)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        for f in files:
            self.addFileToTable(f)

    def addFileToTable(self, f):
        if not is_pdf(f): return

        self.removeTotalsRow()

        r = self.tblFiles.rowCount()
        self.tblFiles.setRowCount(r + 1)
        self.tblFiles.setItem(r, 0, FileItem(f))
        self.tblFiles.setItem(r, 1, QTableWidgetItem(get_size(f)))
        self.tblFiles.setItem(r, 2, QTableWidgetItem(""))

    def countPages(self):
        self.removeTotalsRow()

        sum = 0
        for i in range(self.tblFiles.rowCount()):
            print(self.tblFiles.item(i, 0).text())
            if self.tblFiles.item(i, 2).text() == "":
                with open(self.tblFiles.item(i, 0).f, 'rb') as file:
                    pdfReader = PyPDF2.PdfReader(file)
                    count = len(pdfReader.pages)
                    self.tblFiles.item(i, 2).setText(str(count))
                sum = sum + count
            else:
                sum = sum + int(self.tblFiles.item(i, 2).text())

        self.addTotalsRow(sum)

    def addTotalsRow(self, sum):
        r = self.tblFiles.rowCount()
        self.tblFiles.setRowCount(r + 1)
        self.tblFiles.setItem(r, 0, QTableWidgetItem("Total:"))
        self.tblFiles.setItem(r, 2, QTableWidgetItem(str(sum)))

    def removeTotalsRow(self):
        r = self.tblFiles.rowCount()
        if r > 0:
            if self.tblFiles.item(r-1, 0).text() == "Total:":
                self.tblFiles.removeRow(r-1)


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
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec_())