"""Tests for pinyin matching algorithms."""


from pinyin_wakeword.matchers import (
    match_exact,
    match_fuzzy,
    match_partial,
    strip_punctuation,
)


class TestStripPunctuation:
    def test_chinese_punctuation(self):
        assert strip_punctuation("你好，世界！") == "你好世界"

    def test_english_punctuation(self):
        assert strip_punctuation("hello, world!") == "hello world"

    def test_mixed(self):
        assert strip_punctuation("你好。hello!") == "你好hello"

    def test_no_punctuation(self):
        assert strip_punctuation("你好世界") == "你好世界"

    def test_empty_string(self):
        assert strip_punctuation("") == ""


class TestMatchExact:
    def test_exact_match_at_start(self):
        results = match_exact("小月你好", "小月")
        assert len(results) == 1
        pos, text, conf = results[0]
        assert pos == 0
        assert text == "小月"
        assert conf == 1.0

    def test_exact_match_in_middle(self):
        results = match_exact("你好小月世界", "小月")
        assert len(results) == 1
        pos, text, _ = results[0]
        assert pos == 2
        assert text == "小月"

    def test_exact_match_at_end(self):
        results = match_exact("你好小月", "小月")
        assert len(results) == 1
        assert results[0][0] == 2

    def test_homophone_match(self):
        """晓悦 and 小月 have the same pinyin."""
        results = match_exact("你好晓悦世界", "小月")
        assert len(results) == 1
        pos, text, _ = results[0]
        assert pos == 2
        assert text == "晓悦"

    def test_no_match(self):
        results = match_exact("你好世界", "小月")
        assert len(results) == 0

    def test_multiple_matches(self):
        results = match_exact("小月你好小月", "小月")
        assert len(results) == 2
        assert results[0][0] == 0
        assert results[1][0] == 4

    def test_empty_text(self):
        results = match_exact("", "小月")
        assert len(results) == 0

    def test_empty_wake_word(self):
        results = match_exact("你好", "")
        assert len(results) == 0

    def test_text_shorter_than_wake_word(self):
        results = match_exact("小", "小月小月")
        assert len(results) == 0

    def test_full_wake_word_four_chars(self):
        results = match_exact("请问小月小月你好吗", "小月小月")
        assert len(results) == 1
        pos, text, _ = results[0]
        assert pos == 2
        assert text == "小月小月"

    def test_exact_length_match(self):
        results = match_exact("小月", "小月")
        assert len(results) == 1
        assert results[0][0] == 0


class TestMatchFuzzy:
    def test_perfect_match_returns_1(self):
        results = match_fuzzy("小月", "小月", threshold=0.5)
        assert len(results) == 1
        assert results[0][2] == 1.0

    def test_one_syllable_mismatch(self):
        """小日 vs 小月: 'xiao' matches, 'ri' != 'yue' -> 0.5 similarity."""
        results = match_fuzzy("小日", "小月", threshold=0.5)
        assert len(results) == 1
        assert results[0][2] == 0.5

    def test_below_threshold_excluded(self):
        results = match_fuzzy("大日", "小月", threshold=0.8)
        assert len(results) == 0

    def test_three_of_four_match(self):
        """Three matching syllables out of four -> 0.75 confidence."""
        results = match_fuzzy("小月小日", "小月小月", threshold=0.7)
        assert len(results) >= 1
        assert results[0][2] == 0.75

    def test_empty_inputs(self):
        assert match_fuzzy("", "小月", threshold=0.5) == []
        assert match_fuzzy("小月", "", threshold=0.5) == []


class TestMatchPartial:
    def test_prefix_match(self):
        results = match_partial("小月", "小月小月")
        assert len(results) == 1
        assert results[0][2] == 0.5  # 2 of 4 syllables

    def test_single_char_prefix(self):
        results = match_partial("小", "小月")
        assert len(results) == 1
        assert results[0][2] == 0.5

    def test_homophone_prefix(self):
        results = match_partial("晓", "小月")
        assert len(results) == 1

    def test_non_prefix(self):
        results = match_partial("世界", "小月")
        assert len(results) == 0

    def test_full_length_not_partial(self):
        """If text length >= wake word length, no partial match."""
        results = match_partial("小月小月", "小月")
        assert len(results) == 0

    def test_empty_text(self):
        assert match_partial("", "小月") == []

    def test_empty_wake_word(self):
        assert match_partial("小", "") == []
