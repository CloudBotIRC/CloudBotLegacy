import re

from util import hook, http, web

gateway = 'https://play.spotify.com/{}/{}'
spuri = 'spotify:{}:{}'

spotify_re = (r'(spotify:(track|album|artist|user):([a-zA-Z0-9:]+))', re.I)
http_re = (r'((open|play)\.spotify\.com\/(track|album|artist|user)\/'
              '([a-zA-Z0-9\/]+))', re.I)


def format_track(item):
    try:
        type, id = item["uri"].split(":")[1:]
    except IndexError:
        return "Could not find track."
    url = web.try_isgd(gateway.format(type, id))
    out = u"\x02{}\x02 by \x02{}\x02".format(item["name"], ",".join(a["name"] for a in item["artists"]))
    out += u" from \x02{}\x02".format(item["album"]["name"]) if "name" in item["album"] else ""
    out += u" - \x02{}\x02".format(url)
    return out


def format_album(item):
    try:
        type, id = item["uri"].split(":")[1:]
        more_data = http.get_json("https://api.spotify.com/v1/albums/{}".format(id))
        item.update(more_data)
    except Exception as e:
        return "Could not get album: {}".format(e)
    url = web.try_isgd(gateway.format(type, id))
    return u"\x02{}\x02 by \x02{}\x02 - \x02{}\x02".format(item["name"], ",".join(a["name"] for a in item["artists"]), url)


def format_artist(item):
    try:
        type, id = item["uri"].split(":")[1:]
    except IndexError:
        return "Could not find artist."
    url = web.try_isgd(gateway.format(type, id))
    return u"\x02{}\x02 - \x02{}\x02".format(item["name"], url)


@hook.command('sptrack')
@hook.command('spotify')
@hook.command
def spotify_track(inp):
    "spotify <song> -- Search Spotify for <song>"
    return spotify(inp)


def spotify(inp):
    try:
        data = http.get_json("https://api.spotify.com/v1/search", type="track", limit="1", q=inp.strip())
        item = data["tracks"]["items"][0]
    except Exception as e:
        return "Could not get information: {}".format(e)
    return format_track(item)


@hook.command
def spalbum(inp):
    "spalbum <album> -- Search Spotify for <album>"
    return spotify_album(inp)


def spotify_album(inp):
    try:
        data = http.get_json("https://api.spotify.com/v1/search", type="album", limit="1", q=inp.strip())
        item = data["albums"]["items"][0]
    except Exception as e:
        return "Could not get information: {}".format(e)
    return format_album(item)


@hook.command
def spartist(inp):
    "spartist <artist> -- Search Spotify for <artist>"
    return spotify_artist(inp)


def spotify_artist(inp):
    try:
        data = http.get_json("https://api.spotify.com/v1/search", type="artist", limit="1", q=inp.strip())
        item = data["artists"]["items"][0]
    except Exception as e:
        return "Could not get information: {}".format(e)
    return format_artist(item)


@hook.regex(*http_re)
@hook.regex(*spotify_re)
def spotify_url(match):
    type = match.group(3)
    spotify_id = match.group(4)
    if type == "user":
        if "/" in spotify_id:
            spidsplit = spotify_id.split("/")
            uname = spidsplit[-3]
            utype = spidsplit[-2]
            spotify_id = spidsplit[-1]
        elif ":" in spotify_id:
            spidsplit = spotify_id.split(":")
            uname = spidsplit[-3]
            utype = spidsplit[-2]
            spotify_id = spidsplit[-1]
        url = "http://open.spotify.com/%s/%s/%s/%s" % (type, uname, utype, spotify_id)
        if utype == "playlist":
            auth = "Bearer BQDQ4-0f_26qPXsh6nUnN1zLiKlfgttROpj3iaismSjEJmR4Xqb-f4mOUvzsyZB_ABjEtMPic4ZYMlqqtS3j7khflDjxsZfpZ4gzVYmiuG6kTsedhrIGAj9W5IrzPC8XonGUVcK3y7Ryi2C0IENsWLonI54"
            data = http.get_json("https://api.spotify.com/v1/users/{}/playlists/{}".format(uname, spotify_id), headers={"Authorization": auth})
            data["owner"].update(http.get_json(data["owner"]["href"]))
            return u"Spotify Playlist: \x02{}\x02 by \x02{}\x02 - {} tracks - \x02{}\x02".format(data["name"], data["owner"]["display_name"], len(data["tracks"]), web.try_isgd(url))
        else:
            return u"Please msg blha303 with this: %s | %s" % (url, match.group())
    url = spuri.format(type, spotify_id)
    if type == "track":
        data = http.get_json("https://api.spotify.com/v1/tracks/{}".format(spotify_id))
        return u"Spotify Track: {}".format(format_track(data) if not "error" in data else "{status}: {message}".format(**data["error"]))
    elif type == "artist":
        data = http.get_json("https://api.spotify.com/v1/artists/{}".format(spotify_id))
        return u"Spotify Artist: {}".format(format_artist(data) if not "error" in data else "{status}: {message}".format(**data["error"]))
    elif type == "album":
        data = http.get_json("https://api.spotify.com/v1/albums/{}".format(spotify_id))
        return u"Spotify Album: {}".format(format_album(data) if not "error" in data else "{status}: {message}".format(**data["error"]))
