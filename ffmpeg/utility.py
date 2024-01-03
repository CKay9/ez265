import logging
import re
import subprocess


def get_video_duration(input_file):
    """Get the duration of the video in seconds."""
    command = ['ffmpeg', '-i', input_file]
    process = subprocess.Popen(command,
                               stderr=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               universal_newlines=True)
    _, stderr = process.communicate()  # Modified line
    if match := re.search(r"Duration: (\d+:\d+:\d+.\d+)", stderr):
        duration_str = match[1]
        hours, minutes, seconds = map(float, duration_str.split(':'))
        return hours * 3600 + minutes * 60 + seconds
    logging.info("Duration not transmitted")
    return None


def calculate_percentage(current_time_str, total_duration):
    hours, minutes, seconds = map(float, current_time_str.split(':'))
    current_time_seconds = hours * 3600 + minutes * 60 + seconds
    percentage = (current_time_seconds / total_duration) * 100 if total_duration > 0 else 0
    logging.debug(f"Calculated percentage: {percentage}% from current time {current_time_str} and total duration {total_duration}")
    logging.info(f"Calculating: Current Time = {current_time_seconds}s, Total Duration = {total_duration}s, Percentage = {percentage}%")
    return percentage
