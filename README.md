<p align="center">
  <h1 align="center">pinyin-wakeword</h1>
  <p align="center">Pinyin-based wake word detection for Chinese speech recognition pipelines</p>
</p>

<p align="center">
  <a href="https://pypi.org/project/pinyin-wakeword/"><img src="https://img.shields.io/pypi/v/pinyin-wakeword?color=blue" alt="PyPI version"></a>
  <a href="https://pypi.org/project/pinyin-wakeword/"><img src="https://img.shields.io/pypi/pyversions/pinyin-wakeword" alt="Python versions"></a>
  <a href="https://github.com/akkoaya/pinyin-wakeword/blob/main/LICENSE"><img src="https://img.shields.io/github/license/akkoaya/pinyin-wakeword" alt="License"></a>
  <a href="https://github.com/akkoaya/pinyin-wakeword/issues"><img src="https://img.shields.io/github/issues/akkoaya/pinyin-wakeword" alt="Issues"></a>
</p>

<p align="center">
  <a href="./README_CN.md">简体中文</a> | English
</p>

---

Uses [pypinyin](https://github.com/mozillazg/python-pinyin) to convert Chinese text to pinyin syllables, enabling **homophone-tolerant** wake word matching. For example, configuring the wake word as "小月" will also match "晓悦", "小悦", etc.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Match Modes](#match-modes)
- [Short Mode](#short-mode)
- [Runtime Control](#runtime-control)
- [Events](#events)
- [Examples](#examples)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

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

## Examples

See the [`examples/`](./examples) directory for complete usage examples:

- [`basic_detection.py`](./examples/basic_detection.py) — Basic wake word detection
- [`with_asr.py`](./examples/with_asr.py) — Integration with ASR streaming

## Development

```bash
git clone https://github.com/akkoaya/pinyin-wakeword.git
cd pinyin-wakeword
pip install -e ".[dev]"
pytest -v
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

Please make sure to update tests as appropriate.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [pypinyin](https://github.com/mozillazg/python-pinyin) — Chinese characters to pinyin conversion
