from util import hook

@hook.command
def changenick(inp, input=None):
    "EvilDalik: changenick <nick>"
    if input.nick not in input.bot.config["admins"]:
        return "Only bot admins can use this command!"
    chan = inp.split(' ', 1)
    #if len(chan) != 1:
        #return "Usage: omg please part <channel>"
    input.say("Changing nick to " + inp)
    input.conn.send("NICK " + inp)
