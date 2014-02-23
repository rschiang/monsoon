from codecs import open

# Use MoeDict MeeGo's index. Available at github.com/rschiang/moedict-meego/
with open('../vendor/moedict/index.json', 'r', encoding='utf8') as index:
	q = {}
	for k in e:
		i = e[k]
		try:
			i = i.replace('\'', '\"')
			i = json.loads(i)
		except:
			continue
		if not 'h' in i: continue
		for h in i['h']:
			if not 'd' in h: continue
			for d in h['d']:
				if not 't' in d: continue
				t=d['t']
				if t == u'連' or t == u'介' or t == u'助':
					l=q.get(k, [])
					if t in l: continue
					q[k] = l + [t]

with open('../vendor/moedict.dict', 'w+', encoding='utf8') as output:
	for k in q:
		output.write('%s %s\n' % (k, ','.join(q[k])))
