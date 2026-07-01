# X Thread Cards

[中文说明](README.md)

A Codex / Claude Code skill that turns ordinary copy into X/Twitter-style screenshot cards.

![X Thread Cards preview](docs/preview.png)

Turn ordinary post copy into a batch of X/Twitter-style screenshot cards.

Give it an account screenshot, a list of titles and captions, and an output folder. It preserves the avatar/name area from the screenshot, renders the text locally, and exports one PNG card per item plus a contact sheet preview.

This is useful when you want the look of a social screenshot without asking an image model to redraw exact Chinese text, account names, punctuation, or verification badges.

## Why Use It

Image models often break the exact parts that matter in screenshot-style content:

- Chinese text gets distorted.
- Punctuation moves to awkward places.
- Account names drift.
- Verification badges are redrawn incorrectly.

This skill renders the layout locally with real fonts, so it is better for content cards that need accurate text.

## Use Cases

- Turn a long post or thread into multiple image cards.
- Make tutorial, prompt, or case-study cards for Xiaohongshu, newsletters, courses, or social posts.
- Keep the same account identity across a batch of X-style images.
- Generate precise Chinese or mixed Chinese/English text without image-model text artifacts.

## What It Does

- Generates one PNG card per slide.
- Preserves the account avatar and display-name area from a provided screenshot.
- Renders Chinese and mixed Chinese/English text deterministically.
- Applies basic Chinese line-breaking rules so punctuation such as `，` `、` `。` does not start a line.
- Creates a `contact_sheet.png` preview for quick review.
- Uses system fonts such as PingFang SC on macOS when available.

## Repository Layout

```text
skills/x-thread-cards/
├── SKILL.md
├── agents/
│   └── openai.yaml
└── scripts/
    └── generate_x_thread_cards.py
```

## Install

The easiest way is to open Codex or Claude Code and say:

```text
Please install this skill: https://github.com/Tylerz0/x-thread-cards
```

It should install `skills/x-thread-cards` from this repository into your local Codex skills directory.

For manual installation, copy the skill folder:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R skills/x-thread-cards "${CODEX_HOME:-$HOME/.codex}/skills/x-thread-cards"
```

Install the script dependency:

```bash
python3 -m pip install pillow
```

After installation, invoke it in Codex with:

```text
Use $x-thread-cards to generate X-style screenshot cards from an account screenshot and slide copy.
```

## CLI Usage

The bundled renderer can also be run directly:

```bash
python skills/x-thread-cards/scripts/generate_x_thread_cards.py \
  --account-screenshot /path/to/account-screenshot.png \
  --out-dir /path/to/output \
  --slides-json examples/slides.json \
  --avatar-box 28,253,174,399 \
  --name-box 206,272,644,324 \
  --meta "@lin_ai_notes · 14小时"
```

`--avatar-box` and `--name-box` are pixel crop boxes from the account screenshot in `x1,y1,x2,y2` format.

See [examples/slides.json](examples/slides.json) for sample input and [examples/output/demo.png](examples/output/demo.png) for sample output.

## Slides JSON

Use a JSON array. Each item needs a `title` and `body`; `slug` is optional and is used in the output filename.

```json
[
  {
    "slug": "demo",
    "title": "不是我说，这图真像截图",
    "body": "别紧张，这不是谁的小号发疯现场。你给我头像、昵称和几句文案，我就能批量做出这种像 X 帖子一样的示例图。"
  }
]
```

## Useful Options

```bash
--width 1242
--height 510
--title-size 43
--body-size 45
--meta-size 36
--title-weight-index 11
--body-weight-index 7
--content-x 194
--title-y 104
--body-y 228
--text-width 980
--line-height 64
--no-quote-body
--no-number-titles
```

The defaults are tuned for a cropped iOS/X-style screenshot card. If your source screenshot has a different scale, first adjust `--avatar-box`, `--name-box`, and `--meta`, then tune layout values only if the generated card looks crowded.

## Validate the Skill

If you have the Codex system `skill-creator` skill installed, validate the package with:

```bash
python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/x-thread-cards
```

Expected output:

```text
Skill is valid!
```

## Notes

- This skill intentionally uses deterministic rendering instead of image generation, because image models often distort exact Chinese text and account metadata.
- The default font path targets macOS. The script falls back to other bundled macOS CJK fonts when PingFang is unavailable. On other platforms, pass `--font /path/to/font.ttc`.
- The generated screenshots are visual approximations for content production workflows; they are not affiliated with X/Twitter.
