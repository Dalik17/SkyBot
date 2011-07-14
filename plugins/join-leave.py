from util import hook

@hook.command
def join(inp, input=None):
	"MCBot: join <channel>"
	if input.nick not in input.bot.config["admins"]:
		return "Only bot admins can use this command!"
	chan = inp.split(' ', 1)
	#if len(chan) != 1:
		#return "Usage: MCBot: join <channel>"
	input.say("Joining " + inp + " :D")
	input.conn.send("JOIN " + inp)

@hook.command
def leave(inp, input=None):
	"MCBot: leave <channel>"
	if input.nick not in input.bot.config["admins"]:
		return "Only bot admins can use this command!"
	chan = inp.split(' ', 1)
	#if len(chan) != 1:
		#return "Usage: MCBot: leave <channel>"
	input.say("Kicked out of " + inp + " >:(")
	input.conn.send("PART " + inp)

