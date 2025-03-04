import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import kokoro_onnx
import soundfile as sf
from pathlib import Path
import numpy as np
import time
import pygame.mixer
import os

# Initialize pygame mixer
pygame.mixer.init()

# Assuming model files are in the same directory as this script
MODEL_PATH = Path("kokoro-v1.0.onnx")
VOICES_PATH = Path("voices-v1.0.bin")
MODEL_NAME = "kokoro"
PLACEHOLDER_TEXT = "e.g., my_audio.wav (leave blank for auto-name)"

# Create output directory if it doesn't exist
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# Load available voices from voices-v1.0.bin
def get_available_voices(voices_path):
    try:
        voices_data = np.load(voices_path, allow_pickle=True)
        return list(voices_data.keys())
    except Exception as e:
        return [f"Error loading voices: {str(e)}"]

def generate_output_filename(base_name=MODEL_NAME, voice_name=""):
    """Generate a unique filename with model name, voice name, and timestamp."""
    timestamp = int(time.time() * 1000)
    return f"{base_name}_{voice_name}_{timestamp}.wav"

def is_file_ready(filepath):
    """Check if the file exists and is not locked."""
    path = Path(filepath)
    if not path.exists():
        return False
    try:
        with open(filepath, 'rb') as f:
            return True
    except IOError:
        return False

def convert_and_save():
    # Disable button and change text during processing
    convert_button.config(text="Processing...", state=DISABLED)
    root.update()  # Force update the UI
    
    text = text_entry.get("1.0", END).strip()
    voice = voice_var.get()
    output_filename = output_entry.get().strip()

    if not text:
        status_label.config(text="Error: Please enter some text.", bootstyle=DANGER)
        # Re-enable button
        convert_button.config(text="Convert and Save", state=NORMAL)
        return

    # If output_file is empty or still the placeholder, generate a dynamic filename
    if not output_filename or output_filename == PLACEHOLDER_TEXT:
        output_filename = generate_output_filename(voice_name=voice)
    elif not output_filename.endswith(".wav"):
        output_filename += ".wav"
    
    # Create full path to the output file in the output directory
    output_file = OUTPUT_DIR / output_filename

    try:
        kokoro = kokoro_onnx.Kokoro(MODEL_PATH, VOICES_PATH)
        lang = "en-us" if voice.startswith(('af', 'am', 'bf', 'bm')) else "ja-jp"
        samples, sample_rate = kokoro.create(
            text=text,
            voice=voice,
            speed=1.0,
            lang=lang
        )
        sf.write(output_file, samples, sample_rate)
        
        status_label.config(text=f"Success: Audio saved as {output_file}", bootstyle=SUCCESS)
        
        # Play the audio if the checkbox is checked
        if play_var.get():
            timeout = 2.0  # Max wait time in seconds
            start_time = time.time()
            while not is_file_ready(output_file) and (time.time() - start_time) < timeout:
                time.sleep(0.1)  # Check every 100ms
            
            if not is_file_ready(output_file):
                status_label.config(text=f"Error: File {output_file} not ready for playback", bootstyle=DANGER)
                return
                
            try:
                pygame.mixer.music.load(output_file)
                pygame.mixer.music.play()
                # Wait for playback to finish (remove this block for non-blocking playback)
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
            except Exception as play_error:
                status_label.config(text=f"Error playing audio: {str(play_error)}", bootstyle=DANGER)
    except Exception as e:
        status_label.config(text=f"Error: {str(e)}", bootstyle=DANGER)
    finally:
        # Re-enable button regardless of success or failure
        convert_button.config(text="Convert and Save", state=NORMAL)

# Placeholder functionality for output_entry
def on_entry_focus_in(event):
    if output_entry.get() == PLACEHOLDER_TEXT:
        output_entry.delete(0, END)
        output_entry.config(foreground="black")

def on_entry_focus_out(event):
    if not output_entry.get().strip():
        output_entry.insert(0, PLACEHOLDER_TEXT)
        output_entry.config(foreground="gray")

# Function to toggle theme
def toggle_theme():
    current_theme = root.style.theme_use()
    if current_theme == "flatly":  # Currently light theme
        root.style.theme_use("darkly")  # Switch to dark theme
        theme_button.config(text="☀️")  # Sun icon for switching to light mode
    else:
        root.style.theme_use("flatly")  # Switch to light theme
        theme_button.config(text="🌙")  # Moon icon for switching to dark mode
    
    # Update placeholder text color for current theme
    if output_entry.get() == PLACEHOLDER_TEXT:
        output_entry.config(foreground="gray" if current_theme != "flatly" else "#6c757d")

# Set up the main window with ttkbootstrap
root = ttk.Window(themename="flatly")
root.title("Kokoro ONNX GUI")
root.geometry("600x600")  # Increased height for status message
root.resizable(False, False)

# Main frame
main_frame = ttk.Frame(root, padding=10)
main_frame.pack(fill=BOTH, expand=True)

# Header frame for title and theme toggle
header_frame = ttk.Frame(main_frame)
header_frame.pack(fill=X, pady=5)

# Title on the left
title_label = ttk.Label(header_frame, text="Kokoro ONNX GUI", font=("Helvetica", 16, "bold"))
title_label.pack(side=LEFT)

# Theme toggle button on the right
theme_button = ttk.Button(header_frame, text="🌙", width=3, command=toggle_theme)
theme_button.pack(side=RIGHT)

# Text input
ttk.Label(main_frame, text="Enter Text:", font=("Helvetica", 12)).pack(anchor=W, pady=5)
text_entry = ttk.Text(main_frame, height=5, width=60, font=("Helvetica", 10))
text_entry.pack(fill=X, pady=5)
text_entry.insert("1.0", "Hello, this is a test!")

# Voice selection
ttk.Label(main_frame, text="Select Voice:", font=("Helvetica", 12)).pack(anchor=W, pady=5)
voice_var = ttk.StringVar()
available_voices = get_available_voices(VOICES_PATH)
voice_menu = ttk.Combobox(main_frame, textvariable=voice_var, values=available_voices, state="readonly")
voice_menu.pack(fill=X, pady=5)
voice_menu.set(available_voices[0] if available_voices else "No voices available")

# Output file
ttk.Label(main_frame, text="Output File Name (optional):", font=("Helvetica", 12)).pack(anchor=W, pady=5)
output_entry = ttk.Entry(main_frame, width=60, font=("Helvetica", 10))
output_entry.pack(fill=X, pady=5)
output_entry.insert(0, PLACEHOLDER_TEXT)
output_entry.config(foreground="gray")
output_entry.bind("<FocusIn>", on_entry_focus_in)
output_entry.bind("<FocusOut>", on_entry_focus_out)

# Play audio checkbox
play_var = ttk.BooleanVar(value=False)  # Default to unchecked
play_checkbox = ttk.Checkbutton(
    main_frame,
    text="Play audio after conversion",
    variable=play_var,
    bootstyle="primary"
)
play_checkbox.pack(pady=10)

# Convert button
convert_button = ttk.Button(main_frame, text="Convert and Save", command=convert_and_save, bootstyle=PRIMARY)
convert_button.pack(pady=15)

# Status label with more space
status_frame = ttk.Frame(main_frame)
status_frame.pack(fill=X, pady=10, expand=True)
status_label = ttk.Label(status_frame, text="Ready", font=("Helvetica", 10), bootstyle=INFO, wraplength=580)
status_label.pack(pady=5)

# Run the application
root.mainloop()