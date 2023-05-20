import os
from pathlib import Path

from PIL import Image

import moviepy.editor as mpe
from moviepy.audio.fx.all import audio_loop

import numpy as np

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
        background_color = [1, 141, 34]

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


def add_audio_to_video(video_path, audio_path, output_path, resolution="FullHD", duration_min=1.):
    """Create a video with music."""

    resolution = RESOLUTIONS[resolution]
    duration_sec = duration_min * 60.  # to seconds

    # Create the base clip
    clip = video2clip(video_path, resolution)

    # Add audio to clip
    audio_clip = mpe.AudioFileClip(audio_path)
    clip = merge_audio_and_video(audio_clip, clip, duration=duration_sec)

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




if __name__ == "__main__":
    
    image_name = "PapitaFrita_in_the_image_6277cad1-0c92-4f00-877d-e54cdec22f30-transformed.jpeg"
    music_name = "moods heroic cinematic remix (32039f4169904780bb5017619d581e2a).wav"
    render_name = "alien_ambient_021.mp4"

    duration_min = 120.
    
    
    PATH = Path(os.path.abspath(os.path.dirname(__file__)))
    source_image_path = PATH / "images" / "Alien Ambient" / "Upscaled" 
    source_music_path = PATH / "music" / "Alien Ambient" / "Elegidas" 
    used_image_path = PATH / "images" / "Alien Ambient" / "Upscaled" / "Usadas"
    used_music_path = PATH / "music" / "Alien Ambient" / "Elegidas" / "Usadas"
    render_path = PATH / "renders" / "Alien Ambient"

    # Render video
    add_audio_to_image(
        str(source_image_path / image_name), 
        str(source_music_path / music_name), 
        str(render_path / render_name), 
        duration_min=duration_min)

    # Move files to used path, including the Mubert license pdf
    move_file(source_image_path / image_name, used_image_path)
    move_file(source_music_path / music_name, used_music_path)
    # Move the license together with the music
    move_file(str(source_music_path / music_name).replace(".wav", ".pdf"), used_music_path)


    # Particle Effects
    #
    # video_path = None #"renders/test_track_short.mp4"
    # effect_path = None #"effects/particles_9s_1080p.mkv"
    # add_video_to_image(video_path, audio_path, output_path)