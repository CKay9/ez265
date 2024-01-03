import logging
import queue
from gui.main_window import MainWindow


logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
update_queue = queue.Queue()


def check_queue(window):
    while not update_queue.empty():
        percentage = update_queue.get()
        window.update_progress(percentage)  # Update the progress bar
    window.root.after(100, check_queue, window)


def main():
    window = MainWindow()
    window.run()
    check_queue(window)


if __name__ == "__main__":
    main()
