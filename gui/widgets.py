import threading
from ffmpeg.encoder import start_encoding_threaded


def start_encoding(update_ui_callback,
                   selected_files, output_path,
                   update_queue):
    update_ui_callback('start')
    # Pass the necessary arguments when starting the thread
    threading.Thread(target=start_encoding_threaded,
                     args=(selected_files,
                           output_path,
                           update_queue)).start()


def stop_encoding(update_ui_callback):
    update_ui_callback('stop')
