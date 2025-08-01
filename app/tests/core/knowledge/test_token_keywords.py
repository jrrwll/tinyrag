import this

from app.core.knowledge.text_process.tokens import get_token_count, get_word_count
from app.core.knowledge.text_process.keywords import extract_keywords


def test_word_keywords():
    print("\ntest this.s")
    print(f"word_count: {get_word_count(this.s)}")

    print(f"keywords:\n{extract_keywords(this.s)}")


def test_token():
    print("\ntest this.s")
    print(f"token_count: {get_token_count(this.s)}")
