import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox
import numpy as np
import librosa
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from PIL import Image, ImageFilter, ImageChops
import psutil
import os
from moviepy.editor import VideoClip, AudioFileClip, ImageClip, concatenate_videoclips, VideoFileClip

# Create the Tkinter UI
root = tk.Tk()
root.title("Waveform Video Maker")

# Initialize Tkinter variables
audio_file_path = tk.StringVar()
output_file_path = tk.StringVar()
start_image_path = tk.StringVar()
end_image_path = tk.StringVar()
bg_color_var = tk.StringVar(value="#000000")  # Default black
wf_color_var = tk.StringVar(value="#FFFFFF")  # Default white
circle_waveform_var = tk.BooleanVar(value=False)
draw_second_circle_var = tk.BooleanVar(value=False)  # New variable for second circle
aspect_ratio_9_16_var = tk.BooleanVar(value=False)
line_thickness_var = tk.DoubleVar(value=1)  # Default line thickness
background_image_path = tk.StringVar()
background_video_path = tk.StringVar()
blur_radius = tk.IntVar(value=30)  # Radius for the Gaussian blur to create the bloom effect
bloom_intensity = tk.DoubleVar(value=2)  # Intensity of the bloom effect

# Additional waveform settings
first_waveform_scale_var = tk.DoubleVar(value=1.0)  # Default scale for the first waveform
second_waveform_scale_var = tk.DoubleVar(value=1.0)  # Default scale for the second waveform
second_waveform_color_var = tk.StringVar(value="#FF0000")  # Default color for the second waveform

# Global variables for the linear waveform adjustments
waveform_horizontal_offset = 0  # Adjust to shift waveform left/right
waveform_vertical_scale = 1.0   # Adjust to scale waveform height

# Function to track and print memory usage
def print_memory_usage(frame_number):
    return
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    print(f"Frame {frame_number}: RSS={mem_info.rss / (1024 * 1024)} MB, VMS={mem_info.vms / (1024 * 1024)} MB")

def generate_video(limit_duration=None):
    # Get the input values from the UI
    audio_file = audio_file_path.get()
    output_file = output_file_path.get()
    title_card_start = start_image_path.get() if start_image_path.get() else None
    title_card_end = end_image_path.get() if end_image_path.get() else None
    bg_color = bg_color_var.get()
    wf_color = wf_color_var.get()
    circle_waveform = circle_waveform_var.get()
    draw_second_circle = draw_second_circle_var.get()  # New variable for second circle
    aspect_ratio_9_16 = aspect_ratio_9_16_var.get()
    line_thickness = line_thickness_var.get()
    background_image = background_image_path.get()
    background_video = background_video_path.get()
    first_waveform_scale = first_waveform_scale_var.get()
    second_waveform_scale = second_waveform_scale_var.get()
    second_waveform_color = second_waveform_color_var.get()
    blur_rad = blur_radius.get()
    bloom_intens = bloom_intensity.get()

    if not audio_file or not output_file:
        messagebox.showerror("Error", "Please select both audio and output files.")
        return

    try:
        # Load audio file
        y, sr = librosa.load(audio_file, sr=None)
        duration = librosa.get_duration(y=y, sr=sr)

        # If limit_duration is specified
        if limit_duration:
            duration = min(duration, 7)
            y = y[:int(sr * duration)]
        else:
            duration = librosa.get_duration(y=y, sr=sr)

        # Parameters for video
        if aspect_ratio_9_16:
            video_width = 1080
            video_height = 1920
        else:
            video_width = 1920
            video_height = 1080

        fps = 24

        # Time array for the truncated audio
        t_audio = np.linspace(0, duration, num=len(y))

        # Prepare figure for plotting
        dpi_value = 100  # Adjust if needed

        fig_size = (video_width / dpi_value, video_height / dpi_value)
        fig, ax = plt.subplots(figsize=fig_size, dpi=dpi_value, subplot_kw={'polar': circle_waveform})

        # Check for background video
        background_clip = None
        if background_video:
            try:
                background_clip = VideoFileClip(background_video).resize((video_width, video_height))
                print(f"Background video duration: {background_clip.duration} seconds")
            except Exception as e:
                print(f"Error loading background video: {e}")
                background_clip = None

        # Function to generate each frame
        def make_frame(t):
            frame_number = int(t * fps)
            print_memory_usage(frame_number)

            idx = (np.abs(t_audio - t)).argmin()
            window_size = int(sr * 0.05)  # 50 ms window
            start_idx = max(0, idx - window_size // 2)
            end_idx = min(len(y), idx + window_size // 2)
            y_frame = y[start_idx:end_idx]

            # Clear previous plot
            fig.clf()

            # Create new axes based on the waveform type
            if circle_waveform:
                ax = fig.add_subplot(111, polar=circle_waveform)
            else:
                ax = fig.add_subplot(111)

            # Set background color
            if bg_color.lower() == "#000000":
                ax.set_facecolor('none')
                fig.patch.set_alpha(0.0)
            else:
                ax.set_facecolor(bg_color)
                fig.patch.set_facecolor(bg_color)

            # Get current line thickness
            current_thickness = line_thickness

            # Draw the appropriate waveform
            if circle_waveform:
                draw_circle_waveform(ax, y_frame, wf_color, first_waveform_scale, second_waveform_color, second_waveform_scale, current_thickness, draw_second_circle)
            else:
                draw_linear_waveform(ax, y_frame, wf_color, current_thickness, video_width * 2)  # Overdraw width

            # Remove margins and padding
            fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
            ax.margins(0)
            ax.axis('off')

            # Convert plot to image with transparency
            canvas = FigureCanvas(fig)
            canvas.draw()

            # Use buffer_rgba() to retain transparency
            waveform_img = np.asarray(canvas.buffer_rgba())

            if circle_waveform:
                # No need to resize, the figure matches the video dimensions
                base_img = waveform_img
            else:
                # For linear waveform, resize the overdrawn image to video dimensions
                base_img = np.array(Image.fromarray(waveform_img).resize((video_width, video_height)))

            # Create the glow layer
            pil_base_image = Image.fromarray(base_img)
            glow_layer = pil_base_image.filter(ImageFilter.GaussianBlur(blur_rad))

            # Blend the glow layer with the base image
            glow_intensity_np = (np.array(glow_layer) * bloom_intens).astype(np.uint8)
            combined_img = ImageChops.add(pil_base_image, Image.fromarray(glow_intensity_np))

            # Convert combined image to numpy array
            final_image = np.array(combined_img)

            # Overlay the final image on the background
            if background_image:
                bg_img = Image.open(background_image).resize((video_width, video_height)).convert('RGBA')
                bg_img_np = np.array(bg_img)

                # Blend using alpha channel
                alpha_waveform = final_image[:, :, 3] / 255.0
                for c in range(3):
                    bg_img_np[:, :, c] = (1 - alpha_waveform) * bg_img_np[:, :, c] + alpha_waveform * final_image[:, :, c]

                final_frame = bg_img_np
            elif background_clip:
                bg_time = t % background_clip.duration
                bg_frame = background_clip.get_frame(bg_time)
                combined_img = np.array(bg_frame)

                # Blend using alpha channel
                alpha_waveform = final_image[:, :, 3] / 255.0
                for c in range(3):
                    combined_img[:, :, c] = (1 - alpha_waveform) * combined_img[:, :, c] + alpha_waveform * final_image[:, :, c]

                final_frame = combined_img
            else:
                # Create a solid RGBA background if no image or video is provided
                bg_color_rgb = Image.new("RGBA", (video_width, video_height), bg_color)
                final_frame = np.array(bg_color_rgb)

                # Blend the waveform with the background color
                alpha_waveform = final_image[:, :, 3] / 255.0
                for c in range(3):
                    final_frame[:, :, c] = (1 - alpha_waveform) * final_frame[:, :, c] + alpha_waveform * final_image[:, :, c]

            # Convert the RGBA frame to RGB
            final_frame_rgb = final_frame[:, :, :3]

            return final_frame_rgb.astype(np.uint8)

        # Generate video clip using MoviePy
        video_clip = VideoClip(make_frame, duration=duration).set_fps(fps)

        # Resize the video clip if necessary
        if circle_waveform:
            video_clip = video_clip.resize((video_width, video_height))
        else:
            # For linear waveform, we already resized in make_frame
            pass

        # Add audio to the video
        if limit_duration:
            audio_clip = AudioFileClip(audio_file).subclip(0, duration)  # Use the truncated waveform duration
        else:
            audio_clip = AudioFileClip(audio_file)

        video_clip = video_clip.set_audio(audio_clip)

        # Handle title card clips if provided
        clips = []
        if title_card_start:
            start_image_clip = ImageClip(title_card_start).set_duration(1.5).resize((video_width, video_height)).fadeout(1.5)
            clips.append(start_image_clip)

        clips.append(video_clip)  # Always add the main waveform video

        if title_card_end:
            end_image_clip = ImageClip(title_card_end).set_duration(1.5).resize((video_width, video_height)).fadein(1.5)
            clips.append(end_image_clip)

        # Combine the clips (with or without title cards)
        final_clip = concatenate_videoclips(clips, method="compose")

        # Write the video file
        final_clip.write_videofile(output_file, fps=fps, codec='libx264', audio_codec='aac', threads=4, preset='ultrafast')

        if limit_duration:
            messagebox.showinfo("Success", "10-second video generated successfully!")
        else:
            messagebox.showinfo("Success", "Full video generated successfully!")

    except Exception as e:
        print(f"An error occurred during video generation: {e}")
        messagebox.showerror("Error", str(e))

def generate_10_second_video():
    generate_video(limit_duration=10)

def select_audio_file():
    file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3 *.flac")])
    audio_file_path.set(file_path)

def select_output_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".mp4",
                                             filetypes=[("MP4 Video", "*.mp4")])
    output_file_path.set(file_path)

def select_start_image_file():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
    start_image_path.set(file_path)

def select_end_image_file():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
    end_image_path.set(file_path)

def pick_bg_color():
    color = colorchooser.askcolor(title="Select Background Color", initialcolor=bg_color_var.get())
    if color[1]:
        bg_color_var.set(color[1])

def pick_wf_color():
    color = colorchooser.askcolor(title="Select Waveform Color", initialcolor=wf_color_var.get())
    if color[1]:
        wf_color_var.set(color[1])

def pick_second_waveform_color():
    color = colorchooser.askcolor(title="Select Second Waveform Color", initialcolor=second_waveform_color_var.get())
    if color[1]:
        second_waveform_color_var.set(color[1])

def select_background_image_file():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
    background_image_path.set(file_path)

def select_background_video_file():
    file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mov")])
    background_video_path.set(file_path)

def draw_linear_waveform(ax, y_frame, wf_color, current_thickness, overdrawn_width):
    # Linear waveform
    x_values = np.linspace(0, overdrawn_width, len(y_frame)) + waveform_horizontal_offset

    y_smoothed = y_frame

    # Scale the waveform vertically
    y_smoothed_scaled = y_smoothed * waveform_vertical_scale

    # Plot the waveform
    for i in range(5, 0, -1):
        ax.plot(x_values, y_smoothed_scaled, color=wf_color,
                linewidth=current_thickness * (i * 0.5), alpha=0.1 * i)

    ax.plot(x_values, y_smoothed_scaled, color=wf_color, linewidth=current_thickness)

    # Set axes limits
    ax.set_xlim(0, overdrawn_width)
    ax.set_ylim(-1 * waveform_vertical_scale, 1 * waveform_vertical_scale)

    # Disable automatic scaling
    ax.autoscale(False)
    ax.axis('off')

def draw_circle_waveform(ax, y_frame, wf_color, first_waveform_scale, second_waveform_color, second_waveform_scale, current_thickness, draw_second_circle):
    # Circular (polar) waveform
    theta = np.linspace(0, 2 * np.pi, len(y_frame))

    # Smoothly connect the start and end points
    y_frame_smoothed = np.concatenate([y_frame, [y_frame[0]]])
    theta_smoothed = np.linspace(0, 2 * np.pi, len(y_frame_smoothed))

    # Base radius for the waveform
    base_radius = 1

    # Draw the second (larger) waveform by scaling the radius if enabled
    if draw_second_circle:
        for i in range(5, 0, -1):
            ax.plot(theta_smoothed, (base_radius + y_frame_smoothed) * second_waveform_scale,
                    color=second_waveform_color, linewidth=current_thickness * (i * 0.5), alpha=0.1 * i)
        ax.plot(theta_smoothed, (base_radius + y_frame_smoothed) * second_waveform_scale,
                color=second_waveform_color, linewidth=current_thickness)

    # Draw the first waveform
    for i in range(5, 0, -1):
        ax.plot(theta_smoothed, (base_radius + y_frame_smoothed) * first_waveform_scale,
                color=wf_color, linewidth=current_thickness * (i * 0.5), alpha=0.1 * i)
    ax.plot(theta_smoothed, (base_radius + y_frame_smoothed) * first_waveform_scale,
            color=wf_color, linewidth=current_thickness)

    # Set the limits to ensure everything fits in the plot
    ax.set_ylim([0, (base_radius + 1) * max(first_waveform_scale, second_waveform_scale)])
    ax.set_xlim([0, 2 * np.pi])
    ax.grid(False)
    ax.set_axis_off()

# Create UI elements
# Group: Inputs
inputs_frame = tk.LabelFrame(root, text="Inputs", padx=10, pady=10)
inputs_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky='ew')

tk.Label(inputs_frame, text="Audio File:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
tk.Entry(inputs_frame, textvariable=audio_file_path, width=50).grid(row=0, column=1, padx=5, pady=5)
tk.Button(inputs_frame, text="Browse", command=select_audio_file).grid(row=0, column=2, padx=5, pady=5)

tk.Label(inputs_frame, text="Output File:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
tk.Entry(inputs_frame, textvariable=output_file_path, width=50).grid(row=1, column=1, padx=5, pady=5)
tk.Button(inputs_frame, text="Browse", command=select_output_file).grid(row=1, column=2, padx=5, pady=5)

tk.Label(inputs_frame, text="Start Title Card Image:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
tk.Entry(inputs_frame, textvariable=start_image_path, width=50).grid(row=2, column=1, padx=5, pady=5)
tk.Button(inputs_frame, text="Browse", command=select_start_image_file).grid(row=2, column=2, padx=5, pady=5)

tk.Label(inputs_frame, text="End Title Card Image:").grid(row=3, column=0, sticky='e', padx=5, pady=5)
tk.Entry(inputs_frame, textvariable=end_image_path, width=50).grid(row=3, column=1, padx=5, pady=5)
tk.Button(inputs_frame, text="Browse", command=select_end_image_file).grid(row=3, column=2, padx=5, pady=5)

# Group: Backgrounds
backgrounds_frame = tk.LabelFrame(root, text="Backgrounds", padx=10, pady=10)
backgrounds_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky='ew')

tk.Label(backgrounds_frame, text="Background Image:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
tk.Entry(backgrounds_frame, textvariable=background_image_path, width=50).grid(row=0, column=1, padx=5, pady=5)
tk.Button(backgrounds_frame, text="Browse", command=select_background_image_file).grid(row=0, column=2, padx=5, pady=5)

tk.Label(backgrounds_frame, text="Background Video:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
tk.Entry(backgrounds_frame, textvariable=background_video_path, width=50).grid(row=1, column=1, padx=5, pady=5)
tk.Button(backgrounds_frame, text="Browse", command=select_background_video_file).grid(row=1, column=2, padx=5, pady=5)

# Group: Waveform Settings
waveform_settings_frame = tk.LabelFrame(root, text="Waveform Settings", padx=10, pady=10)
waveform_settings_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky='ew')

tk.Label(waveform_settings_frame, text="Background Color:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
tk.Entry(waveform_settings_frame, textvariable=bg_color_var, width=20).grid(row=0, column=1, sticky='w', padx=5, pady=5)
tk.Button(waveform_settings_frame, text="Select Color", command=pick_bg_color).grid(row=0, column=2, padx=5, pady=5)

tk.Label(waveform_settings_frame, text="Waveform Color:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
tk.Entry(waveform_settings_frame, textvariable=wf_color_var, width=20).grid(row=1, column=1, sticky='w', padx=5, pady=5)
tk.Button(waveform_settings_frame, text="Select Color", command=pick_wf_color).grid(row=1, column=2, padx=5, pady=5)

tk.Label(waveform_settings_frame, text="Line Thickness:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
tk.Scale(waveform_settings_frame, from_=0.1, to=10, resolution=0.1, orient=tk.HORIZONTAL, variable=line_thickness_var).grid(row=2, column=1, columnspan=2, padx=5, pady=5)

# Group: Circular Waveform Settings
circular_waveform_frame = tk.LabelFrame(waveform_settings_frame, text="Circular Waveform Settings", padx=10, pady=10)
circular_waveform_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky='ew')

tk.Checkbutton(circular_waveform_frame, text="Enable Circular Waveform", variable=circle_waveform_var).grid(row=0, column=0, sticky='w', padx=5, pady=5)
tk.Checkbutton(circular_waveform_frame, text="Draw Second Circle", variable=draw_second_circle_var).grid(row=1, column=0, sticky='w', padx=5, pady=5)

tk.Label(circular_waveform_frame, text="First Waveform Scale:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
tk.Scale(circular_waveform_frame, from_=0.1, to=5.0, resolution=0.1, orient=tk.HORIZONTAL, variable=first_waveform_scale_var).grid(row=2, column=1, columnspan=2, padx=5, pady=5)

tk.Label(circular_waveform_frame, text="Second Waveform Scale:").grid(row=3, column=0, sticky='e', padx=5, pady=5)
tk.Scale(circular_waveform_frame, from_=0.1, to=5.0, resolution=0.1, orient=tk.HORIZONTAL, variable=second_waveform_scale_var).grid(row=3, column=1, columnspan=2, padx=5, pady=5)

tk.Label(circular_waveform_frame, text="Second Waveform Color:").grid(row=4, column=0, sticky='e', padx=5, pady=5)
tk.Entry(circular_waveform_frame, textvariable=second_waveform_color_var, width=20).grid(row=4, column=1, sticky='w', padx=5, pady=5)
tk.Button(circular_waveform_frame, text="Select Color", command=pick_second_waveform_color).grid(row=4, column=2, padx=5, pady=5)

# Group: Bloom Settings
bloom_settings_frame = tk.LabelFrame(root, text="Bloom Settings", padx=10, pady=10)
bloom_settings_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky='ew')

tk.Label(bloom_settings_frame, text="Blur Radius:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
tk.Scale(bloom_settings_frame, from_=1, to=100, orient=tk.HORIZONTAL, variable=blur_radius).grid(row=0, column=1, columnspan=2, padx=5, pady=5)

tk.Label(bloom_settings_frame, text="Bloom Intensity:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
tk.Scale(bloom_settings_frame, from_=0.1, to=5.0, resolution=0.1, orient=tk.HORIZONTAL, variable=bloom_intensity).grid(row=1, column=1, columnspan=2, padx=5, pady=5)

# Group: Other Settings
other_settings_frame = tk.LabelFrame(root, text="Other Settings", padx=10, pady=10)
other_settings_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky='ew')

tk.Checkbutton(other_settings_frame, text="9:16 Aspect Ratio", variable=aspect_ratio_9_16_var).grid(row=0, column=1, sticky='w', padx=5, pady=5)

# Generate Video Buttons
tk.Button(root, text="Generate Full Video", command=generate_video).grid(row=5, column=1, padx=5, pady=10)
tk.Button(root, text="Generate Preview Video", command=generate_10_second_video).grid(row=6, column=1, padx=5, pady=5)

root.mainloop()
