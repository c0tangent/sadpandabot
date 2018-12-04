import datetime
import os

import discord
from bs4 import BeautifulSoup
from discord.ext import commands

import ehapi

DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
description = "A discord bot which grabs E-Hentai metadata for E-Hentai links in the chat."
bot = commands.Bot(command_prefix='!', description=description)

BASE = "https://cdn.discordapp.com/attachments/306823976615936002/"
G_CATEGORY = {
    "Doujinshi": BASE + "471642768180117524/doujinshi.png",
    "Manga": BASE + "471642771862716446/manga.png",
    "Artist CG Sets": BASE + "471642764623478804/artistcg.png",
    "Game CG Sets": BASE + "471642769169842176/gamecg.png",
    "Western": BASE + "471642775964745729/western.png",
    "Non-H": BASE + "471642774350069771/non-h.png",
    "Image Sets": BASE + "471642770331926558/imageset.png",
    "Cosplay": BASE + "471642766993260544/cosplay.png",
    "Asian Porn": BASE + "471642765781106689/asianporn.png",
    "Misc": BASE + "471642773087322112/misc.png"
}
EH_COLOUR = discord.Colour(0x660611)


@bot.event
async def on_ready():
    print("Logged in as " + bot.user.name + " " + str(bot.user.id))
    print("------")


@bot.event
async def on_message(message):
    await parse_exlinks(message)
    await bot.process_commands(message)


# search for EH links and post their metadata
async def parse_exlinks(message):
    galleries = ehapi.get_galleries(message.content)
    if galleries:
        logger(message, ", ".join([gallery['token'] for gallery in galleries]))
        if len(galleries) > 5:  # don't spam chat too much if user spams links
            await message.channel.send(embed=embed_titles(galleries))
        else:
            for gallery in galleries:
                await message.channel.send(embed=embed_full(gallery))


# string of titles for lots of links
def embed_titles(exmetas):
    link_list = [create_markdown_url(exmeta['title'], create_ex_url(exmeta['gid'], exmeta['token'])) for exmeta in
                 exmetas]
    msg = "\n".join(link_list)
    return discord.Embed(description=msg,
                         colour=EH_COLOUR)


# pretty discord embeds for small amount of links
def embed_full(exmeta):
    em = discord.Embed(title=BeautifulSoup(exmeta['title'], "html.parser").string,
                       url=create_ex_url(exmeta['gid'], exmeta['token']),
                       timestamp=datetime.datetime.utcfromtimestamp(int(exmeta['posted'])),
                       description=BeautifulSoup(exmeta['title_jpn'], "html.parser").string,
                       colour=EH_COLOUR)
    em.set_image(url=exmeta['thumb'])
    em.set_thumbnail(url=G_CATEGORY[exmeta['category']])
    em.set_footer(text=exmeta['filecount'] + " pages")
    em.add_field(name="rating", value=exmeta['rating'])
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


# make a markdown hyperlink
def create_markdown_url(message, url):
    return "[" + BeautifulSoup(message, "html.parser").string + "](" + url + ")"


# make a EH url from it's gid and token
def create_ex_url(gid, g_token):
    return "https://exhentai.org/g/" + str(gid) + "/" + g_token + "/"


# crude, but using Docker so ¯\_(ツ)_/¯
def logger(message, contents):
    print(contents)


def main():
    print("Logging in...")
    bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
