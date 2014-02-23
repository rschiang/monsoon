import config
from tokenizer import tokenize
from datetime import datetime

# Used for repo synchornization
import json
from git import *
from codecs import open

class TrendTracker(object):

	def __init__(self):
		self.users = {}
		self.words = {}
		self.log = []
		self.initialize()

	def initialize(self):
		if config.logging_repo:
			repo = Repo.clone_from(config.logging_repo, 'log/')
			with repo.config_writer() as conf:
				conf.set_value('user', 'name', config.logging_name or 'Monsoon')
				conf.set_value('user', 'email', config.logging_email or 'monsoon@sitcon.org')

			try:
				with open('log/statistics.json', 'r', encoding='utf8') as f:
					data = json.load(f)
					self.users = data['users']
					self.words = data['words']

			except IOError:
				print 'No statistic to resume from.'
				return

	def track_message(self, user, message):
		# Append statistics
		self.users[user] = self.users.get(user, 0) + 1
		
		for word in tokenize(message):
			self.words[word] = self.words.get(word, 0) + 1

		# Append log
		self.log.append({
				'time': datetime.utcnow().isoformat(),
				'user': user,
				'text': message,
			})

	def get_user_trend(self, limit=5):
		return sorted(self.users.keys(), key=lambda x: self.users[x], reverse=True)[:limit]

	def get_keyword_trend(self, limit=10):
		return sorted([k in self.words.keys() if len(k) > 1], key=lambda x: self.words[x], reverse=True)[:limit]

	def sync(self):
		if config.logging_repo:
			repo = Repo('log/')
			repo.remotes.origin.pull(rebase=True)

			with open('log/statistics.json', 'w+', encoding='utf8') as f:
				json.dump({
					'users': self.users,
					'words': self.words, 
					}, f, ensure_ascii=False, indent=4)

			with open('log/trends.json', 'w+', encoding='utf8') as f:
				json.dump({
					'users': self.get_user_trend(),
					'words': self.get_keyword_trend(),
					}, f, ensure_ascii=False, indent=4)

			from itertools import groupby
			for date, group in groupby(self.log, lambda x: x['time'][:10]):
				# First 10 chars of ISO format is date
				with open('log/%s.log' % date, 'a+', encoding='utf8') as f:
					json.dump(list(group), f, ensure_ascii=False, indent=4)

				repo.index.add(['%s.log' % date])

			repo.index.add(['statistics.json', 'trends.json'])
			repo.index.commit('Updating log %s' % datetime.utcnow().isoformat())

			repo.remotes.origin.push()
