import random
from lala.util import command, msg

class revolver:
    def __init__(self):
        self.reload()

    def reload(self):
        self.bullet = random.randint(1,6)
        self.chamber = 1

    def shoot(self, user, channel, text):
        if (self.chamber >= 5) and (self.chamber != self.bullet):
            msg(channel, "%s: Chamber %s of 6: *click*" % (user, self.chamber))
            msg(channel, "Reloading")
            self.reload()

        elif (self.chamber == self.bullet):
            msg(channel, "%s: Chamber %s of 6: BOOM" % (user, self.chamber))
            self.reload()
            msg(channel, "Reloading")

        else:
            msg(channel, "%s: Chamber %s of 6: *click*" % (user, self.chamber))
            self.chamber += 1

gun = revolver()

@command
def reload(user, channel, text):
    gun.reload()
    msg(channel, "Can't you see I'm reloading")
@command
def shoot(user, channel, text):
    gun.shoot(user, channel, text)
