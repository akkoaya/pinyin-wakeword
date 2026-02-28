"""pinyin-wakeword: Pinyin-based wake word detection for Chinese speech recognition pipelines."""

from .config import WakeWordConfig
from .core import PinyinWakeWord
from .events import WakeWordEvent, WakeWordEventType

__version__ = "0.1.0"
__all__ = ["PinyinWakeWord", "WakeWordConfig", "WakeWordEvent", "WakeWordEventType"]
