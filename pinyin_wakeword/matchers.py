"""Pinyin-based wake word matching algorithms."""

import re
from functools import lru_cache

from pypinyin import lazy_pinyin, Style


# Punctuation pattern for stripping
_PUNCTUATION_RE = re.compile(r"[^\w\s]", re.UNICODE)

# Pinyin style mapping
_STYLE_MAP = {
    "normal": Style.NORMAL,
    "tone": Style.TONE,
    "tone_number": Style.TONE3,
}


def _get_pinyin_style(style_name):
    """Convert style name string to pypinyin Style enum."""
    return _STYLE_MAP.get(style_name, Style.NORMAL)


@lru_cache(maxsize=1024)
def _text_to_pinyin(text, style=Style.NORMAL):
    """Convert text to a tuple of pinyin syllables (cached).

    Args:
        text: Chinese text string.
        style: pypinyin Style enum value.

    Returns:
        Tuple of pinyin strings.
    """
    return tuple(lazy_pinyin(text, style=style))


def strip_punctuation(text):
    """Remove punctuation from text, keeping letters, digits, and whitespace.

    Args:
        text: Input text.

    Returns:
        Text with punctuation removed.
    """
    return _PUNCTUATION_RE.sub("", text)


def match_exact(text, wake_word, style=Style.NORMAL):
    """Sliding window exact pinyin match.

    Scans the input text with a window equal to the wake word length,
    comparing pinyin sequences at each position.

    Args:
        text: Input text to search.
        wake_word: Wake word to match against.
        style: pypinyin Style enum value.

    Returns:
        A list of (position, matched_text, confidence) tuples.
        Confidence is always 1.0 for exact matches.
    """
    if not text or not wake_word:
        return []

    target_pinyin = _text_to_pinyin(wake_word, style)
    word_len = len(wake_word)
    results = []

    if len(text) < word_len:
        return []

    for i in range(len(text) - word_len + 1):
        window = text[i : i + word_len]
        window_pinyin = _text_to_pinyin(window, style)
        if window_pinyin == target_pinyin:
            results.append((i, window, 1.0))

    return results


def match_fuzzy(text, wake_word, threshold=0.8, style=Style.NORMAL):
    """Sliding window fuzzy pinyin match.

    Compares pinyin sequences allowing partial mismatch. The similarity
    is the ratio of matching syllables to total syllables.

    Args:
        text: Input text to search.
        wake_word: Wake word to match against.
        threshold: Minimum similarity ratio (0.0 to 1.0).
        style: pypinyin Style enum value.

    Returns:
        A list of (position, matched_text, confidence) tuples.
    """
    if not text or not wake_word:
        return []

    target_pinyin = _text_to_pinyin(wake_word, style)
    word_len = len(wake_word)
    pinyin_len = len(target_pinyin)
    results = []

    if len(text) < word_len or pinyin_len == 0:
        return []

    for i in range(len(text) - word_len + 1):
        window = text[i : i + word_len]
        window_pinyin = _text_to_pinyin(window, style)

        if len(window_pinyin) != pinyin_len:
            continue

        matches = sum(1 for a, b in zip(window_pinyin, target_pinyin) if a == b)
        similarity = matches / pinyin_len

        if similarity >= threshold:
            results.append((i, window, similarity))

    return results


def match_partial(text, wake_word, style=Style.NORMAL):
    """Check if input text is a pinyin prefix of the wake word.

    Used for detecting incomplete utterances where the user has started
    saying the wake word but hasn't finished.

    Args:
        text: Input text to check.
        wake_word: Full wake word to match against.
        style: pypinyin Style enum value.

    Returns:
        A list of (position, matched_text, confidence) tuples.
        Confidence reflects the fraction of the wake word matched.
        Only returns results if text is shorter than wake word.
    """
    if not text or not wake_word:
        return []

    text_pinyin = _text_to_pinyin(text, style)
    target_pinyin = _text_to_pinyin(wake_word, style)

    if len(text_pinyin) >= len(target_pinyin):
        return []

    if len(text_pinyin) == 0:
        return []

    # Check if text pinyin is a prefix of target pinyin
    for i in range(len(text_pinyin)):
        if text_pinyin[i] != target_pinyin[i]:
            return []

    confidence = len(text_pinyin) / len(target_pinyin)
    return [(0, text, confidence)]
