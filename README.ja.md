# Nano Banana Pro 画像生成スキル

[English README](README.md)

Google Nano Banana Pro (Gemini 3 Pro Image) API を使用した Claude Code 用画像生成スキルです。画像生成スクリプト単体として使用することもできます。

## セットアップ

### 必要環境

- **Python 3.10 以上**（`google-genai` ライブラリの要件）

### 1. リポジトリのクローン

```bash
cd /path/to/your-projects  # 任意の場所
git clone https://github.com/feedtailor/ccskill-nanobanana.git
cd ccskill-nanobanana
```

### 2. APIキーの取得

1. [Google AI Studio](https://aistudio.google.com/apikey) にアクセス
2. Google アカウントでログイン
3. 「Get API key」をクリックしてAPIキーを取得
    > **注意**: Nano Banana Pro は無料枠がないため、課金設定が必要になります

### 3. 環境変数の設定

`.env.example` をコピーして `.env` を作成します：

```bash
cp .env.example .env
```

`.env` ファイルを編集し、取得したAPIキーを設定します：

```
GEMINI_API_KEY=your-api-key-here
```

### 4. 依存パッケージのインストール

```bash
# Python 3.10 以上で venv を作成
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

### 5. 環境変数の設定（スキルとして使用する場合）

`.bashrc` や `.zshrc` に以下を追加：

```bash
export CCSKILL_NANOBANANA_DIR="/path/to/ccskill-nanobanana"
```

## 使い方

### コマンドラインから直接実行

```bash
source venv/bin/activate
python generate_image.py "猫がピアノを弾いている"
```

### オプション

| オプション | 説明 | デフォルト | 選択肢 |
|------------|------|------------|--------|
| `--resolution` | 出力解像度 | 2K | 1K, 2K, 4K |
| `--aspect` | アスペクト比 | 16:9 | 1:1, 16:9, 9:16, 4:3 など |
| `--output` | 出力ディレクトリ | ./generated_images | 任意のパス |
| `--reference` | 参照画像（複数指定可、最大14枚） | なし | 画像ファイルパス |

### 使用例

```bash
# 基本的な使い方
python generate_image.py "夕焼けの海岸線"

# 高解像度ワイド画像
python generate_image.py "山岳風景" --resolution 4K --aspect 16:9

# 出力先を指定
python generate_image.py "ロゴデザイン" --output ./assets/
```

### 参照画像を使った編集

既存の画像を参照して編集・変更ができます：

```bash
# 背景を変更
python generate_image.py "背景を夕焼けに変更して" --reference ./original.png

# 複数の参照画像を使用
python generate_image.py "この人物をこのポーズで描いて" \
    --reference ./person.png \
    --reference ./pose.png
```

参照画像の用途：
- 画像の部分編集（背景変更、色調整など）
- スタイル転送（別の画像のスタイルを適用）
- キャラクター一貫性の維持
- 複数画像の合成

## Claude Code スキルとして使用

### 他のプロジェクトへのインストール

シンボリックリンクを使ってインストール（推奨）：

```bash
# インストール先のプロジェクトに .claude/skills ディレクトリがなければ作成
mkdir -p /path/to/your-project/.claude/skills

# シンボリックリンクを作成
ln -s $CCSKILL_NANOBANANA_DIR/.claude/skills/nano-banana-pro \
      /path/to/your-project/.claude/skills/nano-banana-pro
```

これで Claude Code から画像生成が必要な場面で、このスキルが自動的に利用されます。

本体リポジトリを `git pull` すれば、リンク先のプロジェクトでも自動的にスキルが更新されます。

### スキル言語の設定

デフォルトでは英語版（`SKILL.md`）が使用されます。日本語版を使用するには：

```bash
cd $CCSKILL_NANOBANANA_DIR/.claude/skills/nano-banana-pro

# 日本語に切り替え
mv SKILL.md SKILL.en.md
ln -s SKILL.ja.md SKILL.md

# 英語に戻す場合
rm SKILL.md
mv SKILL.en.md SKILL.md
```

## テスト

```bash
source venv/bin/activate
python -m pytest tests/ -v
```

## 仕様

- **モデル**: `gemini-3-pro-image-preview` (Nano Banana Pro)
- **出力形式**: APIが返す形式に応じて自動決定（PNG/JPEG/WebP）
- **ファイル名**: タイムスタンプ形式（例: `20251130_153045.png`、`20251130_153045.jpg`）
- **ウォーターマーク**: 生成画像には SynthID が埋め込まれます

## ライセンス

MIT
