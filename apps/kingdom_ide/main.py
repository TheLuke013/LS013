import sys
import argparse
from PySide6.QtWidgets import QApplication
from apps.kingdom_ide.app import KingdomIDE

def parse_arguments():
    parser = argparse.ArgumentParser(description='Kingdom IDE')
    parser.add_argument('project', nargs='?', default=None, help='Project directory path')
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    app = QApplication(sys.argv)
    ide = KingdomIDE(args.project)
    ide.showMaximized()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()