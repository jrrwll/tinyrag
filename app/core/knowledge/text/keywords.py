import re

import jieba # type: ignore[import-untyped]
import jieba.analyse # type: ignore[import-untyped]

from app.core.knowledge.text.tokens import _stopwords


def extract_keywords(text: str, top_k: int = 10) -> list[str]:
    tokens = jieba.analyse.extract_tags(
        sentence=text,
        topK=top_k,
    )

    keywords = set()
    for token in tokens:
        # keywords.add(token)
        sub_tokens = re.findall(r"\w+", token)
        for w in sub_tokens:
            if w not in _stopwords:
                keywords.add(w)

    return list(keywords)
