#!/usr/bin/python2
import lala
import ConfigParser
import sys

def main():
    """Main method"""
    config = ConfigParser.SafeConfigParser()
    config.read("config")
    lalaconfig = config._sections["lala"]
    if "-d" in sys.argv:
        debug = True
    else:
        debug = False
    bot = lala.Bot(
            server=lalaconfig["server"],
            admin=lalaconfig["admin"],
            port=int(lalaconfig["port"]),
            nick=lalaconfig["nick"],
            channel=lalaconfig["channel"],
            debug=debug
            )
    #try:
    bot.mainloop()
    #except RuntimeError, e:
        #print e

if __name__ == '__main__':
    main()
