---
name: nano-banana-pro
description: |
  画像生成が必要な時に使用するスキル。
  Google Nano Banana Pro (Gemini 3 Pro Image) APIを使って高品質な画像を生成します。
  ロゴ、インフォグラフィック、イラスト、写真風画像など様々な用途に対応。
---

# Nano Banana Pro 画像生成スキル

## 概要

このスキルは Google Nano Banana Pro API を使用して画像を生成します。
ユーザーが画像生成を必要とする場面で、このスキルを使って画像を作成できます。

## 前提条件

- 環境変数 `NANO_BANANA_PRO_DIR` にこのスキルのリポジトリパスを設定してください
  ```bash
  export NANO_BANANA_PRO_DIR="$HOME/projects/claudecode-skill-nanobananapro"
  ```
- 環境変数 `GEMINI_API_KEY` が設定されている必要があります（または `$NANO_BANANA_PRO_DIR/.env` に記載）

## 使い方

以下のコマンドで画像を生成します：

```bash
$NANO_BANANA_PRO_DIR/venv/bin/python $NANO_BANANA_PRO_DIR/generate_image.py "プロンプト"
```

### オプション

- `--resolution`: 解像度（1K, 2K, 4K）デフォルト: 2K
- `--aspect`: アスペクト比（1:1, 16:9, 9:16, 4:3 など）デフォルト: 1:1
- `--output`: 出力ディレクトリ デフォルト: ./generated_images

### 使用例

基本的な画像生成：
```bash
$NANO_BANANA_PRO_DIR/venv/bin/python $NANO_BANANA_PRO_DIR/generate_image.py "猫がピアノを弾いている水彩画"
```

高解像度でワイド画像を生成：
```bash
$NANO_BANANA_PRO_DIR/venv/bin/python $NANO_BANANA_PRO_DIR/generate_image.py "夕焼けの海岸線" --resolution 4K --aspect 16:9
```

特定のディレクトリに出力：
```bash
$NANO_BANANA_PRO_DIR/venv/bin/python $NANO_BANANA_PRO_DIR/generate_image.py "ロゴデザイン" --output ./assets/images
```

## 出力

- 画像は指定されたディレクトリ（デフォルト: `./generated_images`）に保存されます
- ファイル名はタイムスタンプ形式（例: `20251130_153045.png`）

## 注意事項

- 環境変数 `GEMINI_API_KEY` が設定されている必要があります
- Nano Banana Pro は有料APIのため、課金が発生します
- 生成された画像には SynthID ウォーターマークが含まれます
