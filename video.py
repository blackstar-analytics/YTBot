from PIL import Image
from moviepy.editor import ImageClip, VideoClip, AudioFileClip, concatenate_videoclips
from moviepy.audio.fx.all import audio_loop
import numpy as np


def repeat_audio(audio_clip, nloops=None, duration=None):
    return audio_loop(audio_clip, nloops=nloops, duration=duration)


def add_static_image_to_audio(image_path, audio_path):
    """Create and save a video file to `output_path` after 
    combining a static image that is located in `image_path` 
    with an audio file in `audio_path`"""

    # use set_audio method from image clip to combine the audio with the image
    video_clip = image_clip.set_audio(audio_clip)
    # specify the duration of the new clip to be the duration of the audio clip
    video_clip.duration = audio_clip.duration
    # set the FPS to 1
    video_clip.fps = 1

    return video_clip


if __name__ == "__main__":
    image_path = "images/PapitaFrita_an_alien_artificial_intelligence_that_can_do_magic.png"
    audio_path = "music/moods_dreamy_track.mp3"
    output_path = "renders/test_track.mp4"

    total_duration = 120 * 60.  #  seconds

    # create the audio clip object
    original_audio_clip = AudioFileClip(audio_path)
    audio_clip = audio_loop(original_audio_clip, duration=total_duration)

    # create the image clip object
    image_clip = ImageClip(image_path)

    video_clip = add_static_image_to_audio(image_path, audio_path)

    # write the resuling video clip
    video_clip.write_videofile(output_path)