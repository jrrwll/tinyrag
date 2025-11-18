import re

import jieba  # type: ignore[import-untyped]
import tiktoken
from nltk.corpus import stopwords  # type: ignore[import-untyped]

"""
import nltk

nltk.download('stopwords')
"""
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


def split_text(text: str, max_len: int = 1024) -> list[str]:
    words = list(jieba.cut(text))
    chunks, cur = [], []
    cur_len = 0
    for w in words:
        if cur_len + len(w) <= max_len:
            cur.append(w)
            cur_len += len(w)
        else:
            if cur:
                chunks.append(''.join(cur))
            cur, cur_len = [w], len(w)
    if cur:
        chunks.append(''.join(cur))
    return chunks
