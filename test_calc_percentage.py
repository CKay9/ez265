from ffmpeg.utility import calculate_percentage

# Test various time strings and a fixed total duration
time_strings = ["00:01:00", "00:02:00", "00:03:00"]  # Example times (1 minute, 2 minutes, 3 minutes)
total_duration = 360  # Total duration in seconds (6 minutes)

for time_str in time_strings:
    percentage = calculate_percentage(time_str, total_duration)
    print(f"Time: {time_str}, Percentage: {percentage}%")
