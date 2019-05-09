from sklearn.feature_selection import VarianceThreshold
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import csv
import sys
import pandas as pd
import numpy as np
import os
from json.decoder import JSONDecodeError
import spotipy
import spotipy.util as util
import json
from pprint import pprint



audio_feat_keys = ['danceability', 'energy', 'key', 'mode', 'speechiness', 'acousticness',
                       'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms']



def get_audio_feats(tracks):
    track_ids = [t['track_uri'].split(':')[-1] for t in tracks]
    audio_feats = sp.audio_features(tracks=track_ids)
    tracks_with_feats = []

    for track, audio_feats in zip(tracks, audio_feats):
        tr = {'artist_name': track['artist_name'],
              'track_id': audio_feats['id'],
              'track_name': track['track_name']}

        af = {key: audio_feats[key] for key in audio_feat_keys}
        tr.update(af)
        tracks_with_feats.append(tr)

    return tracks_with_feats



def select_low_variance_features(playlist):
    playlist_feats = playlist[audio_feat_keys]
    selector = VarianceThreshold()
    selector.fit(playlist_feats)
    features = ['artist_name', 'track_name']
    thresh = 0.05  # keep below! want features with low variance
    for col, var in zip(playlist_feats.columns, selector.variances_):
        if var <= thresh:
            features.append(col)
    return playlist[features]


def find_matching_songs(playlist, songs):
    matching_ids = []
    for index, playlist_song in playlist.iterrows():
        s = songs[songs['track_name'].str.match(playlist_song['track_name'], case=False)
                  & songs['artist_name'].str.match(playlist_song['artist_name'], case=False)]
        # s = songs.loc[(songs.track_name.str.lower() == playlist_song.track_name.str.lower())
        #               & (songs.artist_name.str.lower() == playlist_song.artist_name.str.lower())]
        if not s.empty:
            matching_ids.append((index, s.index[0]))
    print(matching_ids)
    return matching_ids


def normalize_df(df):
    return df
    # mms = MinMaxScaler()
    # df_norm = mms.fit_transform(df)
    # return df_norm

def compute_feature_similarity(playlist, songs):
    feat_keys = np.intersect1d(audio_feat_keys, playlist.columns)
    playlist_feats = normalize_df(playlist[feat_keys])


    cos_sums = []
    for index, song in songs.iterrows():
        song_feats = normalize_df(song[feat_keys])
        cs = cosine_similarity(playlist_feats, [song_feats])
        cs_sum = np.sum(np.power(cs, 2))
        cos_sums.append(cs_sum)

    songs['cos'] = cos_sums

    return songs


def make_playlist_suggestions(playlist, songs, n=10):
    playlist = select_low_variance_features(playlist)
    songs = compute_feature_similarity(playlist, songs)
    songs.sort_values(by=['cos'], ascending=False, inplace=True)
    return songs.head(n)


def test_playlist_suggestions(playlist, songs):
    matching_ids = find_matching_songs(playlist, songs)

    if not matching_ids:
        # print("Playlist does not contain any overlap with song database")
        # return []
        raise Exception("Playlist does not contain any overlap with song database")

    playlist = select_low_variance_features(playlist)
    test_playlist, song_index = make_test_playlist(playlist, matching_ids)
    songs = compute_feature_similarity(test_playlist, songs)
    # songs.sort_values(by=['cos'], ascending=False, inplace=True)
    songs['percentile'] = songs.cos.rank(pct=True)
    test_song = songs.iloc[[song_index]]
    return test_song



def make_test_playlist(playlist, matching_ids):
    pid, sid = matching_ids[-1]  # arbitrarily take last matching ID
    return playlist.drop([pid]), sid





if __name__ == '__main__':

    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        username = 'shollenb'
        # print("Usage: %s username" % (sys.argv[0],))
        # sys.exit()

    client_id = '6c7bffcfc3b34a18a941eb564479e818'
    client_secret = 'bb15d066b703430b8d071d9565a9b677'
    redirect_uri = 'http://localhost:8888/callback'
    scope = 'user-top-read'

    try:
        token = util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_uri)
    except (AttributeError, JSONDecodeError):
        os.remove(f".cache-{username}")
        token = util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_uri)

    sp = spotipy.Spotify(auth=token)
    sp.trace = False

    with open('data/mpd.slice.0-999.json', 'rb') as playlist_file:
        j = json.load(playlist_file)
        playlists = j['playlists'][50:]

        songs = pd.read_csv('data/SpotifyAudioFeaturesApril2019.csv')

        write_header = True
        tests = []
        for p in playlists:

            try:
                tracks_test = p['tracks']
                af = get_audio_feats(tracks_test)
                playlist = pd.DataFrame(af)
                test_song = test_playlist_suggestions(playlist, songs)

                print(test_song)
                tests.append(test_song)

                if write_header:
                    test_song.to_csv('results.csv', mode='w+', header=True)
                    write_header = False
                else:
                    test_song.to_csv('results.csv', mode='a', header=False)


            except Exception as e:
                print(e)
                # print(f"No overlapping songs found in playlist {p['pid']}")
                pass


        print(tests)




