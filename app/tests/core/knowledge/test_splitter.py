from app.config import settings
from app.core.file.enums import FileType
from app.core.knowledge.base import ProcessRule
from app.core.knowledge.enums import DocumentFormatType
from app.core.knowledge.text.base import TextSplitterRule
from app.core.knowledge.text.keywords import extract_keywords
from app.core.knowledge.text.process import TextProcessor
from app.tests.test_base import _find_first_file


def test_text():
    local_path = _find_first_file()
    print(f"\nlocal_path={local_path}")
    if not local_path:
        return

    docs = list(TextProcessor.load_documents(local_path, FileType.TXT))
    print(f"\ndocs len {len(docs)}")

    text_processor = TextProcessor.get_processor(settings.DEFAULT_PROCESS_RULE)
    documents = text_processor.split_documents(docs)
    print("\ndocuments:")
    for d in documents:
        print(f"{'=*=' * 40}\n{d.content}")


def test_text_line():
    local_path = _find_first_file()
    print(f"\nlocal_path={local_path}")
    if not local_path:
        return

    docs = list(TextProcessor.load_documents(local_path, FileType.TXT))
    print(f"\ndocs len {len(docs)}")

    process_rule = ProcessRule(text_splitter=TextSplitterRule(
        type=DocumentFormatType.TextLine))
    text_processor = TextProcessor.get_processor(process_rule)
    documents = list(text_processor.split_documents(docs))
    print(f"\ndocuments len {len(documents)}:")
    for d in documents:
        print(f"{'=*=' * 40}\n{d.content}")


def test_json_list():
    local_path = _find_first_file()
    print(f"\nlocal_path={local_path}")
    if not local_path:
        return

    docs = list(TextProcessor.load_documents(local_path, FileType.TXT))
    print(f"\ndocs len {len(docs)}")

    process_rule = ProcessRule(text_splitter=TextSplitterRule(
        type=DocumentFormatType.JsonList))
    text_processor = TextProcessor.get_processor(process_rule)
    documents = list(text_processor.split_documents(docs))
    print(f"\ndocuments len {len(documents)}:")
    for d in documents:
        print(f"{'=*=' * 40}\n{d.content}")
        print(f"keywords: {extract_keywords(d.content)}")
