#!/usr/bin/env python

import six
import lxml
import requests
import subprocess
from bs4 import BeautifulSoup

API = 'https://api.genius.com'
ACCESS_TOKEN = 'Za979SFA7_pwCdjDaAsBhnPb3A5jSgcCMixyiDeJv7U415u3ko6Qd14HIJzqrXFj'

class HitResult():
    def __init__(self, artist, title, song_id, url):
        self.artist = artist
        self.title = title
        self.song_id = song_id
        self.url = url

    def form_output(self):
        '''Forms lyric sheet output for either paging or printing directly to a terminal.'''

        header = '{} - {}'.format(self.artist, self.title)
        divider = '-'*(len(header) + 3)
        lyrics = get_lyrics_from_url(self.url)

        output = header + '\n' + divider + '\n' + lyrics + '\n'
        return output


def genius_search(query):
    ''' Uses the genius.com search API to return a list of HitResult instances,
    formed by JSON responses from the search. '''

    results = []

    search_endpoint = API + '/search?'
    payload = {'q': query, 'access_token': ACCESS_TOKEN}
    search_request_object = requests.get(search_endpoint, params=payload)

    if search_request_object.status_code == 200:
        json_response = search_request_object.json()

        # Get search entry information from JSON response
        for hit in json_response['response']['hits']:
            artist = hit['result']['primary_artist']['name']
            title = hit['result']['title']
            song_id = hit['result']['id']
            url = hit['result']['url']

            results.append(HitResult(artist, title, song_id, url))

    elif 400 <= search_request_object.status_code < 500:
        six.print_('[!] Uh-oh, something seems wrong...')
        six.print_('[!] Please submit an issue at https://github.com/donniebishop/genius_lyrics/issues')
        sys.exit(1)

    elif search_request_object.status_code >= 500:
        six.print_('[*] Hmm... Genius.com seems to be having some issues right now.')
        six.print_('[*] Please try your search again in a little bit!')
        sys.exit(1)

    return results


def get_lyrics_from_url(song_url):
    '''Looks up song_url, parses page for lyrics and returns the lyrics.'''

    get_url = requests.get(song_url)
    song_soup = BeautifulSoup(get_url.text, 'lxml')
    soup_lyrics = song_soup.lyrics.text
    return soup_lyrics


def pick_from_search(results_array):
    ''' If -s/--search is called, return a list of top results, and prompt
    choice from list. Will continue to prompt until it receives a valid choice.
    Returns HitResult instance of the appropriate JSON response. '''

    for n in range(len(results_array)):
        Current = results_array[n]
        result_line = '[{}] {} - {}'.format(n+1, Current.artist, Current.title)
        six.print_(result_line)

    choice = -1
    while choice <= 0 or choice > len(results_array):
        try:
            choice = int(input('\nPlease select a song number: '))
        except ValueError:
            six.print_('[!] Please enter a number.')
            choice = -1

    actual_choice = choice - 1
    return results_array[actual_choice]


# Referents section

class Referent():
    """docstring for Referent"""
    def __init__(self, classification, fragment, ref_id, url):
        self.classification = classification
        self.fragment = fragment
        self.ref_id = ref_id
        self.url = url


def get_referents(song_id):
    ''' Use song_id to pull referents for any annotations for the song. '''

    referents = []

    referents_endpoint = API + '/referents'
    payload = {'song_id': song_id, 'access_token': ACCESS_TOKEN}
    referents_request_object = requests.get(referents_endpoint, params=payload)

    if referents_request_object.status_code == 200:
        json_response = referents_request_object.json()

        for r in json_response['response']['referents']:
            c = r['classification']
            f = r['fragment']
            r_id = r['id']
            r_url = r['url']

            referents.append(Referent(c, f, r_id, r_url))
    elif referents_request_object.status_code >= 500:
        pass

    return referents
