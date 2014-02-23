from threading import Thread, Event

class SyncThread(Thread):

	def __init__(self, parent):
		Thread.__init__(self)
		self.parent = parent
		self.event = Event()
		self.elapsed = 0
		self.interval = 300

	def run(self):
		while not self.event.is_set():
			if self.elapsed < self.interval:
				self.elapsed += 1
				self.event.wait(1)
			else:
				self.elapsed = 0

				print "Starting periodic synchornization."
				parent.tracker.sync()

	def stop(self):
		self.event.set()