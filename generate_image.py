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
from PIL import Image

# このスクリプトと同じディレクトリの .env を読み込む
_script_dir = Path(__file__).parent
load_dotenv(_script_dir / ".env")

# デフォルト値
DEFAULT_RESOLUTION = "2K"
DEFAULT_ASPECT_RATIO = "16:9"
DEFAULT_OUTPUT_DIR = "./generated_images"

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
    return parser.parse_args(args)


def get_output_path(output_dir: str, mime_type: str = "image/png") -> Path:
    """出力ファイルパスを生成する"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # タイムスタンプ形式のファイル名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = MIME_TO_EXT.get(mime_type, ".png")
    return output_path / f"{timestamp}{ext}"


ENHANCE_SYSTEM_PROMPT = """\
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


def enhance_prompt(client: genai.Client, prompt: str) -> str:
    """Enhance a simple prompt into a detailed, professional image generation prompt."""
    print(f"[Enhance] Rewriting prompt...")
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Enhance this image prompt:\n\n{prompt}",
            config=types.GenerateContentConfig(
                system_instruction=ENHANCE_SYSTEM_PROMPT,
                temperature=0.9,
            )
        )
        enhanced = response.text.strip()
        print(f"[Enhance] Enhanced prompt:\n{enhanced}")
        return enhanced
    except Exception as e:
        print(f"[Enhance] Failed to enhance, using original: {e}")
        return prompt


def generate_image(
    prompt: str,
    resolution: str,
    aspect_ratio: str,
    output_dir: str,
    reference_images: list[str] | None = None,
    raw: bool = False
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
        prompt = enhance_prompt(client, prompt)

    # コンテンツの構築
    if reference_images:
        # 参照画像がある場合はリストで渡す
        contents: list = []
        for image_path in reference_images:
            img = Image.open(image_path)
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
    for part in response.parts:
        if part.text is not None:
            print(f"[Info] {part.text}")
        elif part.inline_data is not None:
            # APIが返す画像の実際のMIMEタイプを検出
            mime_type = part.inline_data.mime_type or "image/png"
            image = part.as_image()
            output_path = get_output_path(output_dir, mime_type)
            image.save(str(output_path))
            print(f"[Success] 画像を保存しました: {output_path}")
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
            raw=args.raw
        )
        if result is None:
            sys.exit(1)
    except Exception as e:
        print(f"[Error] 画像生成に失敗しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
