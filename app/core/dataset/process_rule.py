from langchain_text_splitters import RecursiveCharacterTextSplitter, \
    TextSplitter

from app.core.dataset.base import ProcessRule


def get_text_splitter(process_rule: ProcessRule) -> TextSplitter:
    text_splitter = process_rule.text_splitter

    return RecursiveCharacterTextSplitter(
        chunk_size=text_splitter.chunk_size,
        chunk_overlap=text_splitter.chunk_overlap,
        separators=text_splitter.separators,
        add_start_index=True
    )
