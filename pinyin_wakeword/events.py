"""Wake word event types and data."""

import enum


class WakeWordEventType(enum.Enum):
    """Types of events emitted by the wake word detector."""

    DETECTED = "detected"
    """Wake word detected in the input text."""

    PARTIAL_MATCH = "partial_match"
    """Input text is a prefix of a wake word (partial mode only)."""

    NOT_DETECTED = "not_detected"
    """No wake word found in the input text."""


class WakeWordEvent:
    """An event emitted by the wake word detector.

    Attributes:
        type: The event type.
        wake_word: The configured wake word that was matched (DETECTED only).
        matched_text: The substring in the input that matched (DETECTED/PARTIAL_MATCH).
        position: Start index of the match in the input text (DETECTED only).
        confidence: Match confidence from 0.0 to 1.0 (DETECTED only).
        short_mode: Whether short mode was active during detection (DETECTED only).
        text: The full input text (NOT_DETECTED only).
    """

    __slots__ = (
        "type",
        "wake_word",
        "matched_text",
        "position",
        "confidence",
        "short_mode",
        "text",
    )

    def __init__(
        self,
        event_type,
        wake_word=None,
        matched_text=None,
        position=None,
        confidence=None,
        short_mode=None,
        text=None,
    ):
        self.type = event_type
        self.wake_word = wake_word
        self.matched_text = matched_text
        self.position = position
        self.confidence = confidence
        self.short_mode = short_mode
        self.text = text

    def __repr__(self):
        if self.type == WakeWordEventType.DETECTED:
            return (
                "WakeWordEvent(DETECTED, wake_word={!r}, matched_text={!r}, "
                "position={}, confidence={:.2f}, short_mode={})".format(
                    self.wake_word,
                    self.matched_text,
                    self.position,
                    self.confidence if self.confidence is not None else 0.0,
                    self.short_mode,
                )
            )
        if self.type == WakeWordEventType.PARTIAL_MATCH:
            return "WakeWordEvent(PARTIAL_MATCH, matched_text={!r})".format(
                self.matched_text
            )
        return "WakeWordEvent(NOT_DETECTED, text={!r})".format(self.text)
