import datetime
import json
import os
import re

import discord
import requests
from bs4 import BeautifulSoup

DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
client = discord.Client()

page_token = re.compile('https?:\/\/e[\-x]hentai\.org\/s\/([\da-f]{10})\/(\d+)\-(\d+)')
gallery_token = re.compile('https?:\/\/e[\-x]hentai\.org\/(?:g|mpv)\/(\d+)\/([\da-f]{10})')
set_topic_re = re.compile('^!topic (.*)$')

EH_API = "https://e-hentai.org/api.php"
G_CATEGORY = {"Doujinshi": "https://a.safe.moe/4JVyo.png",
              "Manga": "https://a.safe.moe/Uy5AH.png",
              "Artist CG Sets": "https://a.safe.moe/GCLdI.png",
              "Game CG Sets": "https://a.safe.moe/xbECu.png",
              "Western": "https://a.safe.moe/JcGGo.png",
              "Non-H": "https://a.safe.moe/wpqMe.png",
              "Image Sets": "https://a.safe.moe/tjc3i.png",
              "Cosplay": "https://a.safe.moe/NpzDp.png",
              "Asian Porn": "https://a.safe.moe/Im78o.png",
              "Misc": "https://a.safe.moe/X5Tb7.png"}
EH_COLOUR = discord.Colour(0x660611)


@client.event
async def on_message(message):
    gids = get_gids(message.content)
    for token_group in divide_chunks(gids):
        galleries = gallery_api(token_group)
        if galleries:
            logger(message, ", ".join([gallery['title'] for gallery in galleries]))
            if len(gids) > 5:  # don't spam chat too much if user spams links
                await client.send_message(message.channel, embed=titles_only(galleries))
            else:
                for ex_metadata in galleries:
                    await client.send_message(message.channel, embed=construct_embed(ex_metadata))
    new_topic = set_topic(message)
    if new_topic:
        await client.edit_channel(message.channel, topic=new_topic[0])


# get the gids and hashes of every EH url posted in a message
def get_gids(message):
    gallery_results = []
    page_results = page_token.findall(message)
    # fix up ordering and types before querying EH
    remapped_results = [[int(elem[1]), elem[0], int(elem[2])] for elem in page_results]
    # divide into chunks of max 25 requests per POST to EH
    for token_group in divide_chunks(remapped_results):
        gallery_results += page_api(token_group)
    gallery_results += [[int(elem[0]), elem[1]] for elem in gallery_token.findall(message)]
    return gallery_results


# Divide lists into chunks of 25 since EH only allows a max of 25 urls per POST request
def divide_chunks(original_chunk):
    return [original_chunk[i:i + 25] for i in range(0, len(original_chunk), 25)]


# Query the EH api for gid from a gallery page url
def page_api(token_group):
    payload = {"method": "gtoken", "pagelist": token_group}
    r = requests.post(EH_API, data=json.dumps(payload))
    return [[elem['gid'], elem['token']] for elem in r.json()['tokenlist']]


# Query the EH api for metadata from a gallery
def gallery_api(token_group):
    payload = {"method": "gdata", "gidlist": token_group, "namespace": 1}
    r = requests.post(EH_API, data=json.dumps(payload))
    return r.json()['gmetadata']


# string of titles for lots of links
def titles_only(exmetas):
    link_list = [create_markdown_url(exmeta['title'], create_ex_url(exmeta['gid'], exmeta['token'])) for exmeta in exmetas]
    msg = "\n".join(link_list)
    return discord.Embed(description=msg,
                         colour=EH_COLOUR)


# make a markdown hyperlink
def create_markdown_url(message, url):
    return "[" + BeautifulSoup(message, "html.parser").string + "](" + url + ")"


# make a EH url from it's gid and token
def create_ex_url(gid, g_token):
    return "https://exhentai.org/g/" + str(gid) + "/" + g_token + "/"


# pretty discord embeds for small amount of links
def construct_embed(exmeta):
    em = discord.Embed(title=BeautifulSoup(exmeta['title'], "html.parser").string,
                       url=create_ex_url(exmeta['gid'], exmeta['token']),
                       timestamp=datetime.datetime.utcfromtimestamp(int(exmeta['posted'])),
                       description=BeautifulSoup(exmeta['title_jpn'], "html.parser").string,
                       colour=EH_COLOUR)
    em.set_image(url=exmeta['thumb'])
    em.set_thumbnail(url=G_CATEGORY[exmeta['category']])
    em.set_footer(text=exmeta['filecount'] + " pages")
    em = process_tags(em, exmeta['tags'])
    return em


# put our tags from the EH JSON response into the discord embed
def process_tags(em, tags):
    tag_dict = {'male': [], 'female': [], 'parody': [], 'character': [], 'misc': []}
    for tag in tags:
        if ":" in tag:
            splitted = tag.split(":")
            if splitted[0] in tag_dict:
                tag_dict[splitted[0]].append(BeautifulSoup(splitted[1], "html.parser").string)
        else:
            tag_dict['misc'].append(tag)

    def add_field(ex_tag):
        if tag_dict[ex_tag]:
            em.add_field(name=ex_tag, value=', '.join(tag_dict[ex_tag]))

    add_field("male")
    add_field("female")
    add_field("parody")
    add_field("character")
    add_field("misc")
    return em


# set topic for the sadpanda server (and test server)
def set_topic(message):
    if message.server.id is "269723851389272065" or "253229838788198400":
        if message.channel.permissions_for(message.server.me).manage_channels:
            return set_topic_re.findall(message.content)
    return []


def logger(message, contents):
    print(message.author.name + " @ " + message.server.name + " @ " + str(message.timestamp))
    print(contents)
    print("-----")


def main():
    client.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
