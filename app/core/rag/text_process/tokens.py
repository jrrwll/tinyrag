import re

import jieba
import jieba.analyse
import nltk
import tiktoken
from nltk.corpus import stopwords

# nltk.download('stopwords')
_stopwords = set(stopwords.words('english') + stopwords.words('chinese'))


def get_token_count(text: str, encoding: str = 'cl100k_base') -> int:
    """
    :py:attr:`tiktoken.model.MODEL_TO_ENCODING`
    """
    enc = tiktoken.get_encoding(encoding)
    return len(enc.encode(text))


def get_word_count(text: str) -> int:
    en = [w for w in re.findall(r'\b\w+\b', text) if w not in _stopwords]
    zh = [w for w in jieba.lcut(text) if w not in _stopwords
          and re.search(r'[\u4e00-\u9fff]', w)]
    return len(en) + len(zh)
