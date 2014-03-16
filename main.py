#! /usr/bin/python
import config
import tokenizer
from tracker import TrendTracker
from irc.bot import SingleServerIRCBot
from worker import SyncThread

class MonsoonBot(SingleServerIRCBot):

	def __init__(self):
		self.tracker = TrendTracker()
		self.sync_thread = SyncThread(self)
		super(MonsoonBot, self).__init__([(config.server, config.port)], config.nickname, config.nickname, 2)
		self.sync_thread.start()

	def is_authorized(self, sender):
		return config.channel in self.channels and self.channels[config.channel].is_oper(sender)

	def on_nicknameinuse(self, c, e):
		c.nick(c.get_nickname() + '_')

	def on_welcome(self, c, e):
		c.join(config.channel)

	def on_pubmsg(self, c, e):
		sender = e.source.nick
		message = e.arguments[0]

		if sender != c.get_nickname():
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
		arguments = message.split(' ')

		if arguments[0] == 'stat':
			if len(arguments) > 1 and arguments[1] == 'announce':
				target = config.channel 	# Send back to channel
			else:
				target = sender

			trend = self.tracker.get_keyword_trend()
			c.notice(target, "Trending keywords: %s" % ', '.join(trend))

			trend = self.tracker.get_user_trend()
			c.notice(target, "Most active users: %s" % ', '.join(trend))

		elif arguments[0] == 'sync':
			c.notice(sender, "Syncing trend information...")
			self.tracker.sync()
			c.notice(sender, "Done with sync works.")

		elif arguments[0] == "import":
			if len(arguments) < 2:
				c.notice(sender, "You must specify a log date.")
			else:
				self.tracker.import_log(arguments[1])
				c.notice(sender, "Done with importing.")

		elif arguments[0] == 'halt':
			# Shuts the connection and keep idle
			self.ircobj.disconnect_all()
			self.sync_thread.stop()

		elif arguments[0] == 'close':
			# Tore down the whole process
			self.ircobj.disconnect_all()
			self.sync_thread.stop()
			import sys; sys.exit()

		else:
			c.notice(sender, "Unknown command, please retry.")



if __name__ == '__main__':

	# Set loose decoding constraint
	from irc.client import ServerConnection
	ServerConnection.buffer_class.errors = 'replace'

	# Load tokenizer
	tokenizer.initialize()

	bot = MonsoonBot()
	bot.start()
