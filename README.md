# Nano Banana Pro 画像生成スキル

Google Nano Banana Pro (Gemini 3 Pro Image) API を使用した Claude Code 用画像生成スキルです。

## セットアップ

### 1. APIキーの取得

1. [Google AI Studio](https://aistudio.google.com/apikey) にアクセス
2. Google アカウントでログイン
3. 「Get API key」をクリックしてAPIキーを取得
4. **注意**: Nano Banana Pro は無料枠がないため、課金設定が必要です

### 2. 環境変数の設定

`.env.example` をコピーして `.env` を作成し、APIキーを設定します：

```bash
cp .env.example .env
# .env を編集して GEMINI_API_KEY を設定
```

`.env` ファイルの内容：
```
GEMINI_API_KEY=your-api-key-here
```

### 3. 依存パッケージのインストール

```bash
# リポジトリをクローンした場所に移動
cd /path/to/claudecode-skill-nanobananapro
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. 環境変数の設定（スキルとして使用する場合）

`.bashrc` や `.zshrc` に以下を追加：

```bash
export NANO_BANANA_PRO_DIR="$HOME/projects/claudecode-skill-nanobananapro"
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
ln -s $NANO_BANANA_PRO_DIR/.claude/skills/nano-banana-pro \
      /path/to/your-project/.claude/skills/nano-banana-pro
```

これで Claude Code から画像生成が必要な場面で、このスキルが自動的に利用されます。

本体リポジトリを `git pull` すれば、リンク先のプロジェクトでも自動的にスキルが更新されます。

## テスト

```bash
source venv/bin/activate
python -m pytest tests/ -v
```

## 仕様

- **モデル**: `gemini-3-pro-image-preview` (Nano Banana Pro)
- **出力形式**: PNG
- **ファイル名**: タイムスタンプ形式（例: `20251130_153045.png`）
- **ウォーターマーク**: 生成画像には SynthID が埋め込まれます

## ライセンス

MIT
