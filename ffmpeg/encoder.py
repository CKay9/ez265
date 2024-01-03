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

        percentage = None

        # Read the stderr output line by line as FFmpeg runs
        while True:
            line = process.stderr.readline()
            if not line:
                break

            if match := re.search(r"time=(\d+:\d+:\d+.\d+)", line):
                time_str = match[1]
                logging.debug(f"Match found: {time_str}")
                # Calculate the percentage here based on the
                # time_str and total video duration
                # percentage = calculate_percentage(time_str, total_duration)
                # Send the percentage to the UI thread via the queue
                update_queue.put(percentage)

        _, stderr = process.communicate()
        if process.returncode != 0:
            logging.error(f"FFmpeg terminated with errors: {stderr}")
        else:
            logging.info("FFmpeg process completed successfully.")
    except Exception as e:
        logging.exception(f"Failed to execute FFmpeg command: {e}")
    finally:
        # Signal the UI thread that encoding is done
        update_queue.put('done')
    return process


def start_encoding_threaded(selected_files, output_path, update_queue):
    logging.info(f"Selected files: {selected_files}")
    total_files = len(selected_files)

    for index, file in enumerate(selected_files):
        total_duration = get_video_duration(file)
        process = encode_video(file, output_path)
        while process.poll() is None:
            line = process.stderr.readline()
            if not line:
                break

            logging.debug(f"FFmpeg output: {line}")

            if match := re.search(r"time=(\d+:\d+:\d+.\d+)", line):
                time_str = match[1]
                percentage = calculate_percentage(time_str, total_duration)
                logging.info(f"Current encoding progress: {percentage}")
                update_queue.put(percentage)

        overall_percentage = (index + 1) / total_files * 100
        update_queue.put(overall_percentage)

    update_queue.put('done')  # Indicate that encoding is complete
