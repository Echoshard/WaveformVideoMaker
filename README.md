
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
- Title cards and backgrounds are optional

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
- Aspect Ratio: When creating images or videos, ensure that they match the selected aspect ratio (16:9 or 9:16). If the assets do not match the chosen ratio, they may appear stretched or distorted.

- Processing Speed: This tool uses MoviePy, which is not the fastest option for video processing but offers a faster alternative to saving each frame individually. Processing time depends on the length of your video. It's recommended to start with a preview video to verify the appearance before generating the full-length video. You can monitor the progress in the console.

- Background Videos: Ensure that background videos loop seamlessly or are longer than the audio track to avoid abrupt endings or visual inconsistencies.


