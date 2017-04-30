import json
import re

import requests

page_token = re.compile('https?:\/\/e[\-x]hentai\.org\/s\/([\da-f]{10})\/(\d+)\-(\d+)')
gallery_token = re.compile('https?:\/\/e[\-x]hentai\.org\/(?:g|mpv)\/(\d+)\/([\da-f]{10})')
EH_API = "https://e-hentai.org/api.php"


# extract all exurls from a string and get the metadata
def get_galleries(message):
    gids = get_gids(message)
    all_galleries = []
    if gids:
        for token_group in divide_chunks(gids):
            all_galleries += api_gallery(token_group)
    return all_galleries


# get the gids and hashes of every EH url posted in a message
def get_gids(message):
    gallery_results = []
    page_results = page_token.findall(message)
    # fix up ordering and types before querying EH
    remapped_results = [[int(elem[1]), elem[0], int(elem[2])] for elem in page_results]
    # divide into chunks of max 25 requests per POST to EH
    for token_group in divide_chunks(remapped_results):
        gallery_results += api_page(token_group)
    gallery_results += [[int(elem[0]), elem[1]] for elem in gallery_token.findall(message)]
    return gallery_results


# Divide lists into chunks of 25 since EH only allows a max of 25 urls per POST request
def divide_chunks(original_chunk):
    return [original_chunk[i:i + 25] for i in range(0, len(original_chunk), 25)]


# Query the EH api for gid from a gallery page url
def api_page(token_group):
    payload = {"method": "gtoken", "pagelist": token_group}
    r = requests.post(EH_API, data=json.dumps(payload))
    return [[elem['gid'], elem['token']] for elem in r.json()['tokenlist']]


# Query the EH api for metadata from a gallery
def api_gallery(token_group):
    payload = {"method": "gdata", "gidlist": token_group, "namespace": 1}
    r = requests.post(EH_API, data=json.dumps(payload))
    return r.json()['gmetadata']
