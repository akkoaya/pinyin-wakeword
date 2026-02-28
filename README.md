# pinyin-wakeword

Pinyin-based wake word detection for Chinese speech recognition pipelines.

Uses [pypinyin](https://github.com/mozillazg/python-pinyin) to convert Chinese text to pinyin syllables, enabling **homophone-tolerant** wake word matching. For example, configuring the wake word as "小月" will also match "晓悦", "小悦", etc.

## Features

- **Homophone matching** — Detects wake words by pinyin, not characters
- **Sliding window** — Finds wake words anywhere in the input text
- **Short mode** — Shortened matching for noisy/speaking contexts
- **Multiple wake words** — Monitor several wake words simultaneously
- **Three match modes** — Exact, fuzzy (similarity threshold), partial (prefix)
- **Event-driven API** — `feed()`, `check()`, `iter_events()`, and callbacks
- **Lightweight** — Only depends on `pypinyin`

## Installation

```bash
pip install pinyin-wakeword
```

Or install from source:

```bash
git clone https://github.com/akkoaya/pinyin-wakeword.git
cd pinyin-wakeword
pip install -e .
```

## Quick Start

```python
from pinyin_wakeword import PinyinWakeWord, WakeWordConfig, WakeWordEventType

detector = PinyinWakeWord(WakeWordConfig(wake_words="小月小月"))

# Simple boolean check
if detector.check("你好小月小月"):
    print("Wake word detected!")

# Event-based
events = detector.feed("你好小月小月请问天气")
for event in events:
    if event.type == WakeWordEventType.DETECTED:
        print(f"Detected: {event.matched_text} at position {event.position}")

# Callback style
detector.on_detected = lambda e: print(f"Woke up: {e.matched_text}")
detector.feed("小月小月你好")

# Iterator over ASR stream
for event in detector.iter_events(asr_text_stream):
    if event.type == WakeWordEventType.DETECTED:
        start_listening()
```

## Configuration

```python
config = WakeWordConfig(
    wake_words="小月小月",       # Wake word(s), string or list
    short_mode_length=2,         # Characters used in short mode
    match_mode="exact",          # "exact", "fuzzy", or "partial"
    min_text_length=1,           # Minimum input text length
    similarity_threshold=0.8,    # Fuzzy mode threshold (0.0-1.0)
    strip_punctuation=True,      # Remove punctuation before matching
    pinyin_style="normal",       # "normal", "tone", or "tone_number"
)
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `wake_words` | `""` | Wake word string or list of strings |
| `short_mode_length` | `2` | Number of characters for short mode |
| `match_mode` | `"exact"` | Matching strategy |
| `min_text_length` | `1` | Minimum text length to process |
| `similarity_threshold` | `0.8` | Fuzzy mode similarity threshold |
| `strip_punctuation` | `True` | Strip punctuation before matching |
| `pinyin_style` | `"normal"` | Pinyin romanization style |

## Match Modes

### Exact (default)

Pinyin sequences must match exactly. "小月" matches "晓悦" (same pinyin) but not "小日".

```python
detector = PinyinWakeWord(WakeWordConfig(wake_words="小月", match_mode="exact"))
```

### Fuzzy

Allows partial syllable mismatch based on similarity threshold.

```python
detector = PinyinWakeWord(WakeWordConfig(
    wake_words="小月小月",
    match_mode="fuzzy",
    similarity_threshold=0.7,  # 3/4 syllables = 75% >= 70%
))
detector.check("小月小日")  # True (75% match)
```

### Partial

Detects incomplete wake word utterances (prefix matching).

```python
detector = PinyinWakeWord(WakeWordConfig(
    wake_words="小月小月",
    match_mode="partial",
))
events = detector.feed("小月")  # Returns PARTIAL_MATCH event
```

## Short Mode

Reduces the required wake word to the first N characters, useful when the system is already speaking or playing audio:

```python
detector = PinyinWakeWord(WakeWordConfig(
    wake_words="小月小月",
    short_mode_length=2,
))

detector.check("小月")        # False (need full "小月小月")
detector.short_mode = True
detector.check("小月")        # True (only first 2 chars required)
```

## Runtime Control

```python
# Add/remove wake words dynamically
detector.add_wake_word("你好小智")
detector.remove_wake_word("小月小月")

# Toggle short mode
detector.short_mode = True
detector.short_mode = False

# Reset state
detector.reset()
```

## Events

| Event Type | When | Key Fields |
|-----------|------|------------|
| `DETECTED` | Wake word found | `wake_word`, `matched_text`, `position`, `confidence`, `short_mode` |
| `PARTIAL_MATCH` | Prefix match (partial mode) | `matched_text` |
| `NOT_DETECTED` | No match found | `text` |

## Development

```bash
git clone https://github.com/akkoaya/pinyin-wakeword.git
cd pinyin-wakeword
pip install -e ".[dev]"
pytest -v
```

## License

[MIT](LICENSE)
