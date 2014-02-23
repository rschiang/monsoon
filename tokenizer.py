import re
import jieba

URL_LIKE_RE = re.compile(ur'\b[a-z]+:/*[a-z0-9\-\._~:/\?#@!$&\+=]+', flags=re.IGNORECASE)

CJK_CHAR_RANGE = ur'\u3040-\u312f\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff'
CJK_LEFT_RE = re.compile(u'([' + CJK_CHAR_RANGE + u'])([^' + CJK_CHAR_RANGE + u'\\s])')
CJK_RIGHT_RE = re.compile(u'([^' + CJK_CHAR_RANGE + u'\\s])([' + CJK_CHAR_RANGE + u'])')
CJK_SLUG_RE = re.compile(u'([' + CJK_CHAR_RANGE + u']+)')

ASCII_SLUG = ur'[a-z_][a-z0-9\-_\.]*'
ASCII_SLUG_RE = re.compile(u'[#@]?(' + ASCII_SLUG + u')', flags=re.IGNORECASE)

def initialize():
	jieba.set_dictionary('vendor/jieba_tc.dict')
	jieba.load_userdict('vendor/chewing.dict')
	jieba.initialize()

# Add whitespace between CJK characters
def preprocess_cjk(text):
	text = CJK_LEFT_RE.sub(r'\1 \2', text)
	text = CJK_RIGHT_RE.sub(r'\1 \2', text)
	return text

def preprocess_url(text):
	text = URL_LIKE_RE.sub('', text)
	return text

def preprocess_ascii(text):
	text = ASCII_SLUG_RE.sub(r' \1 ', text)
	return text

def preprocess(text):
	# Ensure unicode string
	try:
		text = unicode(text, 'utf8')
	except TypeError:
		pass

	text = preprocess_url(text)
	text = preprocess_cjk(text)
	text = preprocess_ascii(text)
	return text

def tokenize(text):
	tokens = []

	text = preprocess(text)
	tokens += ASCII_SLUG_RE.findall(text)	# ASCII tokens are already usable

	for unit in CJK_SLUG_RE.findall(text):	# CJK tokens need extraction
		tokens.extend(jieba.cut_for_search(unit))

	return tokens