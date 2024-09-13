from flask import Flask, render_template, send_from_directory
import os
import re

app = Flask(__name__)

# Load BASE_DIR from configuration file
def load_base_dir(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()

# Set the path to your configuration file
CONFIG_FILE_PATH = 'putyourfolderpath.txt'
BASE_DIR = load_base_dir(CONFIG_FILE_PATH)

def extract_number(folder_name):
    # Extract numeric part from the folder name using regular expression
    match = re.match(r"(\d+)", folder_name)
    return int(match.group(1)) if match else float('inf')

def get_sorted_folders(base_dir):
    # List all folders in the base directory
    folders = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f))]
    # Sort folders based on numerical prefix extracted from folder names
    sorted_folders = sorted(folders, key=lambda f: extract_number(f))
    # Create a list of tuples with index and folder name, formatted with leading zeros
    numbered_folders = [(f"{i + 1:02}", folder) for i, folder in enumerate(sorted_folders)]
    return numbered_folders

def get_videos_and_resources(folder_name):
    folder_path = os.path.join(BASE_DIR, folder_name)
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    
    videos = []
    resources = []
    for file in files:
        if file.endswith('.mp4'):
            video_name = file[:-4]  # Remove .mp4
            description_file = f"{video_name}.txt"
            description = "No description available."
            if description_file in files:
                with open(os.path.join(folder_path, description_file), 'r') as f:
                    description = f.read()
            videos.append((video_name, file, description))
        elif file.endswith('.vtt') or file.endswith('.pdf') or file.endswith('.html') or file.endswith('.txt'):
            resources.append(file)

    # Ensure videos are sorted correctly
    videos.sort(key=lambda v: int(re.match(r"(\d+)", v[0]).group(1)) if re.match(r"(\d+)", v[0]) else float('inf'))
    
    return videos, resources

@app.route('/')
def index():
    numbered_folders = get_sorted_folders(BASE_DIR)
    return render_template('index.html', folders=numbered_folders)

@app.route('/<folder_name>/')
def folder(folder_name):
    videos, resources = get_videos_and_resources(folder_name)
    current_video = videos[0] if videos else (None, None, "No video available")
    return render_template('folder.html', folder_name=folder_name, videos=videos, resources=resources, current_video=current_video)

@app.route('/<folder_name>/file/<file_name>')
def file(folder_name, file_name):
    folder_path = os.path.join(BASE_DIR, folder_name)
    return send_from_directory(folder_path, file_name)

if __name__ == '__main__':
    app.run(debug=True)
