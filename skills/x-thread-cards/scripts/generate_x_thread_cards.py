#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont


BLACK = (15, 20, 25)
GRAY = (84, 96, 106)
LIGHT_GRAY = (218, 225, 232)
DARK_SCROLL = (112, 112, 112)

NO_LINE_START = set("，。、！？；：,.!?;:、）】》」』’”")
NO_LINE_END = set("（【《「『‘“")

PINGFANG_CANDIDATES = [
    "/System/Library/AssetsV2/com_apple_MobileAsset_Font8/86ba2c91f017a3749571a82f2c6d890ac7ffb2fb.asset/AssetData/PingFang.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
]


def find_font() -> str:
    for candidate in PINGFANG_CANDIDATES:
        if Path(candidate).exists():
            return candidate
    raise SystemExit("No supported CJK font found. Pass --font /path/to/font.ttc.")


def font(path: str, size: int, index: int = 0) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size, index=index)


def parse_box(raw: str) -> tuple[int, int, int, int]:
    parts = [int(part.strip()) for part in raw.split(",")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("box must be x1,y1,x2,y2")
    x1, y1, x2, y2 = parts
    if x2 <= x1 or y2 <= y1:
        raise argparse.ArgumentTypeError("box must satisfy x2>x1 and y2>y1")
    return x1, y1, x2, y2


def transparent_nonwhite(crop: Image.Image, threshold: int = 246) -> Image.Image:
    crop = crop.convert("RGBA")
    px = crop.load()
    for y in range(crop.height):
        for x in range(crop.width):
            r, g, b, a = px[x, y]
            if r > threshold and g > threshold and b > threshold:
                px[x, y] = (255, 255, 255, 0)
            else:
                px[x, y] = (r, g, b, a)
    return crop


def account_assets(
    screenshot: Path,
    avatar_box: tuple[int, int, int, int],
    name_box: tuple[int, int, int, int],
    avatar_size: int,
) -> tuple[Image.Image, Image.Image]:
    ref = Image.open(screenshot).convert("RGBA")
    avatar = ref.crop(avatar_box).resize((avatar_size, avatar_size), Image.LANCZOS)
    mask = Image.new("L", avatar.size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, avatar_size - 1, avatar_size - 1), fill=255)
    avatar.putalpha(mask)
    name = transparent_nonwhite(ref.crop(name_box))
    return avatar, name


def wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font_obj: ImageFont.FreeTypeFont,
    max_width: int,
) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        line = ""
        for ch in paragraph:
            candidate = line + ch
            if draw.textlength(candidate, font=font_obj) <= max_width:
                line = candidate
            elif ch in NO_LINE_START and line:
                line = candidate
            else:
                if line and line[-1] in NO_LINE_END:
                    ch = line[-1] + ch
                    line = line[:-1]
                if line:
                    lines.append(line)
                line = ch
        if line:
            lines.append(line)
        if not paragraph:
            lines.append("")
    return lines


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    text: str,
    xy: tuple[int, int],
    max_width: int,
    font_obj: ImageFont.FreeTypeFont,
    line_h: int,
) -> None:
    x, y = xy
    for line in wrap_text(draw, text, font_obj, max_width):
        if line:
            draw.text((x, y), line, font=font_obj, fill=BLACK)
        y += line_h


def draw_x_mark(draw: ImageDraw.ImageDraw, width: int) -> None:
    left = width - 62
    right = width - 24
    draw.line((left, 34, right, 72), fill=BLACK, width=5)
    draw.line((right, 34, left, 72), fill=BLACK, width=5)


def draw_header(
    img: Image.Image,
    draw: ImageDraw.ImageDraw,
    avatar: Image.Image,
    name: Image.Image,
    meta: str,
    f_meta: ImageFont.FreeTypeFont,
    width: int,
    height: int,
    avatar_xy: tuple[int, int],
    content_x: int,
) -> None:
    img.alpha_composite(avatar, avatar_xy)
    draw.line((avatar_xy[0] + 70, 190, avatar_xy[0] + 70, height), fill=LIGHT_GRAY, width=7)
    img.alpha_composite(name, (content_x, 32))
    draw.text((content_x + name.width + 24, 42), meta, font=f_meta, fill=GRAY)
    draw_x_mark(draw, width)
    draw.rounded_rectangle((width - 22, 108, width - 12, 420), radius=5, fill=DARK_SCROLL)


def load_slides(args: argparse.Namespace) -> list[dict[str, str]]:
    if args.slides:
        data = json.loads(args.slides)
    elif args.slides_json:
        data = json.loads(Path(args.slides_json).read_text(encoding="utf-8"))
    else:
        raise SystemExit("Pass --slides-json PATH or --slides JSON.")
    if not isinstance(data, list):
        raise SystemExit("Slides must be a JSON list.")
    for idx, slide in enumerate(data, start=1):
        if not isinstance(slide, dict) or "title" not in slide or "body" not in slide:
            raise SystemExit(f"Slide {idx} must contain title and body.")
    return data


def draw_slide(
    slide: dict[str, str],
    index: int,
    out_path: Path,
    args: argparse.Namespace,
    avatar: Image.Image,
    name: Image.Image,
    fonts: dict[str, ImageFont.FreeTypeFont],
) -> None:
    img = Image.new("RGBA", (args.width, args.height), "white")
    draw = ImageDraw.Draw(img)
    draw_header(
        img,
        draw,
        avatar,
        name,
        args.meta,
        fonts["meta"],
        args.width,
        args.height,
        (args.avatar_x, args.avatar_y),
        args.content_x,
    )
    title = slide["title"]
    if args.number_titles and not title.lstrip().startswith(f"{index}."):
        title = f"{index}. {title}"
    draw.text((args.content_x, args.title_y), title, font=fonts["title"], fill=BLACK)
    body = slide["body"]
    if args.quote_body:
        body = f"'{body}'"
    draw_wrapped(
        draw,
        body,
        (args.content_x, args.body_y),
        args.text_width,
        fonts["body"],
        args.line_height,
    )
    img.convert("RGB").save(out_path, quality=96)


def make_contact_sheet(paths: Iterable[Path], out_path: Path, args: argparse.Namespace) -> None:
    paths = list(paths)
    if not paths:
        return
    thumb_w = args.width // args.contact_cols
    thumb_h = args.height // 2 if args.contact_cols == 2 else args.height
    rows = (len(paths) + args.contact_cols - 1) // args.contact_cols
    sheet = Image.new("RGB", (thumb_w * args.contact_cols, thumb_h * rows), "white")
    for idx, path in enumerate(paths):
        thumb = Image.open(path).convert("RGB").resize((thumb_w, thumb_h), Image.LANCZOS)
        x = (idx % args.contact_cols) * thumb_w
        y = (idx // args.contact_cols) * thumb_h
        sheet.paste(thumb, (x, y))
    sheet.save(out_path, quality=95)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate X-style screenshot thread cards.")
    parser.add_argument("--account-screenshot", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--slides-json", type=Path)
    parser.add_argument("--slides", help="Inline JSON list of {title, body} objects.")
    parser.add_argument("--avatar-box", type=parse_box, default=(28, 253, 174, 399))
    parser.add_argument("--name-box", type=parse_box, default=(206, 272, 644, 324))
    parser.add_argument("--meta", default="@lin_ai_notes · 14小时")
    parser.add_argument("--width", type=int, default=1242)
    parser.add_argument("--height", type=int, default=510)
    parser.add_argument("--font", default=find_font())
    parser.add_argument("--title-size", type=int, default=43)
    parser.add_argument("--body-size", type=int, default=45)
    parser.add_argument("--meta-size", type=int, default=36)
    parser.add_argument("--title-weight-index", type=int, default=11)
    parser.add_argument("--body-weight-index", type=int, default=7)
    parser.add_argument("--meta-weight-index", type=int, default=3)
    parser.add_argument("--avatar-size", type=int, default=144)
    parser.add_argument("--avatar-x", type=int, default=27)
    parser.add_argument("--avatar-y", type=int, default=34)
    parser.add_argument("--content-x", type=int, default=194)
    parser.add_argument("--title-y", type=int, default=104)
    parser.add_argument("--body-y", type=int, default=228)
    parser.add_argument("--text-width", type=int, default=980)
    parser.add_argument("--line-height", type=int, default=64)
    parser.add_argument("--number-titles", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--quote-body", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--contact-cols", type=int, default=2)
    parser.add_argument("--no-contact-sheet", action="store_true")
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    slides = load_slides(args)
    avatar, name = account_assets(args.account_screenshot, args.avatar_box, args.name_box, args.avatar_size)
    fonts = {
        "title": font(args.font, args.title_size, args.title_weight_index),
        "body": font(args.font, args.body_size, args.body_weight_index),
        "meta": font(args.font, args.meta_size, args.meta_weight_index),
    }

    paths = []
    for index, slide in enumerate(slides, start=1):
        out_path = args.out_dir / f"{index:02d}_{slide.get('slug', 'card')}.png"
        draw_slide(slide, index, out_path, args, avatar, name, fonts)
        paths.append(out_path)

    if not args.no_contact_sheet:
        make_contact_sheet(paths, args.out_dir / "contact_sheet.png", args)

    print(f"wrote {len(paths)} cards to {args.out_dir}")


if __name__ == "__main__":
    main()
