# Nano Banana Pro Image Generation Skill

[日本語版 README](README.ja.md)

A Claude Code skill for image generation using the Google Nano Banana Pro (Gemini 3 Pro Image) API. Can also be used as a standalone image generation script.

## Setup

### Requirements

- **Python 3.10 or later** (required by `google-genai` library)

### 1. Clone the Repository

```bash
cd /path/to/your-projects  # any location you prefer
git clone https://github.com/feedtailor/ccskill-nanobanana.git
cd ccskill-nanobanana
```

### 2. Get API Key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Sign in with your Google account
3. Click "Get API key" to obtain your API key
    > **Note**: Nano Banana Pro has no free tier, so billing setup is required

### 3. Configure Environment Variables

Copy `.env.example` to create `.env`:

```bash
cp .env.example .env
```

Edit the `.env` file and set your API key:

```
GEMINI_API_KEY=your-api-key-here
```

### 4. Install Dependencies

```bash
# Create venv with Python 3.10 or later
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

### 5. Set Environment Variable (for use as a skill)

Add to your `.bashrc` or `.zshrc`:

```bash
export CCSKILL_NANOBANANA_DIR="/path/to/ccskill-nanobanana"
```

## Usage

### Run from Command Line

```bash
source venv/bin/activate
python generate_image.py "a cat playing piano"
```

### Options

| Option | Description | Default | Choices |
|--------|-------------|---------|---------|
| `--resolution` | Output resolution | 2K | 1K, 2K, 4K |
| `--aspect` | Aspect ratio | 16:9 | 1:1, 16:9, 9:16, 4:3, etc. |
| `--output` | Output directory | ./generated_images | any path |
| `--reference` | Reference image(s) (up to 14) | none | image file path |

### Examples

```bash
# Basic usage
python generate_image.py "sunset coastline"

# High-resolution wide image
python generate_image.py "mountain landscape" --resolution 4K --aspect 16:9

# Specify output directory
python generate_image.py "logo design" --output ./assets/
```

### Image Editing with Reference Images

Edit or modify existing images by providing reference images:

```bash
# Change background
python generate_image.py "change background to sunset" --reference ./original.png

# Use multiple reference images
python generate_image.py "draw this person in this pose" \
    --reference ./person.png \
    --reference ./pose.png
```

Reference image use cases:
- Partial image editing (background change, color adjustment, etc.)
- Style transfer (apply style from another image)
- Character consistency
- Image compositing

## Use as Claude Code Skill

### Install to Other Projects

Install via symbolic link (recommended):

```bash
# Create .claude/skills directory in target project if it doesn't exist
mkdir -p /path/to/your-project/.claude/skills

# Create symbolic link
ln -s $CCSKILL_NANOBANANA_DIR/.claude/skills/nano-banana-pro \
      /path/to/your-project/.claude/skills/nano-banana-pro
```

Claude Code will automatically use this skill when image generation is needed.

Run `git pull` on this repository to update the skill in all linked projects.

### Skill Language Configuration

By default, the skill uses English (`SKILL.md`). To use the Japanese version:

```bash
cd $CCSKILL_NANOBANANA_DIR/.claude/skills/nano-banana-pro

# Switch to Japanese
mv SKILL.md SKILL.en.md
ln -s SKILL.ja.md SKILL.md

# To switch back to English
rm SKILL.md
mv SKILL.en.md SKILL.md
```

## Testing

```bash
source venv/bin/activate
python -m pytest tests/ -v
```

## Specifications

- **Model**: `gemini-3-pro-image-preview` (Nano Banana Pro)
- **Output format**: Automatically determined from API response (PNG/JPEG/WebP)
- **Filename**: Timestamp format (e.g., `20251130_153045.png`, `20251130_153045.jpg`)
- **Watermark**: Generated images include SynthID

## License

MIT
