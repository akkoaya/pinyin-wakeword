"""Pinyin-based wake word detection core."""

from .config import WakeWordConfig
from .events import WakeWordEvent, WakeWordEventType
from .matchers import (
    _get_pinyin_style,
    match_exact,
    match_fuzzy,
    match_partial,
    strip_punctuation,
)


class PinyinWakeWord:
    """Pinyin-based wake word detector.

    Processes text input (typically from ASR) and detects configured
    wake words using pinyin comparison, allowing homophone matching.

    Usage::

        detector = PinyinWakeWord(WakeWordConfig(wake_words="小月小月"))

        # 1. feed() returns event list
        events = detector.feed("你好小月小月")
        for event in events:
            if event.type == WakeWordEventType.DETECTED:
                print("Wake word detected:", event.matched_text)

        # 2. Simple boolean check
        if detector.check("小月小月"):
            print("Detected!")

        # 3. Iterator over text stream
        for event in detector.iter_events(asr_stream):
            handle(event)

    Callback style::

        detector = PinyinWakeWord(WakeWordConfig(wake_words="小月小月"))
        detector.on_detected = lambda e: print("Detected:", e.matched_text)
        detector.on_not_detected = lambda e: print("Not detected")
        detector.feed("你好小月小月")
    """

    def __init__(self, config=None):
        """Initialize the wake word detector.

        Args:
            config: A WakeWordConfig instance. Uses defaults if None.
        """
        if config is None:
            config = WakeWordConfig()
        self._config = config
        self._short_mode = False
        self._pinyin_style = _get_pinyin_style(config.pinyin_style)

        # Callbacks (optional)
        self.on_detected = None  # callable(event: WakeWordEvent)
        self.on_partial_match = None  # callable(event: WakeWordEvent)
        self.on_not_detected = None  # callable(event: WakeWordEvent)

    @property
    def short_mode(self):
        """Whether short mode is active.

        In short mode, only the first N characters of each wake word
        are used for matching, where N is config.short_mode_length.
        This increases hit rate in noisy environments.
        """
        return self._short_mode

    @short_mode.setter
    def short_mode(self, value):
        self._short_mode = bool(value)

    @property
    def wake_words(self):
        """Current list of wake words."""
        return list(self._config.wake_words)

    def add_wake_word(self, word):
        """Add a wake word to the detection list.

        Args:
            word: Wake word string to add.
        """
        if word and word not in self._config.wake_words:
            self._config.wake_words.append(word)

    def remove_wake_word(self, word):
        """Remove a wake word from the detection list.

        Args:
            word: Wake word string to remove.
        """
        if word in self._config.wake_words:
            self._config.wake_words.remove(word)

    def reset(self):
        """Reset detector state. Clears short mode."""
        self._short_mode = False

    def check(self, text):
        """Check if text contains any wake word.

        Convenience method that returns True/False without event details.

        Args:
            text: Input text to check.

        Returns:
            True if any wake word was detected, False otherwise.
        """
        events = self.feed(text)
        return any(e.type == WakeWordEventType.DETECTED for e in events)

    def feed(self, text):
        """Process input text and return a list of wake word events.

        Args:
            text: Input text (typically from ASR output).

        Returns:
            List of WakeWordEvent objects.
        """
        if not self._config.wake_words:
            return []

        if not text or len(text) < self._config.min_text_length:
            return []

        # Preprocess
        processed = text
        if self._config.strip_punctuation:
            processed = strip_punctuation(processed)

        if not processed:
            return []

        events = []
        detected = False

        for wake_word in self._config.wake_words:
            effective_word = wake_word
            if self._short_mode:
                effective_word = wake_word[: self._config.short_mode_length]

            matches = self._match(processed, effective_word)

            for position, matched_text, confidence in matches:
                detected = True
                event = WakeWordEvent(
                    event_type=WakeWordEventType.DETECTED,
                    wake_word=wake_word,
                    matched_text=matched_text,
                    position=position,
                    confidence=confidence,
                    short_mode=self._short_mode,
                )
                events.append(event)
                if self.on_detected is not None:
                    self.on_detected(event)

            # Partial match check (only in partial mode, when no exact match)
            if (
                not matches
                and self._config.match_mode == "partial"
            ):
                partial_results = match_partial(
                    processed, effective_word, style=self._pinyin_style
                )
                for position, matched_text, confidence in partial_results:
                    event = WakeWordEvent(
                        event_type=WakeWordEventType.PARTIAL_MATCH,
                        matched_text=matched_text,
                    )
                    events.append(event)
                    if self.on_partial_match is not None:
                        self.on_partial_match(event)

        if not detected:
            event = WakeWordEvent(
                event_type=WakeWordEventType.NOT_DETECTED,
                text=text,
            )
            events.append(event)
            if self.on_not_detected is not None:
                self.on_not_detected(event)

        return events

    def iter_events(self, text_stream):
        """Iterate over wake word events from a text stream.

        Args:
            text_stream: Iterable yielding text strings (e.g. ASR output).

        Yields:
            WakeWordEvent objects.
        """
        for text in text_stream:
            for event in self.feed(text):
                yield event

    def _match(self, text, wake_word):
        """Run the configured matching strategy.

        Args:
            text: Preprocessed input text.
            wake_word: Effective wake word (may be shortened).

        Returns:
            List of (position, matched_text, confidence) tuples.
        """
        mode = self._config.match_mode

        if mode == "fuzzy":
            return match_fuzzy(
                text,
                wake_word,
                threshold=self._config.similarity_threshold,
                style=self._pinyin_style,
            )
        elif mode == "partial":
            # In partial mode, first try exact match, then fall back
            # to prefix check (handled in feed())
            return match_exact(text, wake_word, style=self._pinyin_style)
        else:
            # Default: exact
            return match_exact(text, wake_word, style=self._pinyin_style)
