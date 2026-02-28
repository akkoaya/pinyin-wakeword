"""Basic wake word detection example.

Demonstrates the three main ways to use pinyin-wakeword:
1. feed() - returns event list
2. check() - returns boolean
3. Callback style
"""

from pinyin_wakeword import PinyinWakeWord, WakeWordConfig, WakeWordEventType


def example_feed():
    """Using feed() to get event list."""
    print("=== feed() Example ===")
    detector = PinyinWakeWord(WakeWordConfig(wake_words="小月小月"))

    texts = ["你好世界", "请问小月小月你好吗", "今天天气怎么样"]
    for text in texts:
        events = detector.feed(text)
        for event in events:
            if event.type == WakeWordEventType.DETECTED:
                print(
                    "  DETECTED: wake_word={!r}, matched={!r}, pos={}".format(
                        event.wake_word, event.matched_text, event.position
                    )
                )
            elif event.type == WakeWordEventType.NOT_DETECTED:
                print("  NOT_DETECTED: {!r}".format(event.text))
    print()


def example_check():
    """Using check() for simple boolean detection."""
    print("=== check() Example ===")
    detector = PinyinWakeWord(WakeWordConfig(wake_words="小月"))

    test_cases = ["你好小月", "晓悦你好", "你好世界"]
    for text in test_cases:
        result = detector.check(text)
        print("  {!r} -> {}".format(text, result))
    print()


def example_callback():
    """Using callback style."""
    print("=== Callback Example ===")
    detector = PinyinWakeWord(WakeWordConfig(wake_words="小智"))
    detector.on_detected = lambda e: print(
        "  Detected: {!r} (confidence={:.0%})".format(e.matched_text, e.confidence)
    )
    detector.on_not_detected = lambda e: print("  Missed: {!r}".format(e.text))

    for text in ["小智你好", "今天天气", "小智帮我查一下"]:
        detector.feed(text)
    print()


def example_short_mode():
    """Using short mode for interrupted detection."""
    print("=== Short Mode Example ===")
    detector = PinyinWakeWord(
        WakeWordConfig(wake_words="小月小月", short_mode_length=2)
    )

    print("  Normal mode:")
    print("    '小月你好' -> {}".format(detector.check("小月你好")))

    detector.short_mode = True
    print("  Short mode (2 chars):")
    print("    '小月你好' -> {}".format(detector.check("小月你好")))
    print()


def example_homophone():
    """Demonstrating homophone matching."""
    print("=== Homophone Example ===")
    detector = PinyinWakeWord(WakeWordConfig(wake_words="小月"))

    homophones = ["小月", "晓悦", "小悦", "笑月"]
    for text in homophones:
        result = detector.check(text)
        print("  {!r} -> {} (same pinyin as '小月')".format(text, result))
    print()


def example_multiple_wake_words():
    """Using multiple wake words."""
    print("=== Multiple Wake Words Example ===")
    detector = PinyinWakeWord(
        WakeWordConfig(wake_words=["小月", "小智", "你好"])
    )

    texts = ["小月你好吗", "小智帮我", "你好世界", "再见"]
    for text in texts:
        events = detector.feed(text)
        for event in events:
            if event.type == WakeWordEventType.DETECTED:
                print(
                    "  {!r} -> DETECTED (wake_word={!r})".format(
                        text, event.wake_word
                    )
                )
            elif event.type == WakeWordEventType.NOT_DETECTED:
                print("  {!r} -> NOT_DETECTED".format(text))
    print()


def example_fuzzy_mode():
    """Using fuzzy matching mode."""
    print("=== Fuzzy Mode Example ===")
    detector = PinyinWakeWord(
        WakeWordConfig(
            wake_words="小月小月",
            match_mode="fuzzy",
            similarity_threshold=0.7,
        )
    )

    texts = ["小月小月", "小月小日", "大风大雨"]
    for text in texts:
        events = detector.feed(text)
        for event in events:
            if event.type == WakeWordEventType.DETECTED:
                print(
                    "  {!r} -> DETECTED (confidence={:.0%})".format(
                        text, event.confidence
                    )
                )
            elif event.type == WakeWordEventType.NOT_DETECTED:
                print("  {!r} -> NOT_DETECTED".format(text))
    print()


if __name__ == "__main__":
    example_feed()
    example_check()
    example_callback()
    example_short_mode()
    example_homophone()
    example_multiple_wake_words()
    example_fuzzy_mode()
