import logging
from gui.main_window import MainWindow

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def main():
    window = MainWindow()
    window.run()


if __name__ == "__main__":
    main()
