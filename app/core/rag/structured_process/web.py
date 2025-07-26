from typing import Iterator, Sequence

import bs4
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document


class WebProcessor():

    def load_web_page(self, web_paths: Sequence[str],
            tag: Sequence[str] | None = None,
            id: Sequence[str] | None = None,
            class_: Sequence[str] | None = None) -> Iterator[Document]:
        bs4_strainer = bs4.SoupStrainer(name=tag, id=id, class_=class_)
        loader = WebBaseLoader(
            web_paths=web_paths,
            bs_kwargs=dict(parse_only=bs4_strainer),
        )
        return loader.lazy_load()
