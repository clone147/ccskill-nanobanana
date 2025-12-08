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

- 環境変数 `CCSKILL_NANOBANANA_DIR` にこのスキルのリポジトリパスを設定してください
  ```bash
  export CCSKILL_NANOBANANA_DIR="$HOME/projects/ccskill-nanobanana"
  ```
- 環境変数 `GEMINI_API_KEY` が設定されている必要があります（または `$CCSKILL_NANOBANANA_DIR/.env` に記載）

## 使い方

以下のコマンドで画像を生成します：

```bash
$CCSKILL_NANOBANANA_DIR/venv/bin/python $CCSKILL_NANOBANANA_DIR/generate_image.py "プロンプト"
```

### オプション

- `--resolution`: 解像度（1K, 2K, 4K）デフォルト: 2K
- `--aspect`: アスペクト比（1:1, 16:9, 9:16, 4:3 など）デフォルト: 16:9
- `--output`: 出力ディレクトリ デフォルト: ./generated_images
- `--reference`: 参照画像のパス（複数指定可能、最大14枚）

### 使用例

基本的な画像生成：
```bash
$CCSKILL_NANOBANANA_DIR/venv/bin/python $CCSKILL_NANOBANANA_DIR/generate_image.py "猫がピアノを弾いている水彩画"
```

高解像度でワイド画像を生成：
```bash
$CCSKILL_NANOBANANA_DIR/venv/bin/python $CCSKILL_NANOBANANA_DIR/generate_image.py "夕焼けの海岸線" --resolution 4K --aspect 16:9
```

特定のディレクトリに出力：
```bash
$CCSKILL_NANOBANANA_DIR/venv/bin/python $CCSKILL_NANOBANANA_DIR/generate_image.py "ロゴデザイン" --output ./assets/images
```

### 参照画像を使った編集

既存の画像を参照して編集・変更ができます：

```bash
# 背景を変更
$CCSKILL_NANOBANANA_DIR/venv/bin/python $CCSKILL_NANOBANANA_DIR/generate_image.py "背景を夕焼けに変更して" --reference ./original.png

# 複数の参照画像を使用（ポーズ、スタイルなど）
$CCSKILL_NANOBANANA_DIR/venv/bin/python $CCSKILL_NANOBANANA_DIR/generate_image.py "この人物をこのポーズで描いて" --reference ./person.png --reference ./pose.png
```

参照画像の用途：
- 画像の部分編集（背景変更、色調整など）
- スタイル転送（別の画像のスタイルを適用）
- キャラクター一貫性の維持（同じ人物を異なるシーンで）
- 複数画像の合成

## プロンプトガイドライン

効果的なプロンプトを作成するためのベストプラクティスです。

> 出典: [7 tips to get the most out of Nano Banana Pro](https://blog.google/products/gemini/prompting-tips-nano-banana-pro/) - Google公式ブログ

### 基本要素

プロンプトには以下の要素を含めると、より良い結果が得られます：

- **Subject（主題）**: 誰が/何が画像にいるか？具体的に。（例：光る青い目を持つ無表情なロボットバリスタ、小さな魔法使いの帽子をかぶったふわふわの三毛猫）
- **Composition（構図）**: ショットはどうフレーミングされているか？（例：超クローズアップ、ワイドショット、ローアングルショット、ポートレート）
- **Action（アクション）**: 何が起きているか？（例：コーヒーを淹れている、魔法を唱えている、野原を走っている途中）
- **Location（場所）**: シーンはどこで行われているか？（例：火星の未来的なカフェ、散らかった錬金術師の書斎、ゴールデンアワーの陽光に満ちた草原）
- **Style（スタイル）**: 全体的な美学は？（例：3Dアニメーション、フィルムノワール、水彩画、フォトリアリスティック、1990年代の製品写真）
- **Editing Instructions（編集指示）**: 既存画像を編集する場合は、直接的かつ具体的に。（例：男性のネクタイを緑に変更、背景の車を削除）

### 詳細設定

プロフェッショナルな結果を得るには、より具体的な指示を含めます：

- **構図とアスペクト比**: キャンバスを定義（例：「9:16の縦型ポスター」「シネマティックな21:9のワイドショット」）
- **カメラとライティング**: 撮影監督のようにショットを指示（例：「浅い被写界深度(f/1.8)のローアングルショット」「長い影を作るゴールデンアワーのバックライト」「落ち着いたティール調のシネマティックカラーグレーディング」）
- **テキスト統合**: テキストの見た目と配置を明確に（例：「'URBAN EXPLORER'という見出しを、上部に太字・白・サンセリフフォントで配置」）
- **事実的制約（図表用）**: 正確性の必要性を指定（例：「科学的に正確な断面図」「ビクトリア朝時代の歴史的正確性を確保」）
- **参照画像の役割**: アップロードした画像の役割を明確に定義（例：「画像Aはキャラクターのポーズ用、画像Bはアートスタイル用、画像Cは背景環境用」）

### 現在の制限事項

- 小さいテキストや細部の描画、正確なスペリングは完璧でない場合があります
- 図表やインフォグラフィックの事実的正確性は常に検証してください
- 多言語テキスト生成では文法ミスや文化的ニュアンスの欠落が起こる可能性があります
- 合成やライティング変更などの高度な編集では不自然なアーティファクトが発生することがあります

## 出力

- 画像は指定されたディレクトリ（デフォルト: `./generated_images`）に保存されます
- ファイル名はタイムスタンプ形式（例: `20251130_153045.png`、`20251130_153045.jpg`）
- 拡張子はAPIが返す画像の形式に応じて自動的に決定されます（PNG/JPEG/WebP）

## 注意事項

- 環境変数 `GEMINI_API_KEY` が設定されている必要があります
- Nano Banana Pro は有料APIのため、課金が発生します
- 生成された画像には SynthID ウォーターマークが含まれます
