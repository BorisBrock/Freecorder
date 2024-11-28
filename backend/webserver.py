import json
import os
from datetime import date
from pathlib import Path
import shutil
import logging
import traceback
from flask import Flask, request, Response, send_from_directory, send_file, abort
from flask_compress import Compress

# Project imports
from config import Config


# Globals
config = None


# Main Flask web server application
app = Flask(__name__)
Compress(app)


# Serves the index.html
@app.route('/')
def get_index():
    """Serves the index.html."""
    return send_from_directory("../site", "index.html")


# Video clip streaming
@app.route('/video/<filename>')
def stream_video(filename):
    """Video clip streaming."""
    try:
        logging.info(f"Video stream requested: '{filename}'")
        # Full path to the video file
        video_path = f'/recordings/{filename}'
        
        # Get the range header from the request
        range_header = request.headers.get('Range', None)
        if not range_header:
            # No range requested, send the full file
            return send_file(video_path, mimetype='video/mp4')

        # Parse the range header
        range_start, range_end = range_header.replace('bytes=', '').split('-')
        range_start = int(range_start)
        file_size = os.path.getsize(video_path)
        range_end = int(range_end) if range_end else file_size - 1
        
        if range_start >= file_size or range_end >= file_size:
            abort(416, 'Requested Range Not Satisfiable')

        # Open the file and read the required bytes
        with open(video_path, 'rb') as f:
            f.seek(range_start)
            data = f.read(range_end - range_start + 1)
        
        # Create the response with partial content
        response = Response(data, status=206, mimetype='video/mp4')
        response.headers.add('Content-Range', f'bytes {range_start}-{range_end}/{file_size}')
        response.headers.add('Accept-Ranges', 'bytes')
        return response

    except Exception as e:
        logging.exception("An exception occurred:")
        logging.exception(str(e))
        return f"Error: {str(e)}", 500


# Lets the user download clips
@app.route("/api/download", methods=['GET'])
def handle_api_download():
    """Lets the user download clips."""
    try:
        _file = request.args['file']
        return send_file("/recordings/" + _file, as_attachment=True)
    except Exception:
        logging.exception("Error while processing HTTP REST request")
        exception_string = traceback.print_exc()
        data = {"state": "error", "message": exception_string}
        return json.dumps(data), 404
    

# Returns the list of available files as a JSON array
@app.route("/api/files", methods=['GET'])
def handle_api_files():
    """Returns the list of available files as a JSON array."""
    try:
        folder = Path("recordings")
        files = [{"name": file.name, "size": file.stat().st_size}
                 for file in folder.glob("*.mp4")
                 if file.is_file()]
        data = {
            "state": "ok",
            "files": files
        }
        return json.dumps(data)
    except Exception:
        logging.exception("Error while processing HTTP REST request")
        data = {"state": "error"}
        return json.dumps(data)


# Returns current server statistics as a JSON object
@app.route("/api/stats", methods=['GET'])
def handle_api_stats():
    """Returns current server statistics as a JSON object."""
    try:
        total, used, free = shutil.disk_usage("recordings")
        data = {
            "state": "ok",
            "disk_space_total_mb": f"{total / 1024 / 1024:.2f}",
            "disk_space_used_mb": f"{used / 1024 / 1024:.2f}",
            "disk_space_free_mb": f"{free / 1024 / 1024:.2f}"
        }
        return json.dumps(data)
    except Exception:
        logging.exception("Error while processing HTTP REST request")
        data = {"state": "error"}
        return json.dumps(data)


# Serves all other static files
@app.route('/<path:path>')
def get_file(path):
    """Serves all other static files."""
    return send_from_directory("../site", path)


# Main loop
def main():
    """Implements the main loop."""

    global config

    # Set up logging
    logging.basicConfig(
        filename='data/webserver.log', filemode='w',
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

    # Print version
    logging.info(f"Starting Freecorder webserver")

    # Read the configuration from disk
    try:
        logging.info("Reading configuration from config.yml")
        config = Config("data/config.yml")
    except Exception:
        exit()

    # Set log level
    logging.getLogger().setLevel(config.log_level)

    # Start the web server
    from waitress import serve
    serve(app,
          host=config.config_data['webserver']['ip'],
          port=config.config_data['webserver']['port'])

    # Exit
    logging.info("Exiting main loop")
    logging.info("Shutting down gracefully")


# Main entry point of the application
if __name__ == "__main__":
    main()
