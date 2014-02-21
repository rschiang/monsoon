import re

# Modified from pangu.py 1.0.0 | https://github.com/vinta/pangu.py | MIT License
CJK_CHAR_RANGE = ur'\u3040-\u312f\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff'
CJK_LEFT_RE = re.compile(u'([' + CJK_CHAR_RANGE + u'])([^' + CJK_CHAR_RANGE + u'\\s])')
CJK_RIGHT_RE = re.compile(u'([^' + CJK_CHAR_RANGE + u'\\s])([' + CJK_CHAR_RANGE + u'])')
URL_LIKE_RE = re.compile(ur'\b[a-z]+:/*[a-z0-9\-\._~:/\?#@!$&\+=]+', flags=re.IGNORECASE)
ASCII_SLUG = ur'[a-z_][a-z0-9\-_\.]*'
ASCII_SLUG_RE = re.compile(u'[#@]?(' + ASCII_SLUG + u')', flags=re.IGNORECASE)

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
	text = preprocess_url(text)
	text = preprocess_cjk(text)
	text = preprocess_ascii(text)
	return text
