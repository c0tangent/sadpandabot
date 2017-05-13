# sadpandabot

A discord bot which grabs E-Hentai metadata for E-Hentai links in the chat using discord.py.

## Installing and running

Use the docker image for simple installation, otherwise, use `python >= 3.5` and install the packages in `requirements.txt`. Also set the `DISCORD_TOKEN` env variable (or edit the code to use your discord token).

```
git clone https://github.com/c0tangent/sadpandabot
cd sadpandabot
pip install -r requirements.txt
python3 sadpandabot.py
```

### docker

```
docker run -e "DISCORD_TOKEN=<your discord token here>" cotangent/sadpandabot:0.3.3
```
