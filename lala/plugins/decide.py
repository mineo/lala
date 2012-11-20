from random import choice
from lala.util import command, msg

@command
def decide(user, channel, text):
    """Pick one choice in an arbitrary list of choices separated by a slash"""
    s_text = text.split("/")
    s_text[0] = " ".join(s_text[0].split()[1:])
    msg(channel, "%s: %s" %(user, choice(s_text)))
