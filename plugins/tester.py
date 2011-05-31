from util import hook

@hook.command('tester')
@hook.command
def hello(inp):
	return "Hey There!"