#!/usr/bin/python2
import lala
import ConfigParser

def main():
    """Main method"""
    config = ConfigParser.SafeConfigParser()
    config.read("config")
    lalaconfig = config._sections["lala"]
    bot = lala.Bot(
            server=lalaconfig["server"],
            admin=lalaconfig["admin"],
            port=int(lalaconfig["port"]),
            nick=lalaconfig["nick"],
            channel=lalaconfig["channel"]
            )
    try:
        bot.mainloop()
    except RuntimeError, e:
        print e

if __name__ == '__main__':
    main()
