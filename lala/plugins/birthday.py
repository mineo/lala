from ConfigParser import NoOptionError
import logging

from datetime import datetime, date, timedelta
from lala.util import command, msg, on_join
from lala.config import get, set

_CONFIG_TIME_FORMAT = "%d.%m.%Y"


def _set_birthday(user, channel, date_to_parse):
    today = date.today()
    # Add the year to know if the birthday already happened in this year
    date_to_parse = date_to_parse + str(today.year)
    try:
        logging.debug("Parsing %s" % date_to_parse)
        date_of_birth = datetime.strptime(date_to_parse, _CONFIG_TIME_FORMAT)
        if today > date_of_birth.date():
            date_to_parse = date_to_parse[:-4] + str(today.year + 1)
            logging.debug("Parsing %s" % date_to_parse)
            date_of_birth = datetime.strptime(date_to_parse, _CONFIG_TIME_FORMAT)
    except ValueError:
        msg(channel, "Sorry %s, I couldn't parse %s into a valid date" % (date_to_parse))
        return

    set(user, date_of_birth.strftime(_CONFIG_TIME_FORMAT))


@command
def my_birthday_is(user, channel, text):
    """Sets the users date of birth. The format is %d.%m."""
    date_to_parse = text.split()[1]
    _set_birthday(user, channel, date_to_parse)


@on_join
def birthday_join_notice(user, channel):
    """Greets the user with 'Happy birthday' if it's his birthday.
    Also sets the birthday of the user to next year so he doesn't get
    congratulations twice."""
    try:
        date_of_birth = datetime.strptime(get(user), _CONFIG_TIME_FORMAT).date()
    except NoOptionError:
        return
    today = date.today()
    if date_of_birth == today:
        msg(channel, "\o\ Happy birthday, %s /o/" % user)
        date_of_birth = date_of_birth + timedelta(days=365)
        set(user, date_of_birth.strftime(_CONFIG_TIME_FORMAT))
    elif date_of_birth < today:
        # The users date of birth in this year is already in the past but the
        # configuration file entry doesn't reflect that. This can happen if he
        # didn't join the channel on his birthday.
        _set_birthday(user, channel, "%i.%i." % (date_of_birth.day, date_of_birth.month))
