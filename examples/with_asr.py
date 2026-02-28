"""Example: Wake word detection integrated with ASR pipeline.

This example simulates an ASR (Automatic Speech Recognition) pipeline
that feeds transcribed text to the wake word detector in real-time.
"""

from pinyin_wakeword import PinyinWakeWord, WakeWordConfig, WakeWordEventType


def simulate_asr_stream():
    """Simulate an ASR service producing text output.

    In a real application, this would come from an ASR service like
    FunASR, Alibaba Cloud ASR, or similar.
    """
    return [
        "今天",
        "今天天气",
        "今天天气怎么样",
        "小月",
        "小月小月",
        "小月小月你好",
        "请问",
        "请问明天",
        "请问明天会下雨吗",
    ]


def example_event_driven():
    """Event-driven ASR pipeline using iter_events()."""
    print("=== Event-Driven ASR Pipeline ===")
    detector = PinyinWakeWord(WakeWordConfig(wake_words="小月小月"))

    listening = False
    for event in detector.iter_events(simulate_asr_stream()):
        if event.type == WakeWordEventType.DETECTED:
            print("  [WAKE] Detected: {!r} at position {}".format(
                event.matched_text, event.position
            ))
            listening = True
        elif event.type == WakeWordEventType.NOT_DETECTED:
            if listening:
                print("  [ASR]  Processing: {!r}".format(event.text))
    print()


def example_callback_asr():
    """Callback-based ASR pipeline."""
    print("=== Callback ASR Pipeline ===")

    state = {"listening": False, "query": None}

    def on_wake(event):
        state["listening"] = True
        state["query"] = None
        print("  [WAKE] Wake word detected: {!r}".format(event.matched_text))

    def on_miss(event):
        if state["listening"]:
            state["query"] = event.text
            print("  [ASR]  User said: {!r}".format(event.text))
        else:
            print("  [IDLE] Ignoring: {!r}".format(event.text))

    detector = PinyinWakeWord(WakeWordConfig(wake_words="小月小月"))
    detector.on_detected = on_wake
    detector.on_not_detected = on_miss

    for text in simulate_asr_stream():
        detector.feed(text)
    print()


def example_short_mode_asr():
    """ASR pipeline with short mode toggling.

    Simulates the digital-human scenario:
    - When the system is idle, require full wake word ("小月小月")
    - When the system is speaking, accept shortened wake word ("小月")
    """
    print("=== Short Mode ASR Pipeline ===")
    detector = PinyinWakeWord(
        WakeWordConfig(wake_words="小月小月", short_mode_length=2)
    )

    # Phase 1: System idle, require full wake word
    print("  Phase 1: System idle (full wake word required)")
    print("    '小月' -> {}".format(detector.check("小月")))
    print("    '小月小月' -> {}".format(detector.check("小月小月")))

    # Phase 2: System speaking, accept shortened wake word
    detector.short_mode = True
    print("  Phase 2: System speaking (short mode active)")
    print("    '小月' -> {}".format(detector.check("你好小月")))

    # Phase 3: System done speaking, back to full wake word
    detector.short_mode = False
    print("  Phase 3: System idle again")
    print("    '小月' -> {}".format(detector.check("小月")))
    print()


if __name__ == "__main__":
    example_event_driven()
    example_callback_asr()
    example_short_mode_asr()
