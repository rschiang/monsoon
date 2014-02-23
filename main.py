#! /usr/bin/python
import config
import tokenizer
from tracker import TrendTracker
from irc.bot import SingleServerIRCBot

class MonsoonBot(SingleServerIRCBot):

	def __init__(self):
		self.tracker = TrendTracker()
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
		self.tracker.track_message(sender, message)

	def on_privmsg(self, c, e):
		sender = e.source.nick
		message = e.arguments[0]
		print '*%s* %s' % (sender, message)

		if self.is_authorized(sender):
			self.process_command(c, (sender, message))
		else:
			c.notice(sender, "Hi, this is Monsoon.")

	def process_command(self, c, e):
		sender, message = e
		if message == 'stat':
			trend = self.tracker.get_keyword_trend()
			c.notice(sender, "Trending keywords: %s" % ', '.join(trend))

			trend = self.tracker.get_user_trend()
			c.notice(sender, "Most active users: %s" % ', '.join(trend))

		elif message == 'halt':
			# Shuts the connection and keep idle
			self.ircobj.disconnect_all()

		elif message == 'close':
			# Tore down the whole process
			self.ircobj.disconnect_all()
			import sys; sys.exit()


if __name__ == '__main__':

	# Set loose decoding constraint
	from irc.client import ServerConnection
	ServerConnection.buffer_class.errors = 'replace'

	# Load tokenizer
	tokenizer.initialize()

	bot = MonsoonBot()
	bot.start()
