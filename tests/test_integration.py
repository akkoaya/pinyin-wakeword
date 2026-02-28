"""Integration tests for pinyin-wakeword."""

from pinyin_wakeword import PinyinWakeWord, WakeWordConfig, WakeWordEventType


class TestASRPipelineSimulation:
    """Simulate a real ASR pipeline feeding text to the detector."""

    def test_streaming_asr_detection(self):
        """Simulate incremental ASR output where text grows over time."""
        detector = PinyinWakeWord(WakeWordConfig(wake_words="小月小月"))

        # ASR typically sends increasingly complete transcriptions
        asr_outputs = [
            "你",
            "你好",
            "你好小",
            "你好小月",
            "你好小月小",
            "你好小月小月",
            "你好小月小月请问",
        ]

        detected_count = 0
        for text in asr_outputs:
            events = detector.feed(text)
            for event in events:
                if event.type == WakeWordEventType.DETECTED:
                    detected_count += 1

        # Should detect in the texts that contain "小月小月"
        assert detected_count >= 1

    def test_callback_driven_asr(self):
        """Simulate ASR with callback-based event handling."""
        detected_events = []
        missed_events = []

        detector = PinyinWakeWord(WakeWordConfig(wake_words="小智"))
        detector.on_detected = lambda e: detected_events.append(e)
        detector.on_not_detected = lambda e: missed_events.append(e)

        asr_stream = [
            "今天天气怎么样",
            "小智你好",
            "请问明天天气",
            "小智帮我查一下",
        ]

        for text in asr_stream:
            detector.feed(text)

        assert len(detected_events) == 2
        assert len(missed_events) == 2
        assert detected_events[0].wake_word == "小智"

    def test_iter_events_asr(self):
        """Use iter_events for streaming ASR processing."""
        detector = PinyinWakeWord(WakeWordConfig(wake_words="你好"))

        asr_stream = ["早上好", "你好世界", "再见"]
        events = list(detector.iter_events(asr_stream))

        detected = [e for e in events if e.type == WakeWordEventType.DETECTED]
        assert len(detected) == 1
        assert detected[0].matched_text == "你好"


class TestHomophoneScenarios:
    """Test various homophone matching scenarios."""

    def test_common_homophones(self):
        """Test that common homophones are correctly matched."""
        detector = PinyinWakeWord(WakeWordConfig(wake_words="小月"))

        # 晓悦 has the same pinyin as 小月
        assert detector.check("晓悦") is True
        # 小悦 also matches
        assert detector.check("小悦") is True

    def test_different_tones_match_in_normal_mode(self):
        """In normal mode (no tones), different tones match."""
        detector = PinyinWakeWord(
            WakeWordConfig(wake_words="小月", pinyin_style="normal")
        )
        # Characters with same base pinyin but different tones
        assert detector.check("小月") is True


class TestShortModeScenarios:
    """Test short mode in realistic scenarios."""

    def test_speaking_mode_activation(self):
        """Simulate the digital-human scenario: system is speaking,
        user says shortened wake word to interrupt."""
        detector = PinyinWakeWord(
            WakeWordConfig(wake_words="小月小月", short_mode_length=2)
        )

        # Normal mode: full wake word required
        assert detector.check("小月你好吗") is False

        # System starts speaking, activate short mode
        detector.short_mode = True
        assert detector.check("小月你好吗") is True

        # System stops speaking, deactivate short mode
        detector.short_mode = False
        assert detector.check("小月你好吗") is False

    def test_short_mode_with_homophones(self):
        detector = PinyinWakeWord(
            WakeWordConfig(wake_words="小月小月", short_mode_length=2)
        )
        detector.short_mode = True
        # 晓悦 is homophone of 小月
        assert detector.check("晓悦你好") is True


class TestEdgeCases:
    def test_single_character_wake_word(self):
        detector = PinyinWakeWord(WakeWordConfig(wake_words="好"))
        assert detector.check("好") is True
        assert detector.check("你好吗") is True

    def test_long_text(self):
        detector = PinyinWakeWord(WakeWordConfig(wake_words="小月"))
        long_text = "今天天气很好" * 100 + "小月" + "明天也不错" * 100
        assert detector.check(long_text) is True

    def test_wake_word_with_punctuation_in_text(self):
        detector = PinyinWakeWord(WakeWordConfig(wake_words="小月"))
        assert detector.check("你好，小月！你好吗？") is True

    def test_multiple_detectors_independent(self):
        d1 = PinyinWakeWord(WakeWordConfig(wake_words="小月"))
        d2 = PinyinWakeWord(WakeWordConfig(wake_words="小智"))
        assert d1.check("小月") is True
        assert d1.check("小智") is False
        assert d2.check("小智") is True
        assert d2.check("小月") is False

    def test_add_then_detect(self):
        detector = PinyinWakeWord(WakeWordConfig(wake_words="小月"))
        assert detector.check("小智") is False
        detector.add_wake_word("小智")
        assert detector.check("小智") is True

    def test_fuzzy_mode_with_high_threshold(self):
        detector = PinyinWakeWord(
            WakeWordConfig(
                wake_words="你好小月",
                match_mode="fuzzy",
                similarity_threshold=1.0,
            )
        )
        # Only exact pinyin match at threshold 1.0
        assert detector.check("你好小月") is True
        assert detector.check("你好大月") is False

    def test_partial_mode_callback_on_prefix(self):
        partial_events = []
        detector = PinyinWakeWord(
            WakeWordConfig(wake_words="小月小月", match_mode="partial")
        )
        detector.on_partial_match = lambda e: partial_events.append(e)
        detector.feed("小月")
        assert len(partial_events) == 1

    def test_all_punctuation_input(self):
        detector = PinyinWakeWord(WakeWordConfig(wake_words="小月"))
        events = detector.feed("，。！？")
        # After stripping punctuation, text is empty
        assert events == []
