#!/usr/bin/env python3
"""
Nano Banana Pro 画像生成スクリプト

Google Gemini 3 Pro Image (Nano Banana Pro) APIを使用して画像を生成します。

使用方法:
    python generate_image.py "プロンプト" [--resolution 2K] [--aspect 1:1] [--output ./generated_images]
    python generate_image.py "背景を変更" --reference original.png

環境変数:
    GEMINI_API_KEY: Google AI Studio で取得したAPIキー
    （.env ファイルに記載可能）
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image as PILImage
import io

# このスクリプトと同じディレクトリの .env を読み込む
_script_dir = Path(__file__).parent
load_dotenv(_script_dir / ".env")

# デフォルト値
DEFAULT_RESOLUTION = "2K"
DEFAULT_ASPECT_RATIO = "16:9"
DEFAULT_OUTPUT_DIR = "./generated_images"
DEFAULT_FORMAT = "jpg"
DEFAULT_QUALITY = 85

# MIMEタイプから拡張子へのマッピング
MIME_TO_EXT = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/webp": ".webp",
}


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """コマンドライン引数をパースする"""
    parser = argparse.ArgumentParser(
        description="Nano Banana Pro APIで画像を生成します"
    )
    parser.add_argument(
        "prompt",
        type=str,
        help="画像生成のプロンプト"
    )
    parser.add_argument(
        "--resolution",
        type=str,
        default=DEFAULT_RESOLUTION,
        choices=["1K", "2K", "4K"],
        help=f"出力解像度 (デフォルト: {DEFAULT_RESOLUTION})"
    )
    parser.add_argument(
        "--aspect",
        type=str,
        default=DEFAULT_ASPECT_RATIO,
        help=f"アスペクト比 (デフォルト: {DEFAULT_ASPECT_RATIO})"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=DEFAULT_OUTPUT_DIR,
        help=f"出力ディレクトリ (デフォルト: {DEFAULT_OUTPUT_DIR})"
    )
    parser.add_argument(
        "--reference",
        type=str,
        action="append",
        default=[],
        help="参照画像のパス（複数指定可能、最大14枚）"
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        default=False,
        help="Skip prompt enhancement — use the prompt as-is"
    )
    parser.add_argument(
        "--format",
        type=str,
        default=DEFAULT_FORMAT,
        choices=["jpg", "png", "webp"],
        help=f"Output format (default: {DEFAULT_FORMAT})"
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=DEFAULT_QUALITY,
        help=f"Output quality 1-100 (default: {DEFAULT_QUALITY})"
    )
    parser.add_argument(
        "--lang",
        type=str,
        default="pl",
        help="Language for text in images: 'pl' (Polish, default), 'en' (English), 'none' (suppress all text)"
    )
    parser.add_argument(
        "--text",
        type=str,
        default=None,
        help="Explicit text to render in the image (in target language)"
    )
    return parser.parse_args(args)


def get_output_path(output_dir: str, ext: str = ".png") -> Path:
    """出力ファイルパスを生成する"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # タイムスタンプ形式のファイル名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return output_path / f"{timestamp}{ext}"


_ENHANCE_BASE = """\
You are a world-class art director, photographer, and visual storytelling master. \
Your job is to take a simple image prompt and transform it into a richly detailed, \
cinematic prompt that will produce stunning, professional-quality images.

RULES:
1. Rewrite the prompt using natural, descriptive English sentences (never tag soup).
2. Add specific details about: composition, camera angle, lighting (type, direction, color temperature), \
   materials/textures, mood/atmosphere, color palette, and depth of field.
3. Keep the original intent and subject matter — enhance, don't change the concept.
4. If the prompt involves or could involve people/humans: ALL people MUST be white/Caucasian \
   with Central-Eastern European (Polish) appearance — fair skin, natural hair colors \
   (blonde, brown, auburn), European facial features. This is a hard requirement.
5. Output ONLY the enhanced prompt — no explanations, no preamble, no quotes around it.
6. Keep the enhanced prompt under 300 words.
7. Think like a cinematographer briefing a VFX team — be precise about every visual element.\
"""

_RULE8_NO_TEXT = """
8. CRITICAL — NO TEXT RULE: The image MUST NOT contain ANY visible text, letters, words, \
   numbers, labels, titles, captions, UI text, signs, watermarks, buttons, menus, or written \
   characters of any kind. This is absolute — zero exceptions. \
   If the scene includes screens, monitors, dashboards, or phones — show them with abstract \
   visualizations, colorful graphs, bokeh/blurred content, or geometric patterns instead of \
   any readable text or characters. \
   REMOVE any text-containing elements from your enhanced prompt. Replace descriptions like \
   "dashboard showing analytics" with "dashboard displaying abstract colorful data visualizations \
   with no readable text". \
   Add this sentence at the END of your enhanced prompt: \
   "Absolutely no visible text, letters, words, labels, or written characters anywhere in the image." \
   FALLBACK: If the image model ignores this and renders text anyway, any text that appears \
   MUST be in Polish language, never English.\
"""

_RULE8_POLISH_TEXT = """
8. CRITICAL — TEXT RULE: Render this exact Polish text on the sign/wall/surface: "{text}" \
   Use elegant, legible typography that matches the scene aesthetic. \
   Do NOT add any other text, labels, or words anywhere in the image. \
   Do NOT include formatting markers, asterisks, colons, or meta-instructions in the rendered text. \
   The ONLY visible text in the entire image should be: "{text}"\
"""

_RULE8_ENGLISH = """
8. Text in the image (if any) should be in English.\
"""


def _build_enhance_prompt(lang: str, text: str | None) -> str:
    """Build the system prompt for the enhancer based on language and text settings."""
    if text:
        rule8 = _RULE8_POLISH_TEXT.format(text=text) if lang == "pl" else _RULE8_ENGLISH
    elif lang in ("pl", "none"):
        rule8 = _RULE8_NO_TEXT
    else:
        rule8 = _RULE8_ENGLISH
    return _ENHANCE_BASE + rule8


def enhance_prompt(client: genai.Client, prompt: str, lang: str = "pl", text: str | None = None) -> str:
    """Enhance a simple prompt into a detailed, professional image generation prompt."""
    print(f"[Enhance] Rewriting prompt (lang={lang}, text={'yes' if text else 'no'})...")
    system_prompt = _build_enhance_prompt(lang, text)
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Enhance this image prompt:\n\n{prompt}",
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.9,
            )
        )
        enhanced = response.text.strip()
        print(f"[Enhance] Enhanced prompt:\n{enhanced}")
        return enhanced
    except Exception as e:
        print(f"[Enhance] Failed to enhance, using original: {e}")
        return prompt


def localize_text(
    client: genai.Client,
    image_path: str,
    lang: str,
    aspect_ratio: str,
    resolution: str,
    output_format: str,
    quality: int,
) -> str | None:
    """Second pass: translate any visible text in the image to the target language."""
    lang_name = {"pl": "Polish", "en": "English"}.get(lang, lang)
    print(f"[Localize] Translating text to {lang_name}...")
    img = PILImage.open(image_path)

    prompt = (
        f"Find ALL visible text, labels, UI elements, signs, captions, and written words "
        f"in this image. Translate every piece of text to {lang_name} language. "
        f"Keep the exact same visual style, fonts, colors, layout, and positioning. "
        f"Only change the language of the text. If no text is found, return the image unchanged."
    )

    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-image-preview",
            contents=[img, prompt],
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio,
                    image_size=resolution,
                )
            )
        )

        for part in response.parts:
            if part.text is not None:
                print(f"[Localize] {part.text}")
            elif part.inline_data is not None:
                raw_data = part.inline_data.data
                pil_image = PILImage.open(io.BytesIO(raw_data))
                output_path = Path(image_path)

                if output_format == "jpg":
                    if pil_image.mode in ("RGBA", "LA", "P"):
                        pil_image = pil_image.convert("RGB")
                    pil_image.save(str(output_path), "JPEG", quality=quality, optimize=True)
                elif output_format == "webp":
                    pil_image.save(str(output_path), "WEBP", quality=quality, method=6)
                else:
                    pil_image.save(str(output_path), "PNG", optimize=True)

                size_kb = output_path.stat().st_size / 1024
                print(f"[Localize] Saved: {output_path} ({size_kb:.0f} KB)")
                return str(output_path)

        print("[Localize] No image in response, keeping original")
    except Exception as e:
        print(f"[Localize] Failed: {e}, keeping original")
    return image_path


def generate_image(
    prompt: str,
    resolution: str,
    aspect_ratio: str,
    output_dir: str,
    reference_images: list[str] | None = None,
    raw: bool = False,
    output_format: str = DEFAULT_FORMAT,
    quality: int = DEFAULT_QUALITY,
    lang: str = "pl",
    text: str | None = None,
) -> str | None:
    """
    Nano Banana Pro APIで画像を生成する

    Args:
        prompt: 画像生成のプロンプト
        resolution: 出力解像度 (1K, 2K, 4K)
        aspect_ratio: アスペクト比 (例: 1:1, 16:9)
        output_dir: 出力ディレクトリ
        reference_images: 参照画像のパスリスト（最大14枚）
        raw: Trueの場合、プロンプトを強化せずそのまま使用する
        output_format: 出力フォーマット (jpg, png, webp)
        quality: 出力品質 1-100

    Returns:
        生成された画像のファイルパス、失敗時はNone
    """
    # 参照画像の存在確認
    if reference_images:
        for image_path in reference_images:
            if not Path(image_path).exists():
                print(f"[Error] 参照画像が見つかりません: {image_path}")
                return None

    client = genai.Client()

    # Enhance prompt unless raw mode or reference images (editing mode)
    if not raw and not reference_images:
        prompt = enhance_prompt(client, prompt, lang=lang, text=text)

    # コンテンツの構築
    if reference_images:
        # 参照画像がある場合はリストで渡す
        contents: list = []
        for image_path in reference_images:
            img = PILImage.open(image_path)
            contents.append(img)
        contents.append(prompt)
    else:
        # 参照画像がない場合はプロンプトのみ
        contents = prompt

    response = client.models.generate_content(
        model="gemini-3.1-flash-image-preview",
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(
                aspect_ratio=aspect_ratio,
                image_size=resolution
            )
        )
    )

    # レスポンスから画像を取得して保存
    format_ext = {"jpg": ".jpg", "png": ".png", "webp": ".webp"}
    target_ext = format_ext.get(output_format, ".jpg")

    for part in response.parts:
        if part.text is not None:
            print(f"[Info] {part.text}")
        elif part.inline_data is not None:
            # Convert genai Image to PIL Image for format control
            raw_data = part.inline_data.data
            pil_image = PILImage.open(io.BytesIO(raw_data))
            output_path = get_output_path(output_dir, target_ext)

            # Save in target format with quality control
            if output_format == "jpg":
                if pil_image.mode in ("RGBA", "LA", "P"):
                    pil_image = pil_image.convert("RGB")
                pil_image.save(str(output_path), "JPEG", quality=quality, optimize=True)
            elif output_format == "webp":
                pil_image.save(str(output_path), "WEBP", quality=quality, method=6)
            else:
                pil_image.save(str(output_path), "PNG", optimize=True)

            size_kb = output_path.stat().st_size / 1024
            print(f"[Success] Saved: {output_path} ({size_kb:.0f} KB, {output_format.upper()} q{quality})")

            # Localization pass: translate text to target language if text was requested
            if text and lang == "pl":
                result_path = localize_text(
                    client, str(output_path), lang, aspect_ratio, resolution,
                    output_format, quality,
                )
                return result_path

            return str(output_path)

    print("[Warning] レスポンスに画像が含まれていませんでした")
    return None


def main():
    """メイン関数"""
    args = parse_args()

    # 参照画像の数をチェック
    if args.reference and len(args.reference) > 14:
        print("[Error] 参照画像は最大14枚までです")
        sys.exit(1)

    try:
        result = generate_image(
            prompt=args.prompt,
            resolution=args.resolution,
            aspect_ratio=args.aspect,
            output_dir=args.output,
            reference_images=args.reference if args.reference else None,
            raw=args.raw,
            output_format=args.format,
            quality=args.quality,
            lang=args.lang,
            text=args.text,
        )
        if result is None:
            sys.exit(1)
    except Exception as e:
        print(f"[Error] 画像生成に失敗しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
