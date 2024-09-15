
# WaveformVideoMaker

WaveformVideoMaker is a lightweight tool designed for fast and easy audio waveform video generation. While it focuses on simplicity and speed, it still offers a range of customizable features to create visually appealing videos with minimal effort.
<img src="https://github.com/user-attachments/assets/6af4c296-6226-4967-97ec-000210598b2a" width="50%">

## Features

- Generate videos with circular or linear waveform visualizations.
- Customize waveform colors, scales, and line thickness.
- Add title card images at the start and end of the video.
- Support for background images and videos.
- Apply bloom effects to the waveforms with adjustable blur radius and intensity.
- Choose between standard (16:9) and portrait (9:16) aspect ratios.
- Create full-length videos or 10-second previews.

## Installation

To get started, clone this repository and install the required dependencies:

```bash
pip install numpy librosa matplotlib Pillow psutil moviepy
```

Alternatively, you can install the dependencies using the provided `requirements.txt` file:

```bash
pip install -r requirements.txt
```

## Usage

1. Run the script to open the WaveformVideoMaker interface:

```bash
python waveform_video_maker.py
```

2. Use the interface to:
   - Select an audio file and specify the output file path.
   - Optionally, add start and end title card images.
   - Customize the waveform and background settings.
   - Adjust bloom settings for glow effects.
   - Choose the video aspect ratio (16:9 or 9:16).

3. Click on "Generate Full Video" to create a video with the full audio length or "Generate 10-second Video" for a short preview.

## Requirements

- Python 3.6+
- numpy
- librosa
- matplotlib
- Pillow
- psutil
- moviepy

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Notes

- When making images or videos ensure that it is the correct aspect ratio, 16/9 or 9/16 if that is chosen or else it will stretch the assets oddly.

- It's using MoviePy isn't exactly fast but saves doing a frame every save.

- At this time I won't be adding too many new features. 

- Background videos must loop correctly or be longer then your 


