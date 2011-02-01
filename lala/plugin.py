class baseplugin(object):
    name = "baseplugin"
    author = "mineo"
    def __init__(self, Bot):
        raise NotImplementedError()

    def call(self, Bot, user, channel, text):
        raise NotImplementedError()
