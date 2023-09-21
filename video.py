import tempfile
import os
from pathlib import Path

from PIL import Image

import moviepy.editor as mpe
from moviepy.editor import concatenate_videoclips, concatenate_audioclips
from moviepy.editor import concatenate_videoclips, CompositeVideoClip
from moviepy.video.fx.all import fadein, fadeout
from moviepy.audio.fx.all import audio_loop, audio_fadein, audio_fadeout

import numpy as np
import pandas as pd

RESOLUTIONS = {
    "8K": (7680, 4320),
    "4K": (3840, 2160),
    "2K": (2560, 1440),
    "FullHD": (1920, 1080),
    "HD": (1280, 720),
    "SD": (854, 480)
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_files_from_directory(directory, extension):
    """
    Get all files with a specific extension from a directory.
    
    Args:
        directory (str): Path to the directory.
        extension (str): File extension (e.g., ".jpg" or ".mp3").
    
    Returns:
        list: List of file paths.
    """
    directory_path = Path(directory)
    return sorted(directory_path.glob(f"*{extension}"))

def repeat_audio(audio_clip, nloops=None, duration=None):
    return audio_loop(audio_clip, nloops=nloops, duration=duration)

def add_static_image_to_audio(image, audio):
    """Create and save a video file to `output_path` after 
    combining a static image that is located in `image_path` 
    with an audio file in `audio_path`"""

    # use set_audio method from image clip to combine the audio with the image
    video_clip = image.set_audio(audio)
    # specify the duration of the new clip to be the duration of the audio clip
    video_clip.duration = audio.duration
    # set the FPS to 1
    video_clip.fps = 1
    return video_clip

def mask_video_background(video, color=None, thr=0, softness=3):
    if color is None:
        color = [0, 1, 0]

    masked_video = video.fx(mpe.vfx.mask_color, color=color, thr=thr, s=softness)
    return masked_video

def overlay_masked_video_to_static_image(video, image):
    new_video = mpe.CompositeVideoClip([image, video]).set_duration(video.duration)
    return new_video

def overlay_effect(image_clip, effect_clip, background_color=None, effect_color=None):
    """Add effect to an image."""
    if background_color is None:
        # TODO: Detect background color automatically
        background_color = [0, 1, 0]
        #background_color = [1, 141, 34]

    effect_video = mask_video_background(
        effect_clip, 
        color=background_color,
        thr=200,
        softness=3)

    # applying color effect
    if effect_color is not None:
        # TODO: Choose a color from the clip automatically
        effect_video = effect_video.fx(mpe.vfx.colorx, np.asarray(effect_color))

    return overlay_masked_video_to_static_image(effect_video, image_clip)

def match_audio_and_video_duration(audio, video, duration):
    new_audio = audio_loop(audio, duration=duration)
    new_video = video.loop(duration=duration)
    return new_audio, new_video

def merge_audio_and_video(audio, video, duration):
    new_audio, new_video = match_audio_and_video_duration(audio, video, duration)
    new_video = new_video.set_audio(new_audio)
    return new_video


def move_file(source, destination):
    """
    Move a file from source to destination.
    
    Args:
        source (str): Path to the file to be moved.
        destination (str): Path to the directory where the file will be moved.
    
    Returns:
        None
    """
    source_path = Path(source)
    destination_path = Path(destination)
    
    source_path.rename(destination_path / source_path.name)


# ============================================================================
# MAIN FUNCTIONS
# ============================================================================


def image2clip(path, resolution):
    """Read and resize image."""
    return mpe.ImageClip(path).resize(resolution)

def video2clip(path, resolution):
    """Read and resize video."""
    return mpe.VideoFileClip(path).resize(resolution)



def add_effect_to_image(image_path, effect_path, output_path, background_color=None, effect_color=None, resolution="FullHD"):

    resolution = RESOLUTIONS[resolution]
    image_clip = image2clip(image_path, resolution)
    effect_clip = video2clip(effect_path, resolution)
    
    clip = overlay_effect(image_clip, effect_clip, background_color, effect_color)
    
    # Write file 
    clip.write_videofile(output_path, threads=8)


def add_audio_to_video(video_path, audio_path, output_path, resolution="FullHD", duration_min=1., fadein_sec=5):
    """Create a video with music."""

    resolution = RESOLUTIONS[resolution]
    duration_sec = duration_min * 60.  # to seconds

    # Create the base clip
    clip = video2clip(video_path, resolution)

    # Add audio to clip
    audio_clip = mpe.AudioFileClip(audio_path)
    clip = merge_audio_and_video(audio_clip, clip, duration=duration_sec)

    # Fade in
    if fadein_sec>0:
        clip = audio_fadein(clip, fadein_sec)

    # Render video
    clip.write_videofile(output_path, threads=8)

def add_audio_to_image(image_path, audio_path, output_path, resolution="FullHD", duration_min=1.):
    """Create an image video with music."""

    if os.path.exists(output_path):
        raise FileExistsError(f"Output file {output_path} already exists.")

    resolution = RESOLUTIONS[resolution]
    duration_sec = duration_min * 60.  # to seconds

    # Create the base clip
    clip = image2clip(image_path, resolution)
    clip = clip.set_duration(10.)
    clip.fps = 1

    # Add audio to clip
    audio_clip = mpe.AudioFileClip(audio_path)
    clip = merge_audio_and_video(audio_clip, clip, duration=duration_sec)

    # Render video
    clip.write_videofile(output_path, threads=8)

def add_fadein_to_audio(audioclip, fadein_duration):
    """
    Add a fade-in effect to the beginning of an audio clip.
    
    Args:
        audioclip (AudioClip): The audio clip to which the fade-in effect will be added.
        fadein_duration (float): Duration of the fade-in effect in seconds.
    
    Returns:
        AudioClip: Audio clip with the fade-in effect.
    """
    # return audioclip.fx(fadein, fadein_duration)
    return audio_fadein(audioclip, fadein_duration)

def add_fadeout_to_audio(audioclip, fadeout_duration):
    """
    Add a fade-out effect to the end of an audio clip.
    
    Args:
        audioclip (AudioClip): The audio clip to which the fade-out effect will be added.
        fadeout_duration (float): Duration of the fade-out effect in seconds.
    
    Returns:
        AudioClip: Audio clip with the fade-out effect.
    """
    # return audioclip.fx(fadeout, fadeout_duration)
    return audio_fadeout(audioclip, fadeout_duration)

def add_fadein_to_video(videoclip, fadein_duration):
    """
    Add a fade-in effect to the beginning of a video clip.
    
    Args:
        videoclip (VideoClip): The video clip to which the fade-in effect will be added.
        fadein_duration (float): Duration of the fade-in effect in seconds.
    
    Returns:
        VideoClip: Video clip with the fade-in effect.
    """
    # Fade in from black
    faded_video = videoclip.fx(fadein, fadein_duration)

    # # Apply Gaussian blur effect that decreases over time
    # blured_video = faded_video.fx(blur, lambda t: max(0, fadein_duration - t))
    
    # return CompositeVideoClip([faded_video, blured_video])
    return faded_video

def add_fadeout_to_video(videoclip, fadeout_duration):
    """
    Add a fade-out effect to the end of a video clip.
    
    Args:
        videoclip (VideoClip): The video clip to which the fade-out effect will be added.
        fadeout_duration (float): Duration of the fade-out effect in seconds.
    
    Returns:
        VideoClip: Video clip with the fade-out effect.
    """
    # Fade out to black
    faded_video = videoclip.fx(fadeout, fadeout_duration)
    
    # # Apply Gaussian blur effect that increases over time
    # blured_video = faded_video.fx(blur, lambda t: max(0, t - (videoclip.duration - fadeout_duration)))
    
    # return CompositeVideoClip([faded_video, blured_video])
    return faded_video

def create_playlist_video(image_files, music_files, resolution="FullHD"):
    """
    Create a video that plays all audio tracks in sequence, 
    changing the image displayed with each new track.
    
    Args:
        image_files (list): List of images paths.
        music_files (list): List of music track paths.
        resolution (str): Desired video resolution (default is "FullHD").
    
    Returns:
        final_video
    """

    # Ensure that the number of images matches the number of music tracks
    if len(image_files) != len(music_files):
        raise ValueError("The number of images must match the number of music tracks.")

    video_clips = []
    audio_clips = []

    for i, (image_file, music_file) in enumerate(zip(image_files, music_files)):
        # Create an image clip for the duration of the music track
        audio_clip = mpe.AudioFileClip(str(music_file))
        image_clip = image2clip(str(image_file), RESOLUTIONS[resolution])
        image_clip = image_clip.set_duration(audio_clip.duration)
      
        # Apply fade-in and fade-out effects to the video for transitions
        image_clip = add_fadein_to_video(image_clip, 2)
        image_clip = add_fadeout_to_video(image_clip, 2)

        # Apply fadin and fadeout to audio tracks, except begining and end of playlist
        if i != 0:
            audio_clip = add_fadein_to_audio(audio_clip, 2)
        if i != len(image_files):
            audio_clip = add_fadeout_to_audio(audio_clip, 2)
        
        video_clips.append(image_clip)
        audio_clips.append(audio_clip)

    # Concatenate all video and audio clips
    final_video = concatenate_videoclips(video_clips)
    final_audio = concatenate_audioclips(audio_clips)

    # Apply fade-in effect at the start and fade-out effect at the end
    final_video = add_fadein_to_video(final_video, 3)
    final_audio = add_fadein_to_audio(final_audio, 3)
    
    final_video = add_fadeout_to_video(final_video, 3)
    final_audio = add_fadeout_to_audio(final_audio, 3)

    final_video = final_video.set_audio(final_audio)

    return final_video

def create_playlist_video_with_effect(image_files, music_files, resolution="FullHD", effect_kw=None):
    """
    Create a video that plays all audio tracks in sequence, 
    changing the image displayed with each new track.
    
    Args:
        image_files (list): List of images paths.
        music_files (list): List of music track paths.
        resolution (str): Desired video resolution (default is "FullHD").
    
    Returns:
        final_video
    """

    # Ensure that the number of images matches the number of music tracks
    if len(image_files) != len(music_files):
        raise ValueError("The number of images must match the number of music tracks.")

    temp_video_files = []

    # Step 1: Apply effect loop to each image and save to temporary files
    for image_file in image_files:
        image_clip = image2clip(str(image_file), RESOLUTIONS[resolution])

        # Add effect overlay
        if effect_kw:
            effect_clip = video2clip(str(effect_kw["effect_path"]), RESOLUTIONS[resolution])
            image_clip = overlay_effect(
                image_clip, 
                effect_clip, 
                effect_kw["background_color"], 
                effect_kw["effect_color"])
        
        # Save to a temporary file
        temp_file = tempfile.mktemp(suffix=".mp4")
        image_clip.write_videofile(temp_file, threads=8)
        temp_video_files.append(temp_file)

    video_clips = []
    audio_clips = []

    # Step 2: Load temporary video clips, set duration, and apply fade-in and fade-out effects
    for i, (temp_video_file, music_file) in enumerate(zip(temp_video_files, music_files)):
        audio_clip = mpe.AudioFileClip(str(music_file))
        video_clip = mpe.VideoFileClip(temp_video_file).loop(duration=audio_clip.duration)

        # Apply fade-in and fade-out effects to the video for transitions
        video_clip = add_fadein_to_video(video_clip, 2)
        video_clip = add_fadeout_to_video(video_clip, 2)

        # Apply fade-in and fade-out to audio tracks, except beginning and end of playlist
        if i != 0:
            audio_clip = add_fadein_to_audio(audio_clip, 2)
        if i != len(image_files) - 1:
            audio_clip = add_fadeout_to_audio(audio_clip, 2)
        
        video_clips.append(video_clip)
        audio_clips.append(audio_clip)

    # Step 3: Concatenate all video and audio clips
    final_video = concatenate_videoclips(video_clips)
    final_audio = concatenate_audioclips(audio_clips)

    # Apply fade-in effect at the start and fade-out effect at the end
    final_video = add_fadein_to_video(final_video, 3)
    final_audio = add_fadein_to_audio(final_audio, 3)
    
    final_video = add_fadeout_to_video(final_video, 3)
    final_audio = add_fadeout_to_audio(final_audio, 3)

    final_video = final_video.set_audio(final_audio)

    # Cleanup temporary files
    for temp_file in temp_video_files:
        os.remove(temp_file)

    return final_video



if __name__ == "__main__":

    move_files_when_done = True    
    
    data = pd.read_csv('input.csv')
    print(f'Generating {len(data)} videos...')

    for i, (image_name, music_name, render_name) in data.iterrows():


        # image_name = "PapitaFrita_an_alien_landscape_inspired_in_7844fedf-a1e7-421c-aa22-30ca011b83ec-transformed.jpeg"
        # music_name = "moods beautiful peaceful remix (be94a2a4c97a44698910dff11d589e8f).wav"
        # render_name = "ethereal_passenger_001.mp4"
        #effect_name = "dust_spaced_1080.mp4"
        #effect_name = "grain_with_lines_1080.mp4"
        effect_name = "particulas_black_1080.mp4"

        duration_min = 79.99
        
        channels = {
            0: "Alien Ambient",
            1: "Ethereal_Passenger"
        }
        channel = channels[1]

        PATH = Path(os.path.abspath(os.path.dirname(__file__)))
        source_image_path = PATH / "images" / channel / "Upscaled" 
        source_music_path = PATH / "music" / channel / "Elegidas" 
        used_image_path = PATH / "images" / channel / "Upscaled" / "Usadas"
        used_music_path = PATH / "music" / channel / "Elegidas" / "Usadas"
        render_path = PATH / "renders" / channel
        effect_path = PATH / 'effects'
        effect_output_path = render_path

        # Render video
        # add_audio_to_image(
        #     str(source_image_path / image_name), 
        #     str(source_music_path / music_name), 
        #     str(render_path / render_name), 
        #     duration_min=duration_min)

        # Particle Effects
        effect_video_name = f"tmp_{render_name}"
        video_path =  effect_output_path / effect_video_name

        
        add_effect_to_image(
            str(source_image_path / image_name),
            str(effect_path / effect_name),
            str(effect_output_path / effect_video_name),
            background_color=[0, 0, 0],
            #effect_color=[239/255, 145/255, 93/255]
            effect_color=[1, 1, 1]
            )
        
        add_audio_to_video(
            str(video_path),
            str(source_music_path / music_name),
            str(render_path / render_name),
            duration_min=duration_min,
            fadein_sec=4
            )


        if move_files_when_done:
            # Move files to used path, including the Mubert license pdf
            move_file(source_image_path / image_name, used_image_path)
            move_file(source_music_path / music_name, used_music_path)
            # Move the license together with the music
            move_file(str(source_music_path / music_name).replace(".wav", ".pdf"), used_music_path)


