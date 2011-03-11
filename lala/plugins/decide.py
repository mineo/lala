import logging

from random import choice
from lala.util import command, msg

@command("decide")
def decide(user, channel, text):
    s_text = text.split("/")
    s_text[0] = " ".join(s_text[0].split()[1:])
    msg(channel, "%s: %s" %(user, choice(s_text)))
