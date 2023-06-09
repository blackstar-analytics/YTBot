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
    
    image_name = "PapitaFrita_a_landscape_in_an_alien_and_spiritual_planet_seen_f_036c620c-4a88-4c3b-96fb-259b2acf88eb-transformed.jpeg"
    music_name = "Sing_for_Absolution.mp3"
    effect_name = "particulas_green_1080.mp4"
    effect_video_name = "temp_prueba3.mp4"
    render_name = "prueba3.mp4"

    duration_min = 1.
    
    channel_1 = "Ethereal_Passenger"
    channel_2 = "Alien Ambient"

    PATH = Path(os.path.abspath(os.path.dirname(__file__)))
    source_image_path = PATH / "images" / "Ethereal_Passenger" / "Upscaled" 
    source_music_path = PATH / "music" / "Ethereal_Passenger" / "Elegidas" 
    used_image_path = PATH / "images" / "Ethereal_Passenger" / "Upscaled" / "Usadas"
    used_music_path = PATH / "music" / "Ethereal_Passenger" / "Elegidas" / "Usadas"
    render_path = PATH / "renders" / "Ethereal_Passenger"
    effect_path = PATH / 'effects'
    effect_output_path = render_path

    # Render video
    # add_audio_to_image(
    #     str(source_image_path / image_name), 
    #     str(source_music_path / music_name), 
    #     str(render_path / render_name), 
    #     duration_min=duration_min)

    # Particle Effects
    
    video_path =  effect_output_path / effect_video_name

    
    add_effect_to_image(
        str(source_image_path / image_name),
        str(effect_path / effect_name),
        str(effect_output_path / effect_video_name),
        background_color=[1, 141, 34],
        effect_color=[255, 229, 204]
        )
    
    add_audio_to_video(
        str(video_path),
        str(source_music_path / music_name),
        str(render_path / render_name),
        duration_min=duration_min
        )

    # Move files to used path, including the Mubert license pdf
    #move_file(source_image_path / image_name, used_image_path)
    #move_file(source_music_path / music_name, used_music_path)
    # Move the license together with the music
    #move_file(str(source_music_path / music_name).replace(".wav", ".pdf"), used_music_path)


