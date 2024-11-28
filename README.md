# Freecorder

Freecorder is minimalistic NVR (Network Video Recorder). It was designed to record IP camera footage 24/7 in a rolling manner. It is simple to set up, runs on almost every platform (Docker or bare metal) and uses very little resources.

![Screenshot](images/screenshot.png)

The following features make this project unique:
- Ultra low resource usage: this project was designed to run with minimal CPU and memory footprint. No GPU/NPU is required.
- Flexible deployment options: you can run this project bare metal, e.g. on a Rasberry Pi, or deploy it via Docker, e.g. on your NAS.
- Total simplicity: the user interface is clean, modern, minimalistic and very easy to use.

## Features

- 24/7 continuous video recording from an RTSP stream (IP camera).
- Audio and video support.
- Web interface for browsing all recorded clips.
- Direct playback of clips via the web interface.
- Direct downloading of clips via the web interface.

## What this project does *NOT* offer

In order to achieve minimal hardware resource usage, several features implemented by other NVR systems are not available in this project:
- Live video view
- Motion detection
- Object detection

If you require these features, take a look at other projects like Frigate, Shinobi or ZoneMinder.

# Configuration

Todo

# Deployment

## Via Docker

Todo

## Bare Metal

Todo

# Used Assets and Libraries

The following assets and libraries are used by this project:

- [PicoCSS CSS Framework](https://picocss.com/)
- [ffmpeg](https://ffmpeg.org/)
