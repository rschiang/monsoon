from tokenizer import tokenize

class TrendTracker(object):

	def __init__(self):
		self.users = {}
		self.words = {}
		self.initialize()

	def initialize(self):
		pass

	def track_message(self, user, message):
		self.users[user] = self.users.get(user, 0) + 1
		for word in tokenize(message):
			self.words[word] = self.words.get(word, 0) + 1

	def get_user_trend(self, limit=5):
		return sorted(self.users.keys(), key=lambda x: self.users[x], reverse=True)[:limit]

	def get_keyword_trend(self, limit=10):
		return sorted(self.words.keys(), key=lambda x: self.words[x], reverse=True)[:limit]

	def sync(self):
		pass