import csv
from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json

load_dotenv()

client_id = os.getenv("client_id")
client_secret = os.getenv("client_secret")
print(client_id, client_secret)

def get_token():
    auth_string = client_id + ':' + client_secret
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = str(base64.b64encode(auth_bytes), 'utf-8')

    url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': 'Basic ' + auth_base64,
        'Content-type': 'application/x-www-form-urlencoded'
    }
    data = {'grant_type': 'client_credentials'}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)

    if result.status_code != 200:
        print(f"Error: {result.status_code}, {json_result}")
        return None

    token = json_result["access_token"]
    return token


def get_auth_header(token):
    return {'Authorization': 'Bearer ' + token}


def get_artist_genre(artist_id, token):
    url = f"https://api.spotify.com/v1/artists/{artist_id}"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)

    if result.status_code != 200:
        return "Genre not found"

    genres = json_result.get("genres", [])
    return ", ".join(genres) if genres else "No genre available"


def get_audio_features(track_id, token):
    url = f"https://api.spotify.com/v1/audio-features/{track_id}"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)

    if result.status_code != 200:
        return None

    return json_result


def search_for_tracks(artist_name, token):
    url = 'https://api.spotify.com/v1/search'
    headers = get_auth_header(token)

    query = f"?q={artist_name}&type=track&limit=5"
    query_url = url + query

    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)

    if result.status_code != 200:
        print(f"Error: {result.status_code}, {json_result}")
        return []

    tracks = json_result['tracks']['items']
    if len(tracks) == 0:
        print(f"No tracks found for {artist_name}.")
        return []

    track_data = []
    print(f"Top 5 tracks by {artist_name}:")

    for idx, track in enumerate(tracks):
        track_name = track['name']
        album_name = track['album']['name']
        popularity = track['popularity']
        release_date = track['album']['release_date']
        track_id = track['id']
        artist_id = track['artists'][0]['id']

        # Get genre from artist API
        genre = get_artist_genre(artist_id, token)

        # Get audio features
        audio_features = get_audio_features(track_id, token)

        # Check for valid audio features
        if audio_features:
            tempo = audio_features.get('tempo', 'N/A')
            key = audio_features.get('key', 'N/A')
            mode = audio_features.get('mode', 'N/A')
            loudness = audio_features.get('loudness', 'N/A')
        else:
            tempo, key, mode, loudness = 'N/A', 'N/A', 'N/A', 'N/A'

        # Print details
        print(f"\n🎵 {idx + 1}. Track Name: {track_name}")
        print(f"   🎤 Album Name: {album_name}")
        print(f"   🌟 Popularity Score: {popularity}")
        print(f"   📅 Release Date: {release_date}")
        print(f"   🎧 Genre: {genre}")
        print(f"   🎼 Audio Features: Tempo - {tempo}, Key - {key}, Mode - {mode}, Loudness - {loudness}")

        # Add data to the list
        track_data.append([
            track_name, album_name, popularity, release_date,
            genre, tempo, key, mode, loudness
        ])

    # Write data to CSV
    save_to_csv(track_data, artist_name)


def save_to_csv(track_data, artist_name):
    csv_filename = f"{artist_name.replace(' ', '_').lower()}_top_tracks.csv"

    # Define CSV column names
    header = ['Track Name', 'Album Name', 'Popularity Score', 'Release Date', 'Genre', 'Tempo', 'Key', 'Mode', 'Loudness']

    # Write to CSV
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(track_data)

    print(f"\n✅ CSV file '{csv_filename}' created successfully!")


# Get Spotify token
token = get_token()
if token:
    search_for_tracks('Sid Sriram', token)
