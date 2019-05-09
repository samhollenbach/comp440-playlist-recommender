# Playlist Recommender - Comp 440 (Collective Intelligence) Final Project
## Sam Hollenbach / Raza Khalid

This project analyzes audio features from plylists and recommends songs to add to the playlist from a database of over 130k songs.
The program uses Spotipy to collect audio features from the Spotify API.

### Running the Project

There is one main script, `recommeder.py`, and one supporting performance script, `perf.py`. Run them as a normal python script:
```
python3 recommender.py
python3 perf.py
```

**NOTE:** You can actually pass in a Spotify username as an argument for the script, 
but then you need your own client IDs and tokens and such, which is a hassle.
Therefore it just uses my personal Spotify account which has no songs on it (because I use Apple Music).
In theory, changing these credentials would allow this program to analyze one's own playlists,
but for now we are using a set of 4000 playlists for testing archived from the Spotify Million Playlist Challenge.


### Approach

#### Feature Extraction

We used a kind of inverse variance thersholding to select features to use in our comparisons. This is because of our base
assumption that a playlist is built around a certain "sound", or rather one or more specific audio features in our context.
Eliminating features that have a lot of variance will keep only the features that "define" the playlist's "sound". 

#### Testing and Suggesting

The main script loops through one of the 4 playlist files (1000 playlists), and either makes song recommendations for the playlist,
or runs performance testing, and saves the performance the results to an `results.csv` file. For both, each song in the song database
is assigned a score based on it's audio feature cosine similarities to the rest of the playlist.
The similarity scores are then converted to score percentiles against the rest of dataset.
This final performance score is stored in the last column of this file under `percentile` on a 0 to 1.0 scale.
When doing performance testing, the algorithm will remove one song from each playlist it is testing, run this pipeline,
and determine what percentile our removed song achieves. 

### Performance

The `perf.py` script does very basic analysis on the output `results.csv` file, 
computing the number of playlists analyzed, and the average percentile score of the test songs.

After testing 65 playlists, we've achieved an average percentile of 0.768.
If we chose random songs, this average would settle to 0.50, so our approach seems to be working fairly well. 

