import requests
import json

MUBERT_API_ENDPOINT = "https://mubert.com/api/v3/track/generate"

def build_params(
    apiKey,
    genre="",
    mood="",
    intensity=0,
    tempo=0,
    duration=0,
    instrument="",
    audioFormat="wav",
    samplerate=0,
    channels=0,
    bitdepth=0,
    title="",
    artist="",
    album="",
    genreId="",
    moodId="",
    intensityId="",
    instrumentId="",
    audioFormatId="",
    samplerateId="",
    channelsId="",
    bitdepthId=""
):
    params = {
        "apiKey": apiKey,
        "genre": genre,
        "mood": mood,
        "intensity": intensity,
        "tempo": tempo,
        "duration": duration,
        "instrument": instrument,
        "audioFormat": audioFormat,
        "samplerate": samplerate,
        "channels": channels,
        "bitdepth": bitdepth,
        "title": title,
        "artist": artist,
        "album": album,
        "genreId": genreId,
        "moodId": moodId,
        "intensityId": intensityId,
        "instrumentId": instrumentId,
        "audioFormatId": audioFormatId,
        "samplerateId": samplerateId,
        "channelsId": channelsId,
        "bitdepthId": bitdepthId
    }

    return params


def generate_music(genre, mood):
    # Set the parameters for the Mubert API request
    params = {
        "apiKey": "your_api_key",
        "genre": genre,
        "mood": mood
    }

    # Send a POST request to the Mubert API endpoint
    response = requests.post(MUBERT_API_ENDPOINT, data=json.dumps(params))

    # Extract the audio data from the response
    audio_data = response.content

    # Return the audio data
    return audio_data

def save_audio_file(audio_data, file_path):
    with open(file_path, 'wb') as f:
        f.write(audio_data)


def main():
    # Loop infinitely to listen for user input
    while True:
        # Get the genre and mood from the user
        genre = input("Enter a genre (e.g. rock, classical, jazz): ")
        mood = input("Enter a mood (e.g. happy, sad, calm): ")

        # Generate the music based on the user input
        audio_data = generate_music(genre, mood)

        # Save the audio data to a file
        name = input("Enter a file name `name`.wav")
        file_path = f"{name}.wav"
        save_audio_file(audio_data, file_path)

if __name__ == "__main__":
    main()
