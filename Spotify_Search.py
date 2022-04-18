from tkinter import *
from tkinter import ttk
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from PIL import Image, ImageTk
import requests
from io import BytesIO

# Establishes the credentials for the Spotify API
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id = 'bc8e3997f0b74c5880082853462bae26',
    client_secret = '55e7709d7cd244cba8251cbff83a4a3e'))

# Sets up the main window for the user interface
main_window = Tk()
main_window.title('Spotify Artist Search')
main_window.geometry("800x600")
main_window.columnconfigure(0, weight = 1)
main_window.resizable(width = False, height = False)
frame1 = Frame(main_window, width = 646, height = 646)

# Defines the variable for the user entry
artist_var = StringVar()

def submit():

    # Makes necesarry variables global
    # allowing them to be handled by multiple functions 
    # assigned to tkinter widgets
    global all_albums
    global all_artists
    global artist_id
    global artist_found
    
    all_albums = []
    album_images = []
    album_names = []
    all_artists = []
    btns = []
    artist_found = False
    artist_id = ''
    
    # Deletes widgets from prior searches, if present.
    if len(frame1.winfo_children()) > 0:
        for widget in frame1.winfo_children():
            widget.destroy()
    
    # Retrieves the users entry and searches for an artist through the API.
    response = artist_var.get()
    q = f'artist:{response}'
    artist_results = sp.search(q,limit = 10,type = 'artist')
    
    # If no artists match users search, assigns artist ID as null.
    if len(artist_results['artists']['items']) == 0 and artist_found == False:
        artist_id = 'null'
    
    # If just one artist is found, automatically retrieves the artist ID.
    if len(artist_results['artists']['items']) == 1 and artist_found == False:
        artist_id = artist_results['artists']['items'][0]['id']
        artist_found = True
    
    # If multiple artists found, loops through to see if any artist names
    # match the users entry exactly, retrives the artist ID if this is the case.
    if artist_id == '' and artist_found == False:
        for item in artist_results['artists']['items']:
            if item['name'] == response:
                artist_id = item['id']
                artist_found = True
                break
    
    # If still no artist found, launches popup window asking user to select
    # artist.
    if artist_id == '' and artist_found == False:
        artist_found = True
        artist_sel = Toplevel(main_window)
        artist_sel.columnconfigure(0, weight = 1)
        art_sel_lab = Label(artist_sel,text = 'Did you mean...').grid(row = 0, 
            sticky = "N", padx = 20, pady = 5)

        # Loops through every artist found through the initial search, making
        # a button for each one, upon clicking the button the user entry box
        # contents will be changed to what the user selected and the album
        # search will be performed using the selected artist.
        for idx, item in enumerate(artist_results['artists']['items']):
            artist = {}
            artist['name'] = item['name']
            artist['id'] = item['id']
            new_btn = Button(
                artist_sel, 
                text = item['name'], 
                command = lambda c = idx: [artist_click((all_artists[c]['name']),
                (all_artists[c]['id'])),
                artist_sel.destroy()]).grid(row = idx + 1,sticky = "N")
            artist['button'] = new_btn
            all_artists.append(artist)
    
    # Once an artist has been found/selected by the user, uses the artist ID
    # to search for albums through the API.
    if artist_id != '' and artist_id != 'null':
        q = f'artist:{response}'
        results = sp.search(q,limit = 20,type = 'album')
        j = len(results['albums']['items'])
        i = 0
        while i < 6:
            # Loops through all albums from the album search, making buttons
            # and labels for each one.
            for idx, item in enumerate(results['albums']['items']):

                # This if statement verifies that the album is actually by the
                # artist the user entered by comparing the artist_id of the
                # album to the artist_id of the artist entered by the user. 
                # The Spotipy API search function only allows searching by name, 
                # and sometimes returns albums not actually by the artist and 
                # instead returns results for artists with similar names. This
                # prevents those albums from being displayed.
                if item['artists'][0]['id'] == artist_id :
                    album = {}
                    album_cover = (item['images'][0]['url'])
                    album_id = (item['id'])
                    retr_cover = requests.get(album_cover)
                    im = Image.open(BytesIO(retr_cover.content))
                    im = im.resize((200,200))
                    image = ImageTk.PhotoImage(im)
                    album_btn = Button(
                        frame1,
                        image = image,
                        command = lambda album_idx = i : album_click(album_idx))
                    btn_label = Label(
                        frame1,
                        text = (item['name']),
                        wraplength = 200,
                        justify = CENTER, 
                        font = ('Arial',12,'normal'))
                    album['name'] = item['name']
                    album['cover'] = image
                    album['button'] = album_btn
                    album['label'] = btn_label
                    album['album_id'] = album_id
                    album['released'] = item['release_date']
                    album['artist'] = item['artists'][0]['name']
                    current_ids = []

                    # This block ensures that no duplicate albums are placed as
                    # the search function can sometimes return duplicates.
                    for item in all_albums:
                        current_ids.append(item['album_id'])
                    if album_id not in current_ids and len(all_albums) < 6: 
                        all_albums.append(album)
                        i += 1

                # If the loop is on the last albom or 6 albums have been found,
                # changes i to 6 to break the loop and stop adding new albums.
                if idx == j - 1 or len(all_albums) == 6:
                    i = 6

        if len(all_albums) > 6:
            z = 6
        else:
            z = len(all_albums)
    
        # Places button and label tkinter objects on the grid to display them
        # in the window.
        for i in range(z):
            button = all_albums[i]['button']
            label = all_albums[i]['label']
            if i == 0:
                j = 0
                k = 0
            elif i == 1:
                j = 0
                k = 1
            elif i == 2:
                j = 0
                k = 2
            elif i == 3:
                j = 2
                k = 0
            elif i == 4:
                j = 2
                k = 1
            else:
                j = 2
                k = 2
            button.grid(row = j, column = k)
            label.grid(row = j + 1, column = k)
            
    # Informs user if no artist was found with the name they entered.
    if artist_id == 'null':
        q = f'No artist found\nnamed {response}.\nPlease try again.'
        label = Label(frame1, text = q)
        label.grid(row = 0, column =1)

# Function for the button that appears if a user is prompted to select an
# artist. Will place the artists name in the entry box, then rerun the submit
# function. As there is now an artist found the submit function goes straight
# to the album search.
def artist_click(name,number):
    artist_entry.delete(0, END)
    artist_entry.insert(0, name)
    submit()
    artist_id = number
    artist_found = True

# Function for the button that appears as the album cover. When clicked will
# perform another query of the spotify API to retrieve all tra cks of the album.
# Lists album name, album artist, release date, and track listing in a popup 
# window.
def album_click(album_idx):
    popup = Toplevel(main_window)
    popup.columnconfigure(0, weight = 1)
    popup.title('Album Details')
    title_lab = Label(
        popup, 
        text = (all_albums[album_idx]['name'])).grid(row = 0, sticky = "N")
    artist_lab = Label(
        popup, 
        text = (all_albums[album_idx]['artist'])).grid(row = 1, sticky = "N")
    rel_date = Label(
        popup, 
        text = str('Released: ' + all_albums[album_idx]['released'])).grid(row = 2, sticky = "N")
    track_listing = []
    track_results = sp.album_tracks(all_albums[album_idx]['album_id'])
    for tr_item in track_results['items']:
        track_listing.append(tr_item['name'])
    track_string = ''
    for idx, item in enumerate(track_listing):
        track = (str(idx+1) +": " + item + '\n')
        track_string = track_string + track
    tracks = Label(
        popup, 
        text = track_string, 
        justify = LEFT).grid(row = 3,sticky = "N",padx = 20)

# Tkinter widgets for the entry box and submit button.
artist_label = Label(
    main_window,
    text = 'Enter an Artist:',
    font = ('Arial',20, 'bold'))

artist_entry = Entry(
    main_window,
    textvariable = artist_var,
    font = ('Arial',20,'normal'))

sub_btn = Button(
    main_window,
    text = 'Submit',
    font = ('Arial',15,'normal'),
    command = submit)

artist_label.grid(row = 0, sticky = "N")
artist_entry.grid(row = 1, sticky = "N")
sub_btn.grid(row = 2, sticky = "N")
frame1.grid(row = 3, sticky = "N")

main_window.mainloop()