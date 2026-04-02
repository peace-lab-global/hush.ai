"""单句后处理单元测试。"""

from hushai.postprocess import to_one_sentence


def test_chinese_first_sentence():
    assert to_one_sentence("你好。世界") == "你好。"


def test_english_exclamation():
    assert to_one_sentence("Hello! World") == "Hello!"


def test_first_line_when_no_punctuation():
    assert to_one_sentence("no punctuation here\nsecond line") == "no punctuation here"


def test_long_line_truncated_without_punctuation():
    long = "x" * 400
    out = to_one_sentence(long)
    assert len(out) == 300
    assert out == "x" * 300


def test_empty():
    assert to_one_sentence("") == ""
    assert to_one_sentence("   ") == ""


def test_question_mark():
    assert to_one_sentence("为何如此? 下一句") == "为何如此?"
