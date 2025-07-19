from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QApplication, QDesktopWidget
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
import os
import subprocess
import sys

class InstallerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 PDF Vector App - Installer")
        self.setFixedSize(500, 500)
        self.center_window()

        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #7B1FA2, stop:1 #9C27B0);
                color: white;
                font-family: Arial;
            }
            QPushButton {
                background-color: white;
                color: #7B1FA2;
                padding: 12px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #E1BEE7;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignCenter)

        image_path = os.path.join("ui", "d2v.jpg")
        if os.path.exists(image_path):
            logo = QLabel()
            pixmap = QPixmap(image_path).scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo.setPixmap(pixmap)
            logo.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo)


        title = QLabel("Welcome to PDF Vector App")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 20, QFont.Bold))
        layout.addWidget(title)


        subtitle = QLabel("🔧 Installing required dependencies to get started…")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)
        subtitle.setFont(QFont("Arial", 12))
        layout.addWidget(subtitle)


        install_button = QPushButton("✨ Install & Launch App")
        install_button.clicked.connect(self.install_dependencies)
        layout.addWidget(install_button)

        self.setLayout(layout)

    def center_window(self):

        frame_geometry = self.frameGeometry()
        screen_center = QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())

    def install_dependencies(self):
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            QMessageBox.information(self, "✅ Done", "Dependencies installed successfully!")
            self.hide()
            
            from ui.main_ui import MainWindow 
            self.main_ui = MainWindow()
            self.main_ui.show()
        except Exception as e:
            QMessageBox.critical(self, "❌ Failed", f"Installation failed:\n{str(e)}")
