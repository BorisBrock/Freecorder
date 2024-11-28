import os
import time
import logging
import subprocess
import signal
import shutil
from datetime import datetime
from pathlib import Path

# Project imports
from config import Config


# Globals
config = None
run = True
process = None


# Sets the time zone environment variable
def set_time_zone(tz):
    '''Sets the time zone environment variable.'''
    if tz is None:
        logging.warning("Recorder: Warning: No time zone set")
    else:
        logging.info(f"Recorder: Setting tme zone to {tz}")
        os.environ['TZ'] = tz
        time.tzset()
        logging.info(f"Recorder: Time is now {time.strftime('%X %x %Z')}")


# This is called when SIGTERM is received
def handler_stop_signals(signum, frame):
    global run
    logging.debug("SIGTERM/SIGINT received")
    run = False
    if process:
        logging.info("stopping ffmpeg process")
        process.terminate()
        logging.info("ffmpeg terminated")


# Gets the given folder's size
def get_folder_size_mb(folder_path):
    return int(sum(os.path.getsize(os.path.join(folder_path, file)) for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))) / 1024 /1024)


# Checks if the disk usage limit is reached and deletes the oldest files
def cleanup_files():
    logging.info("Checking disk usage:")
    while True:
        current_usage_mb = get_folder_size_mb("recordings")
        max_allowed_usage_mb = config.config_data['recorder']['max_disk_usage_mb']
        logging.info(f"Currently used: {current_usage_mb} MB, allowed disk usage: {max_allowed_usage_mb} MB")
        if current_usage_mb <= max_allowed_usage_mb:
            logging.info("Disk usage ok. No further cleanup required")
            break
        # Delete oldest file
        folder = Path("recordings")
        files = [file for file in folder.iterdir() if file.is_file()]
        if not files:
            logging.info("No files found to delete")
            break
        oldest_file = min(files, key=lambda file: file.stat().st_mtime)
        logging.info(f"Deleting oldest clip: '{oldest_file.name}'")
        oldest_file.unlink()


# Records a clip from the camera stream to disk
def record_file():
    global process
    if os.path.exists("recordings/current.mp4"):
        os.remove("recordings/current.mp4")
    logging.info("Recording new clip")
    time_string_start = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    stream_url = config.config_data['recorder']['stream_url']
    clip_duration = config.config_data['recorder']['clip_duration']
    command = ["ffmpeg", "-i", stream_url, "-c:v", "copy", "-c:a", "aac",  "-b:a", "128k", "-t", clip_duration, "recordings/current.mp4"]
    process = subprocess.Popen(command)
    # Wait for ffmpeg to finish
    process.wait()
    time_string_end = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    if process.returncode == 0:
        clip_name = f"Rec_{time_string_start}_{time_string_end}.mp4"
        logging.info(f"Clip '{clip_name}' recorded successfully")
        os.rename("recordings/current.mp4", f"recordings/{clip_name}")
    else:
        logging.error(f"ffmpeg failed with exit code {process.returncode}")
        logging.error(process.stderr)


# Main loop
def main():
    '''Main loop.'''
    global config
    global run

    # Set up signal handlers
    signal.signal(signal.SIGINT, handler_stop_signals)
    signal.signal(signal.SIGTERM, handler_stop_signals)

    # Set up logging
    logging.basicConfig(
        filename='data/recorder.log', filemode='w',
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

    # Print version
    logging.info(f"Starting Freecorder recorder")

    # Read the configuration from disk
    try:
        logging.info("Reading backend configuration from config.yml")
        config = Config("data/config.yml")
    except Exception:
        exit()

    # Set log level
    logging.getLogger().setLevel(config.log_level)

    # Set time zone
    set_time_zone(config.config_data.get("time_zone"))

    # Recorder main loop
    logging.debug("Entering main loop")
    while run:
        try:
            cleanup_files()
            record_file()
        except Exception:
            logging.exception("Recording stream failed")
            time.sleep(5.0)

    # Exit
    logging.info("Exiting main loop")
    logging.info("Shutting down gracefully")


# Main entry point of the application
if __name__ == "__main__":
    main()
