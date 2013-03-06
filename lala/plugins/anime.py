import anidb
import logging

from lala.util import command, msg
from lala.config import get_int, set_default_options

anidb.set_client("pyanihttp", 1)
set_default_options(max_tags="5", max_search_results="5")

def get_anime(user, channel, text):
    try:
        aid = int(text.split()[1])
    except ValueError:
        msg(channel, "%s: %s can't be parsed into an anime id" % (user,
            text.split()[1]))
        return None
    except IndexError:
        return None
    logging.info("Querying AniDb for information about %i" % aid)
    try:
        anime = anidb.query(anidb.QUERY_ANIME, aid)
    except anidb.exceptions.BannedException:
        msg(channel, "%s: Sorry, looks like I'm banned from using the HTTP api"
                % user)
        return None
    if anime is None:
        logging.info("No data")
        msg(channel, "%s: Sorry, no data could be retrieved" % user)
        return None
    return anime

@command
def atags(user, channel, text):
    """Show the tags of an anime. Parameters: an aid"""
    anime = get_anime(user, channel, text)
    if anime is None:
        return
    anime.tags.sort(cmp=lambda x, y: cmp(int(x.count), int(y.count)))
    anime.tags.reverse()
    tags = [tag.name for tag in anime.tags]
    msg(channel, "Anime %s is tagged %s" % (anime.id,
            ", ".join(tags[:get_int("max_tags")])))

@command
def ainfo(user, channel, text):
    """Query the AniDB for information about an anime. Parameters: An aid"""
    anime = get_anime(user, channel, text)
    if anime is None:
        return
    info_s = "Anime #%i: %i episodes." % (anime.id,
            anime.episodecount)
    if anime.startdate is not None:
        info_s += " Airing from: %s" % (anime.startdate)
    if anime.enddate is not None:
        info_s += " to: %s" % (anime.enddate)
    msg(channel, info_s)

    rating_s = u"Ratings:"
    for i in ("permanent", "temporary"):
        if anime.ratings[i]["count"] is not None:
            rating_s += " %s: %.2f by %i people." % \
                (i,
                 anime.ratings[i]["rating"],
                 anime.ratings[i]["count"])
    msg(channel, rating_s)
    titles = []
    for lang in ("ja", "x-jat", "en", "de"):
        try:
            titles += [title.title for title in anime.titles[lang] if title.type ==
                    "main" or title.type == "official"]
        except KeyError:
            # There are no titles for that language
            pass
    title_s = "Known as: %s" % ", ".join(titles)
    msg(channel, title_s)

@command
def asearch(user, channel, text):
    """Search for an anime"""
    try:
        name = " ".join(text.split()[1:])
    except KeyError:
        pass
    logging.info(name)
    results = anidb.search(name)
    max_results = get_int("max_search_results")

    if len(results) > max_results:
        msg(channel, "%s: Too many results, please refine your search" % user)
        return

    result_strings = []
    for anime in results:
        titles = []
        for lang in ("ja", "x-jat", "en", "de"):
            try:
                titles += [title.title for title in anime.titles[lang] if title.type ==
                        "main" or title.type == "official"]
            except KeyError:
                # There are no titles for that language
                pass
        result_strings.append("%i: %s" % (anime.id, ", ".join(titles)))
    msg(channel, result_strings)
