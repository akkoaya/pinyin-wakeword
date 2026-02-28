"""Tests for PinyinWakeWord core."""

from pinyin_wakeword.config import WakeWordConfig
from pinyin_wakeword.core import PinyinWakeWord
from pinyin_wakeword.events import WakeWordEventType


class TestBasicDetection:
    def test_detect_wake_word(self):
        detector = PinyinWakeWord(WakeWordConfig(wake_words="小月"))
        events = detector.feed("你好小月")
        detected = [e for e in events if e.type == WakeWordEventType.DETECTED]
        assert len(detected) == 1
        assert detected[0].matched_text == "小月"
        assert detected[0].wake_word == "小月"
        assert detected[0].confidence == 1.0

    def test_no_detection(self):
        detector = PinyinWakeWord(WakeWordConfig(wake_words="小月"))
        events = detector.feed("你好世界")
        assert len(events) == 1
        assert events[0].type == WakeWordEventType.NOT_DETECTED
        assert events[0].text == "你好世界"

    def test_homophone_detection(self):
        detector = PinyinWakeWord(WakeWordConfig(wake_words="小月"))
        events = detector.feed("晓悦你好")
        detected = [e for e in events if e.type == WakeWordEventType.DETECTED]
        assert len(detected) == 1
        assert detected[0].matched_text == "晓悦"

    def test_check_returns_bool(self):
        detector = PinyinWakeWord(WakeWordConfig(wake_words="小月"))
        assert detector.check("你好小月") is True
        assert detector.check("你好世界") is False

    def test_empty_input(self):
        detector = PinyinWakeWord(WakeWordConfig(wake_words="小月"))
        events = detector.feed("")
        assert events == []

    def test_none_config(self):
        detector = PinyinWakeWord()
        events = detector.feed("小月")
        assert events == []

    def test_position_tracking(self):
        detector = PinyinWakeWord(WakeWordConfig(wake_words="小月"))
        events = detector.feed("你好小月世界")
        detected = [e for e in events if e.type == WakeWordEventType.DETECTED]
        assert detected[0].position == 2


class TestShortMode:
    def test_short_mode_reduces_wake_word(self):
        detector = PinyinWakeWord(
            WakeWordConfig(wake_words="小月小月", short_mode_length=2)
        )
        detector.short_mode = True
        assert detector.check("小月你好") is True

    def test_short_mode_event_flag(self):
        detector = PinyinWakeWord(
            WakeWordConfig(wake_words="小月小月", short_mode_length=2)
        )
        detector.short_mode = True
        events = detector.feed("小月你好")
        detected = [e for e in events if e.type == WakeWordEventType.DETECTED]
        assert detected[0].short_mode is True

    def test_normal_mode_requires_full_word(self):
        detector = PinyinWakeWord(WakeWordConfig(wake_words="小月小月"))
        assert detector.check("小月你好") is False

    def test_short_mode_default_off(self):
        detector = PinyinWakeWord(WakeWordConfig(wake_words="小月小月"))
        assert detector.short_mode is False

    def test_short_mode_custom_length(self):
        detector = PinyinWakeWord(
            WakeWordConfig(wake_words="小月小月", short_mode_length=3)
        )
        detector.short_mode = True
        # "小月小" is 3 chars, should match first 3 chars of "小月小月"
        assert detector.check("你小月小好") is True


class TestMultipleWakeWords:
    def test_detect_first_wake_word(self):
        detector = PinyinWakeWord(
            WakeWordConfig(wake_words=["小月", "小智"])
        )
        events = detector.feed("你好小月")
        detected = [e for e in events if e.type == WakeWordEventType.DETECTED]
        assert len(detected) == 1
        assert detected[0].wake_word == "小月"

    def test_detect_second_wake_word(self):
        detector = PinyinWakeWord(
            WakeWordConfig(wake_words=["小月", "小智"])
        )
        events = detector.feed("你好小智")
        detected = [e for e in events if e.type == WakeWordEventType.DETECTED]
        assert len(detected) == 1
        assert detected[0].wake_word == "小智"

    def test_detect_both_wake_words(self):
        detector = PinyinWakeWord(
            WakeWordConfig(wake_words=["小月", "小智"])
        )
        events = detector.feed("小月和小智")
        detected = [e for e in events if e.type == WakeWordEventType.DETECTED]
        assert len(detected) == 2

    def test_no_not_detected_when_any_matches(self):
        detector = PinyinWakeWord(
            WakeWordConfig(wake_words=["小月", "小智"])
        )
        events = detector.feed("你好小月")
        not_detected = [e for e in events if e.type == WakeWordEventType.NOT_DETECTED]
        assert len(not_detected) == 0


class TestPunctuationHandling:
    def test_strip_punctuation_default(self):
        detector = PinyinWakeWord(WakeWordConfig(wake_words="小月"))
        assert detector.check("小月！") is True

    def test_strip_punctuation_disabled(self):
        detector = PinyinWakeWord(
            WakeWordConfig(wake_words="小月", strip_punctuation=False)
        )
        # With punctuation not stripped, "小月！" has 3 chars but wake word is 2
        # The sliding window will try "小月" and "月！"
        # "小月" should still match since punctuation is just in the text
        assert detector.check("小月！") is True

    def test_punctuation_in_middle_breaks_match(self):
        detector = PinyinWakeWord(WakeWordConfig(wake_words="小月"))
        # "小，月" with strip_punctuation=True becomes "小月" which matches
        assert detector.check("小，月") is True


class TestCallbacks:
    def test_on_detected_callback(self):
        results = []
        detector = PinyinWakeWord(WakeWordConfig(wake_words="小月"))
        detector.on_detected = lambda e: results.append(e)
        detector.feed("你好小月")
        assert len(results) == 1
        assert results[0].type == WakeWordEventType.DETECTED

    def test_on_not_detected_callback(self):
        results = []
        detector = PinyinWakeWord(WakeWordConfig(wake_words="小月"))
        detector.on_not_detected = lambda e: results.append(e)
        detector.feed("你好世界")
        assert len(results) == 1
        assert results[0].type == WakeWordEventType.NOT_DETECTED

    def test_no_callback_when_none(self):
        detector = PinyinWakeWord(WakeWordConfig(wake_words="小月"))
        # Should not raise even without callbacks
        detector.feed("你好小月")
        detector.feed("你好世界")


class TestIterEvents:
    def test_iter_over_stream(self):
        detector = PinyinWakeWord(WakeWordConfig(wake_words="小月"))
        stream = ["你好", "小月你好", "世界"]
        events = list(detector.iter_events(stream))
        detected = [e for e in events if e.type == WakeWordEventType.DETECTED]
        not_detected = [e for e in events if e.type == WakeWordEventType.NOT_DETECTED]
        assert len(detected) == 1
        assert len(not_detected) == 2

    def test_empty_stream(self):
        detector = PinyinWakeWord(WakeWordConfig(wake_words="小月"))
        events = list(detector.iter_events([]))
        assert events == []


class TestAddRemoveWakeWord:
    def test_add_wake_word(self):
        detector = PinyinWakeWord(WakeWordConfig(wake_words="小月"))
        detector.add_wake_word("小智")
        assert detector.check("你好小智") is True

    def test_remove_wake_word(self):
        detector = PinyinWakeWord(
            WakeWordConfig(wake_words=["小月", "小智"])
        )
        detector.remove_wake_word("小月")
        assert detector.check("你好小月") is False
        assert detector.check("你好小智") is True

    def test_add_duplicate_ignored(self):
        detector = PinyinWakeWord(WakeWordConfig(wake_words="小月"))
        detector.add_wake_word("小月")
        assert detector.wake_words == ["小月"]

    def test_remove_nonexistent_safe(self):
        detector = PinyinWakeWord(WakeWordConfig(wake_words="小月"))
        detector.remove_wake_word("不存在")  # Should not raise
        assert detector.wake_words == ["小月"]


class TestReset:
    def test_reset_clears_short_mode(self):
        detector = PinyinWakeWord(WakeWordConfig(wake_words="小月小月"))
        detector.short_mode = True
        detector.reset()
        assert detector.short_mode is False


class TestMinTextLength:
    def test_short_text_skipped(self):
        detector = PinyinWakeWord(
            WakeWordConfig(wake_words="月", min_text_length=2)
        )
        events = detector.feed("月")
        assert events == []

    def test_text_at_min_length(self):
        detector = PinyinWakeWord(
            WakeWordConfig(wake_words="月", min_text_length=1)
        )
        assert detector.check("月") is True


class TestFuzzyMode:
    def test_fuzzy_match(self):
        detector = PinyinWakeWord(
            WakeWordConfig(
                wake_words="小月小月",
                match_mode="fuzzy",
                similarity_threshold=0.7,
            )
        )
        # 3 of 4 syllables match -> 0.75 >= 0.7
        assert detector.check("小月小日") is True

    def test_fuzzy_below_threshold(self):
        detector = PinyinWakeWord(
            WakeWordConfig(
                wake_words="小月小月",
                match_mode="fuzzy",
                similarity_threshold=0.9,
            )
        )
        # 3 of 4 syllables match -> 0.75 < 0.9
        assert detector.check("小月小日") is False


class TestPartialMode:
    def test_partial_exact_match(self):
        """In partial mode, exact match still works."""
        detector = PinyinWakeWord(
            WakeWordConfig(wake_words="小月", match_mode="partial")
        )
        events = detector.feed("你好小月")
        detected = [e for e in events if e.type == WakeWordEventType.DETECTED]
        assert len(detected) == 1

    def test_partial_prefix_match(self):
        detector = PinyinWakeWord(
            WakeWordConfig(wake_words="小月小月", match_mode="partial")
        )
        events = detector.feed("小月")
        partial = [e for e in events if e.type == WakeWordEventType.PARTIAL_MATCH]
        assert len(partial) == 1


class TestEventRepr:
    def test_detected_repr(self):
        detector = PinyinWakeWord(WakeWordConfig(wake_words="小月"))
        events = detector.feed("小月")
        detected = [e for e in events if e.type == WakeWordEventType.DETECTED]
        r = repr(detected[0])
        assert "DETECTED" in r
        assert "小月" in r

    def test_not_detected_repr(self):
        detector = PinyinWakeWord(WakeWordConfig(wake_words="小月"))
        events = detector.feed("世界")
        not_detected = [e for e in events if e.type == WakeWordEventType.NOT_DETECTED]
        r = repr(not_detected[0])
        assert "NOT_DETECTED" in r
