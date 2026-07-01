# X Thread Cards

[English](README.en.md)

![X Thread Cards 预览](docs/preview.png)

一句话：把一段普通文案，批量做成「看起来像 X/Twitter 帖子截图」的图片。

你给它三样东西：

- 一张账号截图，用来提取头像、昵称和认证标识。
- 一组标题和正文。
- 一个输出目录。

它会自动生成一组 X 风格截图卡片，并附带一张总览图，方便你直接挑选、发布或继续微调。

## 适合什么场景

这个 skill 适合做小红书、朋友圈、公众号、课程资料里的「社交媒体截图感」图文内容。

比如：

- 把一条长推文拆成多张截图卡片。
- 把提示词、教程、案例拆解做成系列图。
- 做一组像「真实 X 帖子」的内容预览图。
- 保持同一个账号头像和昵称，批量生成多张同风格图片。
- 避免 AI 画图模型把中文、账号名、标点和认证标识画错。

它不是用来真的发 X 帖子的，也不是 X 官方工具。它只是帮你快速做出「X 截图风格」的内容图片。

## 功能

- 为每一段文案生成一张 PNG 卡片。
- 从账号截图中裁出头像、昵称和认证标识，保证账号区域不像重新画的。
- 正文用本地字体渲染，所以中文不会被 AI 画歪、画糊或改字。
- 自动处理中文换行，避免 `，` `、` `。` 这类标点出现在行首。
- 自动生成 `contact_sheet.png` 总览图，一眼看完整组效果。
- 支持调整字号、行高、正文宽度、是否自动编号、是否加引号。

## 使用效果

输入一组这样的文案：

```json
[
  {
    "title": "不是我说，这图真像截图",
    "body": "别紧张，这不是谁的小号发疯现场。你给我头像、昵称和几句文案，我就能批量做出这种像 X 帖子一样的示例图。"
  }
]
```

会输出：

```text
01_demo.png
contact_sheet.png
```

## 目录结构

```text
skills/x-thread-cards/
├── SKILL.md
├── agents/
│   └── openai.yaml
└── scripts/
    └── generate_x_thread_cards.py
```

## 安装

最简单的方式：打开 Codex 或 Claude Code，直接说：

```text
请帮我安装这个 skill：[你的 GitHub 链接]
```

它会把这个仓库里的 `skills/x-thread-cards` 安装到本地 Codex skills 目录。

如果你想手动安装，也可以复制 skill 文件夹：

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R skills/x-thread-cards "${CODEX_HOME:-$HOME/.codex}/skills/x-thread-cards"
```

脚本依赖是 Pillow：

```bash
python3 -m pip install pillow
```

安装后，可以在 Codex 里这样调用：

```text
Use $x-thread-cards to turn this account screenshot and these captions into X-style image cards.
```

## 命令行用法

如果你不想通过 Codex，也可以直接运行脚本：

```bash
python skills/x-thread-cards/scripts/generate_x_thread_cards.py \
  --account-screenshot /path/to/account-screenshot.png \
  --out-dir /path/to/output \
  --slides-json /path/to/slides.json \
  --avatar-box 28,253,174,399 \
  --name-box 206,272,644,324 \
  --meta "@lin_ai_notes · 14小时"
```

这里最重要的是两个裁剪框：

- `--avatar-box`：头像在账号截图里的位置。
- `--name-box`：昵称和认证标识在账号截图里的位置。

格式都是 `x1,y1,x2,y2`。如果换了一张账号截图，通常只需要重新调这两个值。

## 文案 JSON

文案用 JSON 数组。每一项就是一张图片。

每一项都需要：

- `title`：图片顶部标题。
- `body`：正文内容。
- `slug`：可选，用于输出文件名。

```json
[
  {
    "slug": "demo",
    "title": "不是我说，这图真像截图",
    "body": "别紧张，这不是谁的小号发疯现场。你给我头像、昵称和几句文案，我就能批量做出这种像 X 帖子一样的示例图。"
  }
]
```

## 常用参数

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

默认参数已经按 iOS/X 风格截图卡片调过。一般只需要改：

- `--avatar-box`
- `--name-box`
- `--meta`
- `--slides-json`
- `--out-dir`

如果正文太挤，再调 `--body-size`、`--text-width` 和 `--line-height`。

## 校验 Skill

如果本地安装了 Codex 系统 skill `skill-creator`，可以运行：

```bash
python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/x-thread-cards
```

期望输出：

```text
Skill is valid!
```

## 说明

- 这个 skill 有意采用确定性的本地渲染，而不是图像生成模型，因为图像模型很容易扭曲中文、账号名称和细节标识。
- 默认字体路径面向 macOS。脚本会在 PingFang 不可用时尝试其他 macOS CJK 字体；其他系统可以通过 `--font /path/to/font.ttc` 指定字体。
- 生成图片是面向内容生产流程的视觉近似稿，与 X/Twitter 官方无关。
