<p align="center">
  <h1 align="center">pinyin-wakeword</h1>
  <p align="center">基于拼音的中文唤醒词检测库，适用于语音识别（ASR）管线</p>
</p>

<p align="center">
  <a href="https://pypi.org/project/pinyin-wakeword/"><img src="https://img.shields.io/pypi/v/pinyin-wakeword?color=blue" alt="PyPI version"></a>
  <a href="https://pypi.org/project/pinyin-wakeword/"><img src="https://img.shields.io/pypi/pyversions/pinyin-wakeword" alt="Python versions"></a>
  <a href="https://github.com/akkoaya/pinyin-wakeword/blob/main/LICENSE"><img src="https://img.shields.io/github/license/akkoaya/pinyin-wakeword" alt="License"></a>
  <a href="https://github.com/akkoaya/pinyin-wakeword/issues"><img src="https://img.shields.io/github/issues/akkoaya/pinyin-wakeword" alt="Issues"></a>
</p>

<p align="center">
  简体中文 | <a href="./README.md">English</a>
</p>

---

使用 [pypinyin](https://github.com/mozillazg/python-pinyin) 将中文文本转换为拼音音节，实现**同音字容错**的唤醒词匹配。例如，配置唤醒词为"小月"，同样可以匹配"晓悦"、"小悦"等同音词。

## 目录

- [特性](#特性)
- [安装](#安装)
- [快速开始](#快速开始)
- [配置参数](#配置参数)
- [匹配模式](#匹配模式)
- [短模式](#短模式)
- [运行时控制](#运行时控制)
- [事件类型](#事件类型)
- [示例](#示例)
- [开发](#开发)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

## 特性

- **同音字匹配** — 基于拼音检测，不依赖字符精确匹配
- **滑动窗口** — 在输入文本的任意位置查找唤醒词
- **短模式** — 在嘈杂/播报环境下缩短匹配长度，提高命中率
- **多唤醒词** — 同时监测多个唤醒词
- **三种匹配模式** — 精确匹配、模糊匹配（相似度阈值）、前缀匹配
- **事件驱动 API** — `feed()`、`check()`、`iter_events()` 及回调函数
- **轻量级** — 仅依赖 `pypinyin`

## 安装

```bash
pip install pinyin-wakeword
```

或从源码安装：

```bash
git clone https://github.com/akkoaya/pinyin-wakeword.git
cd pinyin-wakeword
pip install -e .
```

## 快速开始

```python
from pinyin_wakeword import PinyinWakeWord, WakeWordConfig, WakeWordEventType

detector = PinyinWakeWord(WakeWordConfig(wake_words="小月小月"))

# 简单布尔检查
if detector.check("你好小月小月"):
    print("检测到唤醒词！")

# 事件模式
events = detector.feed("你好小月小月请问天气")
for event in events:
    if event.type == WakeWordEventType.DETECTED:
        print(f"检测到: {event.matched_text}，位置 {event.position}")

# 回调模式
detector.on_detected = lambda e: print(f"唤醒: {e.matched_text}")
detector.feed("小月小月你好")

# 迭代器模式（配合 ASR 流）
for event in detector.iter_events(asr_text_stream):
    if event.type == WakeWordEventType.DETECTED:
        start_listening()
```

## 配置参数

```python
config = WakeWordConfig(
    wake_words="小月小月",       # 唤醒词，字符串或列表
    short_mode_length=2,         # 短模式匹配字符数
    match_mode="exact",          # "exact"（精确）、"fuzzy"（模糊）、"partial"（前缀）
    min_text_length=1,           # 最短输入文本长度
    similarity_threshold=0.8,    # 模糊模式相似度阈值 (0.0-1.0)
    strip_punctuation=True,      # 匹配前去除标点
    pinyin_style="normal",       # "normal"（无声调）、"tone"（声调）、"tone_number"（数字声调）
)
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `wake_words` | `""` | 唤醒词，字符串或字符串列表 |
| `short_mode_length` | `2` | 短模式使用的字符数 |
| `match_mode` | `"exact"` | 匹配策略 |
| `min_text_length` | `1` | 最短文本长度 |
| `similarity_threshold` | `0.8` | 模糊模式相似度阈值 |
| `strip_punctuation` | `True` | 匹配前去除标点符号 |
| `pinyin_style` | `"normal"` | 拼音风格 |

## 匹配模式

### 精确匹配（默认）

拼音序列必须完全一致。"小月"可匹配"晓悦"（同音），但不匹配"小日"。

```python
detector = PinyinWakeWord(WakeWordConfig(wake_words="小月", match_mode="exact"))
```

### 模糊匹配

允许部分音节不匹配，基于相似度阈值判断。

```python
detector = PinyinWakeWord(WakeWordConfig(
    wake_words="小月小月",
    match_mode="fuzzy",
    similarity_threshold=0.7,  # 3/4 音节 = 75% >= 70%
))
detector.check("小月小日")  # True（75% 匹配）
```

### 前缀匹配

检测不完整的唤醒词（前缀匹配），适用于流式 ASR 场景。

```python
detector = PinyinWakeWord(WakeWordConfig(
    wake_words="小月小月",
    match_mode="partial",
))
events = detector.feed("小月")  # 返回 PARTIAL_MATCH 事件
```

## 短模式

将唤醒词缩短为前 N 个字符。适用于系统正在播报或播放音乐时，降低唤醒门槛：

```python
detector = PinyinWakeWord(WakeWordConfig(
    wake_words="小月小月",
    short_mode_length=2,
))

detector.check("小月")        # False（需要完整的"小月小月"）
detector.short_mode = True
detector.check("小月")        # True（只需前 2 个字符）
```

## 运行时控制

```python
# 动态添加/移除唤醒词
detector.add_wake_word("你好小智")
detector.remove_wake_word("小月小月")

# 切换短模式
detector.short_mode = True
detector.short_mode = False

# 重置状态
detector.reset()
```

## 事件类型

| 事件类型 | 触发条件 | 关键字段 |
|----------|----------|----------|
| `DETECTED` | 检测到唤醒词 | `wake_word`, `matched_text`, `position`, `confidence`, `short_mode` |
| `PARTIAL_MATCH` | 前缀匹配命中 | `matched_text` |
| `NOT_DETECTED` | 未检测到 | `text` |

## 示例

查看 [`examples/`](./examples) 目录获取完整示例：

- [`basic_detection.py`](./examples/basic_detection.py) — 基本唤醒词检测
- [`with_asr.py`](./examples/with_asr.py) — 与 ASR 流式集成

## 开发

```bash
git clone https://github.com/akkoaya/pinyin-wakeword.git
cd pinyin-wakeword
pip install -e ".[dev]"
pytest -v
```

## 贡献指南

欢迎贡献！请按以下步骤操作：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/your-feature`)
3. 提交更改 (`git commit -m 'Add some feature'`)
4. 推送分支 (`git push origin feature/your-feature`)
5. 发起 Pull Request

请确保同步更新相关测试。

## 许可证

本项目基于 MIT 许可证开源，详见 [LICENSE](LICENSE) 文件。

## 致谢

- [pypinyin](https://github.com/mozillazg/python-pinyin) — 中文转拼音库
