from pathlib import Path

from video import create_playlist_video_with_effect, get_files_from_directory


PATH = Path.cwd()

# Get all images and music tracks
image_folder = PATH / "images/Ethereal_Passenger/Lotus"
music_folder = PATH / "music/Ethereal_Passenger/Lotus"

image_files = get_files_from_directory(image_folder, ".png")
music_files = get_files_from_directory(music_folder, ".wav")

# Effect properties. Colors are normalized RGB, 0-1
effect_kw = {
    "effect_path": PATH / "effects" / "particulas_black_1080.mp4",
    "background_color": [0, 0, 0],
    "effect_color": [1, 1, 1]
}

output = create_playlist_video_with_effect(image_files, music_files, resolution="FullHD", effect_kw=effect_kw)

# Render the final video
output.fps = 25
output.write_videofile("test.mp4", threads=8)