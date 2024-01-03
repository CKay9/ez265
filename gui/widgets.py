import threading
from ffmpeg.encoder import start_encoding_threaded


def start_encoding(update_ui_callback, file_vars, output_path):
    update_ui_callback('start')
    # Pass the necessary arguments when starting the thread
    threading.Thread(target=start_encoding_threaded,
                     args=(update_ui_callback, file_vars, output_path)).start()


def stop_encoding(update_ui_callback):
    update_ui_callback('stop')
