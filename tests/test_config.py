"""Tests for WakeWordConfig."""

from pinyin_wakeword.config import WakeWordConfig


class TestDefaults:
    def test_default_wake_words_empty(self):
        cfg = WakeWordConfig()
        assert cfg.wake_words == []

    def test_default_short_mode_length(self):
        cfg = WakeWordConfig()
        assert cfg.short_mode_length == 2

    def test_default_match_mode(self):
        cfg = WakeWordConfig()
        assert cfg.match_mode == "exact"

    def test_default_min_text_length(self):
        cfg = WakeWordConfig()
        assert cfg.min_text_length == 1

    def test_default_similarity_threshold(self):
        cfg = WakeWordConfig()
        assert cfg.similarity_threshold == 0.8

    def test_default_strip_punctuation(self):
        cfg = WakeWordConfig()
        assert cfg.strip_punctuation is True

    def test_default_pinyin_style(self):
        cfg = WakeWordConfig()
        assert cfg.pinyin_style == "normal"


class TestCustomValues:
    def test_string_wake_word_wrapped_in_list(self):
        cfg = WakeWordConfig(wake_words="小月小月")
        assert cfg.wake_words == ["小月小月"]

    def test_list_wake_words_kept_as_list(self):
        cfg = WakeWordConfig(wake_words=["小月小月", "你好小智"])
        assert cfg.wake_words == ["小月小月", "你好小智"]

    def test_empty_string_gives_empty_list(self):
        cfg = WakeWordConfig(wake_words="")
        assert cfg.wake_words == []

    def test_custom_short_mode_length(self):
        cfg = WakeWordConfig(short_mode_length=3)
        assert cfg.short_mode_length == 3

    def test_custom_match_mode(self):
        cfg = WakeWordConfig(match_mode="fuzzy")
        assert cfg.match_mode == "fuzzy"

    def test_custom_similarity_threshold(self):
        cfg = WakeWordConfig(similarity_threshold=0.9)
        assert cfg.similarity_threshold == 0.9

    def test_custom_pinyin_style(self):
        cfg = WakeWordConfig(pinyin_style="tone")
        assert cfg.pinyin_style == "tone"


class TestRepr:
    def test_repr_contains_class_name(self):
        cfg = WakeWordConfig(wake_words="小月")
        r = repr(cfg)
        assert r.startswith("WakeWordConfig(")

    def test_repr_contains_wake_words(self):
        cfg = WakeWordConfig(wake_words="小月")
        r = repr(cfg)
        assert "wake_words=" in r
