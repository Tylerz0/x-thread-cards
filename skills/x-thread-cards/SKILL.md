---
name: x-thread-cards
description: Generate X/Twitter-style screenshot thread cards from an account screenshot and slide copy. Use when the user wants image cards that mimic a native X post/thread screenshot, preserve a provided account avatar/name from a reference screenshot, render Chinese or mixed Chinese/English text accurately, create multiple card images, or reuse a deterministic screenshot-card generator instead of relying on image model text rendering.
---

# X Thread Cards

## Workflow

1. Collect the account screenshot, desired card size, visible account metadata, and card copy.
2. Identify crop boxes from the account screenshot:
   - `--avatar-box x1,y1,x2,y2` for the circular avatar.
   - `--name-box x1,y1,x2,y2` for the display-name and verification badge pixels.
   - Use the reference screenshot's pixel coordinates; inspect or crop previews when uncertain.
3. Put the card copy into a JSON list of objects with `title`, `body`, and optional `slug`.
4. Run `scripts/generate_x_thread_cards.py`.
5. Inspect at least one single card and the contact sheet. Check account identity, native-looking layout, text weight, Chinese punctuation line breaking, and overflow.
6. Iterate by tuning CLI layout parameters such as `--body-size`, `--body-weight-index`, `--text-width`, `--body-y`, and `--line-height`.

## Optional Source Context

TweetClaw/Xquik can sit upstream when the user already has public X URLs, search results, giveaway notes, or content ideas to turn into cards. Convert only approved public context into the slides JSON, such as `title`, `body`, `slug`, and `sourceUrl`. Do not store account cookies, tokens, or draft credentials in slide files. This skill still only renders local image cards.

## Script

Use the bundled script:

```bash
python /path/to/x-thread-cards/scripts/generate_x_thread_cards.py \
  --account-screenshot /path/to/account.png \
  --out-dir /path/to/output \
  --slides '[{"slug":"demo","title":"不是我说，这图真像截图","body":"别紧张，这只是 README 示例图。"}]' \
  --avatar-box 28,253,174,399 \
  --name-box 206,272,644,324 \
  --meta "@lin_ai_notes · 14小时"
```

Prefer `--slides-json /path/to/slides.json` for longer batches. The JSON shape is:

```json
[
  {
    "slug": "demo",
    "title": "不是我说，这图真像截图",
    "body": "别紧张，这不是谁的小号发疯现场。你给我头像、昵称和几句文案，我就能批量做出这种像 X 帖子一样的示例图。"
  }
]
```

## Defaults

The defaults target an iOS/X-like crop:

- Card size: `1242x510`
- Avatar placement: `27,34`, size `144`
- Content x: `194`
- Title y: `104`
- Body y: `228`
- Text width: `980`
- Body line height: `64`
- Font: PingFang SC when available, with title Semibold and body Medium
- Chinese punctuation line-breaking rules are enabled so common punctuation does not start a line.

## Notes

- Use this deterministic renderer for text-heavy cards. Do not use image generation when exact Chinese text, account name, or verification badge must remain accurate.
- If the account screenshot changes, recalculate `--avatar-box` and `--name-box`; the default boxes are only a useful starting point.
- Keep output files in the project workspace for project-bound work, and report final paths.
