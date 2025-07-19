from PyQt5.QtWidgets import QApplication
import sys
from ui.installer import InstallerWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = InstallerWindow()
    window.show()
    sys.exit(app.exec_())