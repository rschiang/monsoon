import config
from tokenizer import tokenize
from datetime import datetime

# Used for repo synchornization
import json
import traceback

# Workaround to solve os.getlogin issue in git-python
import os
os.getlogin = lambda: config.logging_name or 'Monsoon'

from git import *
from codecs import open
from threading import Lock

class TrendTracker(object):

	def __init__(self):
		self.users = {}
		self.words = {}
		self.log = []
		self.lock = Lock()
		self.initialize()

	def initialize(self):
		self.lock.acquire()
		if config.logging_repo:
			# Initialize clean repo
			from shutil import rmtree
			if os.path.exists('log/'): rmtree('log/')
			repo = Repo.clone_from(config.logging_repo, 'log/')
			
			# Bootstrap configurations
			conf = repo.config_writer()
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
				
		self.lock.release()

	def track_message(self, user, message):
		self.lock.acquire()

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

		self.lock.release()

	def get_user_trend(self, limit=5):
		return sorted(self.users.keys(), key=lambda x: self.users[x], reverse=True)[:limit]

	def get_keyword_trend(self, limit=10):
		return sorted([k for k in self.words.keys() if len(k) > 1], key=lambda x: self.words[x], reverse=True)[:limit]

	def sync(self):
		self.lock.acquire()
		if config.logging_repo:			
			repo = Repo('log/')

			print "--> pulling remote repository."
			try:
				repo.remotes.origin.pull(rebase=True)
			except:
				traceback.print_exc(); return

			with open('log/statistics.json', 'w+', encoding='utf8') as f:
				print "--> writing statistics."
				json.dump({
					'users': self.users,
					'words': self.words, 
					}, f, ensure_ascii=False, indent=4)

			with open('log/trends.json', 'w+', encoding='utf8') as f:
				print "--> writing trends."
				json.dump({
					'users': self.get_user_trend(),
					'words': self.get_keyword_trend(),
					}, f, ensure_ascii=False, indent=4)

			from itertools import groupby
			for date, group in groupby(self.log, lambda x: x['time'][:10]):
				# First 10 chars of ISO format is date
				print "--> writing IRC log of day %s" % date
				with open('log/%s.log' % date, 'a+', encoding='utf8') as f:
					for entry in group:
						f.write('[%s] <%s> %s\n' % (group['time'], group['user'], group['text']))

				repo.index.add(['%s.log' % date])

			repo.index.add(['statistics.json', 'trends.json'])
			repo.index.commit('Updating log %s' % datetime.utcnow().isoformat())

			print "--> pushing to remote repository."
			try:
				repo.remotes.origin.push()
			except:
				traceback.print_exc(); return

		self.lock.release()
