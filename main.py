#! /usr/bin/python
import config
from irc.bot import SingleServerIRCBot

class MonsoonBot(SingleServerIRCBot):

	def __init__(self):
		super(MonsoonBot, self).__init__([(config.server, config.port)], config.nickname, config.nickname, 2)

	def is_authorized(self, sender):
		return config.channel in self.channels and self.channels[config.channel].is_oper(sender)

	def on_nicknameinuse(self, c, e):
		c.nick(c.get_nickname() + '_')

	def on_welcome(self, c, e):
		c.join(config.channel)

	def on_pubmsg(self, c, e):
		sender = e.source.nick
		message = e.arguments[0]
		print '<%s> %s' % (sender, message)

	def on_privmsg(self, c, e):
		sender = e.source.nick
		message = e.arguments[0]

		if self.is_authorized(sender):
			print '*%s* %s' % (sender, message)

	def on_privnotice(self, c, e):
		sender = e.source.nick
		message = e.arguments[0]
		print self.channels.keys()

		if self.is_authorized(sender):
			print '!%s! %s' % (sender, message)

if __name__ == '__main__':

	# Set loose decoding constraint
	from irc.client import ServerConnection
	ServerConnection.buffer_class.errors = 'replace'

	bot = MonsoonBot()
	bot.start()
