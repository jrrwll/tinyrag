import this

from app.core.knowledge.text_process.tokens import get_token_count, get_word_count
from app.core.knowledge.text_process.keywords import extract_keywords
from app.tests import print_time


def test_word_keywords(print_time):
    print("\ntest this.s")
    print(f"word_count: {get_word_count(this.s)}")

    print(f"keywords:\n{extract_keywords(this.s)}")


def test_token(print_time):
    print("\ntest this.s")
    print(f"token_count: {get_token_count(this.s)}")
