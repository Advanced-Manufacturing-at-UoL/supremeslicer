import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel

class SimpleUI(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # This is the main layout
        layout = QVBoxLayout()

        # Create a label and a button
        self.label = QLabel('Hello, PyQt5!', self)
        btnGreet = QPushButton('Click Me', self)
        btnGreet.clicked.connect(self.on_click)

        # Add widgets to the layout
        layout.addWidget(self.label)
        layout.addWidget(btnGreet)

        # Set the layout on the application's window
        self.setLayout(layout)
        self.setWindowTitle('Simple PyQt5 App')
        self.show()

    def on_click(self):
        self.label.setText('Button Clicked!')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SimpleUI()
    sys.exit(app.exec_())
