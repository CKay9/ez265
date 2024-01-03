import glob
import logging
import os
import cv2
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from .widgets import start_encoding, stop_encoding


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ezncode")
        self.root.geometry("800x600")
        self.root.grid_columnconfigure(1, weight=1)

        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.file_vars = {}
        # Dictionary to store the variables associated with the checkboxes

        self.setup_ui()
        self.center_window()

    def center_window(self):
        # Get the screen width and height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calculate the x and y coordinates based on the screen dimensions
        x = (screen_width - 800) // 2
        y = (screen_height - 600) // 2

        # Set the geometry of the tkinter window and position it in the center
        self.root.geometry(f'800x600+{x}+{y}')

    def setup_ui(self):
        self.setup_scrollable_area()
        self.setup_path_selection()
        self.setup_buttons()
        self.setup_progress()

    def setup_scrollable_area(self):
        self.canvas = tk.Canvas(self.root)
        self.scrollbar = ttk.Scrollbar(self.root,
                                       orient="vertical",
                                       command=self.canvas.yview)

        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                      scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0),
                                  window=self.scrollable_frame,
                                  anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.grid(row=2, column=0, columnspan=3, sticky='nsew')
        self.scrollbar.grid(row=2, column=3, sticky='ns')

        # Bind mouse wheel scrolling events
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(4, weight=0)

        self.check_all_button = tk.Button(self.root, text="Check All", command=self.check_all)
        self.uncheck_all_button = tk.Button(self.root, text="Uncheck All", command=self.uncheck_all)

        self.check_all_button.grid(row=3, column=1, padx=(400, 5), pady=0, sticky='e')
        self.uncheck_all_button.grid(row=3, column=2, padx=(0, 20), pady=0, sticky='w')

    def on_mousewheel(self, event):
        if event.delta < 0:
            self.canvas.yview_scroll(1, "units")
        else:
            self.canvas.yview_scroll(-1, "units")

    def check_all(self):
        # Check all checkboxes
        for var in self.file_vars.values():
            var.set(1)

    def uncheck_all(self):
        # Uncheck all checkboxes
        for var in self.file_vars.values():
            var.set(0)

    def on_canvas_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def setup_path_selection(self):
        ttk.Label(self.root,
                  text="Input Directory:").grid(row=0,
                                                column=0,
                                                padx=20,
                                                pady=(20, 5))
        ttk.Entry(self.root,
                  textvariable=self.input_path).grid(row=0,
                                                     column=1,
                                                     pady=(20, 5),
                                                     sticky='ew')
        ttk.Button(self.root,
                   text="Browse",
                   command=self.select_input_path).grid(row=0,
                                                        column=2,
                                                        padx=15,
                                                        pady=(20, 5))

        ttk.Label(self.root,
                  text="Output Directory:").grid(row=1,
                                                 column=0,
                                                 padx=20,
                                                 pady=(0, 5))
        ttk.Entry(self.root,
                  textvariable=self.output_path).grid(row=1,
                                                      column=1,
                                                      pady=(0, 5),
                                                      sticky='ew')
        ttk.Button(self.root,
                   text="Browse",
                   command=self.select_output_path).grid(row=1,
                                                         column=2,
                                                         pady=(0, 5),
                                                         padx=15)

    def setup_buttons(self):
        self.start_button = ttk.Button(self.root,
                                       text="Start Encoding",
                                       command=lambda:
                                       start_encoding(self.update_progress,
                                                      self.file_vars,
                                                      self.output_path))
        self.start_button.grid(row=3, column=0, columnspan=1,
                               pady=(10, 0), padx=(20, 5), sticky='w')

        self.stop_button = ttk.Button(self.root, text="Stop",
                                      command=lambda:
                                      stop_encoding(self.update_ui))
        self.stop_button.grid(row=3, column=1, columnspan=1,
                              pady=(10, 0), sticky='w')

    def setup_progress(self):
        self.progress = ttk.Progressbar(self.root, orient="horizontal",
                                        length=200, mode="determinate")
        self.progress.grid(row=4, column=0, columnspan=3,
                           padx=20, pady=(10, 0), sticky='ew')
        self.progress_label = tk.Label(self.root, text="0%",
                                       bg='systemTransparent')
        self.progress_label.grid(row=5, column=0, columnspan=3,
                                 padx=20, pady=(0, 15), sticky='ew')

    def update_ui(self, action):
        if action == 'start':
            self.start_button['state'] = 'disabled'
            self.stop_button['state'] = 'normal'
        elif action == 'stop':
            self.stop_button['state'] = 'disabled'

    def select_input_path(self):
        if path := filedialog.askdirectory():
            self.input_path.set(path)
            self.update_file_list()

    def select_output_path(self):
        if path := filedialog.askdirectory():
            self.output_path.set(path)

    def update_progress(self, progress_value):
        if progress_value == 'start':
            # Handle the start of encoding
            self.set_progress(0)  # Reset progress bar to 0%
            logging.debug("Encoding started.")
        elif progress_value == 'stop':
            # Handle the end of encoding
            logging.debug("Encoding stopped.")
        else:
            try:
                progress_num = float(progress_value)
                self.root.after(0, lambda: self.set_progress(progress_num))
            except ValueError:
                logging.debug(
                    f"Non-numerical progress value received: {progress_value}"
                    )

    def set_progress(self, progress_value):
        logging.debug(f"Setting progress to: {progress_value}%")
        self.progress['value'] = progress_value  # Update progress bar
        self.progress_label.config(text=f"{progress_value:.2f}%")

    def update_file_list(self):
        # Clear the current list
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # This will include both .mkv and .mp4 files
        video_files = glob.glob(f"{self.input_path.get()}/*")  # Get all files
        video_files = [file for file in video_files
                       if file.lower().endswith(('.mkv', '.mp4'))]

        video_files = sorted(video_files)

        for file in video_files:
            file_name = os.path.basename(file)  # Get just the file name
            file_size = os.path.getsize(file)   # Get the file size in bytes
            file_size_mb = file_size / 1000000  # Convert to megabytes

            # Calculate video length (in seconds) using OpenCV
            video = cv2.VideoCapture(file)
            fps = int(video.get(cv2.CAP_PROP_FPS))
            frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            video_length_seconds = frames / fps if fps > 0 else 0
            video.release()

            # Convert video length to hours, minutes, and seconds
            hours, minutes, seconds = seconds_to_hms(video_length_seconds)

            seconds = round(seconds, 2)
            hours = int(hours) if hours.is_integer() else hours
            minutes = int(minutes) if minutes.is_integer() else minutes

            var = tk.IntVar()
            self.file_vars[file] = var

            # Create a custom widget with label and checkbox
            frame = tk.Frame(self.scrollable_frame)
            frame.pack(anchor='w')

            label_text = f"{file_name}\nSize: {file_size_mb:.2f} MB\nLength: {hours}h {minutes}m {seconds}s"
            label = tk.Label(frame, text=label_text, justify='left')
            label.pack(side='right')

            separator = ttk.Separator(self.scrollable_frame,
                                      orient='horizontal')
            separator.pack(fill='x', padx=5)

            checkbox = tk.Checkbutton(frame, variable=var)
            checkbox.pack(side='left', padx=(20, 10))

    def run(self):
        self.root.mainloop()


def seconds_to_hms(seconds):
    # Convert seconds to hours, minutes, and seconds
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return hours, minutes, seconds
