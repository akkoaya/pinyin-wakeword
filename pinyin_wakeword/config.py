"""Wake word detection configuration."""


class WakeWordConfig:
    """Configuration for pinyin-based wake word detection.

    Args:
        wake_words: Wake word string or list of strings.
            Example: "小月小月" or ["小月小月", "你好小智"].
        short_mode_length: Number of characters to use in short mode.
            When short_mode is enabled on the detector, only the first
            N characters of each wake word are matched. Default 2.
        match_mode: Matching strategy. One of:
            - "exact": Pinyin sequences must match exactly (default).
            - "fuzzy": Allow partial mismatch based on similarity_threshold.
            - "partial": Input is a prefix of the wake word pinyin.
        min_text_length: Minimum input text length to attempt matching.
            Texts shorter than this are skipped. Default 1.
        similarity_threshold: Minimum similarity ratio for fuzzy mode
            (0.0 to 1.0). Ignored in other modes. Default 0.8.
        strip_punctuation: Whether to remove punctuation before matching.
            Default True.
        pinyin_style: Pinyin romanization style. One of:
            - "normal": No tone marks or numbers (default).
            - "tone": With tone marks (e.g. "xiǎo").
            - "tone_number": With tone numbers (e.g. "xiao3").
    """

    __slots__ = (
        "wake_words",
        "short_mode_length",
        "match_mode",
        "min_text_length",
        "similarity_threshold",
        "strip_punctuation",
        "pinyin_style",
    )

    def __init__(
        self,
        wake_words="",
        short_mode_length=2,
        match_mode="exact",
        min_text_length=1,
        similarity_threshold=0.8,
        strip_punctuation=True,
        pinyin_style="normal",
    ):
        if isinstance(wake_words, str):
            self.wake_words = [wake_words] if wake_words else []
        else:
            self.wake_words = list(wake_words)
        self.short_mode_length = short_mode_length
        self.match_mode = match_mode
        self.min_text_length = min_text_length
        self.similarity_threshold = similarity_threshold
        self.strip_punctuation = strip_punctuation
        self.pinyin_style = pinyin_style

    def __repr__(self):
        fields = ", ".join(
            "{}={!r}".format(name, getattr(self, name)) for name in self.__slots__
        )
        return "WakeWordConfig({})".format(fields)
