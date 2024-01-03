import subprocess
import re
import os
import logging
from ffmpeg.utility import get_video_duration, calculate_percentage
import queue

update_queue = queue.Queue()


def encode_video(input_file, output_path):
    base_name = os.path.basename(input_file)
    name_without_ext, _ = os.path.splitext(base_name)
    output_file = f"{output_path}/{name_without_ext}_HEVC.mkv"
    logging.info("Starting FFmpeg process...")
    command = [
        'ffmpeg',
        '-i', input_file,
        '-c:v', 'hevc_videotoolbox',
        '-crf', '30',
        '-c:a', 'copy',
        output_file
    ]

    try:
        process = subprocess.Popen(
            command, stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            universal_newlines=True
        )
        _, stderr = process.communicate()
        if process.returncode != 0:
            logging.error(f"FFmpeg terminated with errors: {stderr}")
        else:
            logging.info("FFmpeg process completed successfully.")
    except Exception as e:
        logging.exception(f"Failed to execute FFmpeg command: {e}")
    return process


def start_encoding_threaded(update_ui_callback, file_vars, output_path):
    selected_files = [file for file, var in file_vars.items() if var.get() > 0]
    logging.info(f"Selected files: {selected_files}")
    total_files = len(selected_files)

    for index, file in enumerate(selected_files):
        total_duration = get_video_duration(file)
        process = encode_video(file, output_path.get())
        while process.poll() is None:
            line = process.stderr.readline()
            if not line:
                break

            logging.debug(f"FFmpeg output: {line}")

            if match := re.search(r"time=(\d+:\d+:\d+.\d+)", line):
                time_str = match[1]
                percentage = calculate_percentage(time_str, total_duration)
                logging.info(f"Current encoding progress: {percentage}")
                update_ui_callback(percentage)

        overall_percentage = (index + 1) / total_files * 100
        update_ui_callback(overall_percentage)
