import sys
from PyQt6.QtCore import *
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QLabel,
    QApplication,
    QLineEdit,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton
)
from PyQt6.QtGui import QIcon


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Yotool")

        layout = QVBoxLayout()
        searchboxl = QHBoxLayout()


        instrtext = QLabel("Search,Play and Download from Youtube/yt-dlp")

        self.searchbox = QLineEdit()
        self.searchbox.setPlaceholderText("Enter Youtube URL or Search Term")
        clippastebutton = QPushButton()
        clippastebutton.setIcon(QIcon.fromTheme("paste"))
        clippastebutton.clicked.connect(self.pasteClipboardtobox)
        searchboxl.addWidget(self.searchbox)
        searchboxl.addWidget(clippastebutton)

        submitbutton = QPushButton("Submit")
        

        layout.addWidget(instrtext)
        layout.addLayout(searchboxl)
        layout.addWidget(submitbutton)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def pasteClipboardtobox(self):
        self.searchbox.setText(QApplication.clipboard().text())

app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec()
