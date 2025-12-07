"""
Nano Banana Pro 画像生成スクリプトのテスト
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

# テスト対象モジュールのパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from generate_image import (
    generate_image,
    parse_args,
    get_output_path,
    DEFAULT_RESOLUTION,
    DEFAULT_ASPECT_RATIO,
    DEFAULT_OUTPUT_DIR,
    MIME_TO_EXT,
)


class TestParseArgs:
    """コマンドライン引数パーサーのテスト"""

    def test_prompt_only(self):
        """プロンプトのみ指定"""
        args = parse_args(["猫がピアノを弾いている"])
        assert args.prompt == "猫がピアノを弾いている"
        assert args.resolution == DEFAULT_RESOLUTION
        assert args.aspect == DEFAULT_ASPECT_RATIO
        assert args.output == DEFAULT_OUTPUT_DIR

    def test_with_resolution(self):
        """解像度を指定"""
        args = parse_args(["プロンプト", "--resolution", "4K"])
        assert args.resolution == "4K"

    def test_with_aspect_ratio(self):
        """アスペクト比を指定"""
        args = parse_args(["プロンプト", "--aspect", "16:9"])
        assert args.aspect == "16:9"

    def test_with_output_dir(self):
        """出力ディレクトリを指定"""
        args = parse_args(["プロンプト", "--output", "./custom_output/"])
        assert args.output == "./custom_output/"

    def test_all_options(self):
        """全オプションを指定"""
        args = parse_args([
            "風景画",
            "--resolution", "1K",
            "--aspect", "4:3",
            "--output", "/tmp/images/"
        ])
        assert args.prompt == "風景画"
        assert args.resolution == "1K"
        assert args.aspect == "4:3"
        assert args.output == "/tmp/images/"


class TestGetOutputPath:
    """出力パス生成のテスト"""

    def test_creates_directory_if_not_exists(self):
        """ディレクトリが存在しない場合は作成される"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "new_dir"
            output_path = get_output_path(str(output_dir))
            assert output_dir.exists()
            assert output_path.parent == output_dir

    def test_filename_format(self):
        """ファイル名がタイムスタンプ形式である"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = get_output_path(tmpdir)
            # ファイル名が YYYYMMDD_HHMMSS.png 形式であること
            filename = output_path.name
            assert filename.endswith(".png")
            # 数字とアンダースコアのみで構成
            name_without_ext = filename[:-4]
            assert name_without_ext.replace("_", "").isdigit()
            assert len(name_without_ext) == 15  # YYYYMMDD_HHMMSS


class TestGenerateImage:
    """画像生成のテスト"""

    @patch("generate_image.genai")
    def test_successful_generation(self, mock_genai):
        """正常に画像が生成される"""
        # モックの設定
        mock_client = Mock()
        mock_genai.Client.return_value = mock_client

        mock_image = Mock()
        mock_image.save = Mock()

        mock_inline_data = Mock()
        mock_inline_data.mime_type = "image/png"

        mock_part = Mock()
        mock_part.text = None
        mock_part.inline_data = mock_inline_data
        mock_part.as_image.return_value = mock_image

        mock_response = Mock()
        mock_response.parts = [mock_part]
        mock_client.models.generate_content.return_value = mock_response

        with tempfile.TemporaryDirectory() as tmpdir:
            result = generate_image(
                prompt="テスト画像",
                resolution="2K",
                aspect_ratio="1:1",
                output_dir=tmpdir
            )

            # API呼び出しの確認
            mock_client.models.generate_content.assert_called_once()
            call_kwargs = mock_client.models.generate_content.call_args
            assert call_kwargs.kwargs["model"] == "gemini-3-pro-image-preview"

            # 画像保存の確認
            mock_image.save.assert_called_once()
            assert result is not None
            assert result.endswith(".png")

    @patch("generate_image.genai")
    def test_no_image_in_response(self, mock_genai):
        """レスポンスに画像がない場合はNoneを返す"""
        mock_client = Mock()
        mock_genai.Client.return_value = mock_client

        mock_part = Mock()
        mock_part.text = "テキストのみ"
        mock_part.inline_data = None

        mock_response = Mock()
        mock_response.parts = [mock_part]
        mock_client.models.generate_content.return_value = mock_response

        with tempfile.TemporaryDirectory() as tmpdir:
            result = generate_image(
                prompt="テスト",
                resolution="2K",
                aspect_ratio="1:1",
                output_dir=tmpdir
            )
            assert result is None

    @patch("generate_image.genai")
    def test_api_error_handling(self, mock_genai):
        """APIエラー時に例外が発生する"""
        mock_client = Mock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.generate_content.side_effect = Exception("API Error")

        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(Exception, match="API Error"):
                generate_image(
                    prompt="テスト",
                    resolution="2K",
                    aspect_ratio="1:1",
                    output_dir=tmpdir
                )


class TestReferenceImageOption:
    """参照画像オプションのテスト"""

    def test_no_reference_image(self):
        """参照画像なしの場合は空リスト"""
        args = parse_args(["プロンプト"])
        assert args.reference == []

    def test_single_reference_image(self):
        """参照画像を1つ指定"""
        args = parse_args(["プロンプト", "--reference", "image.png"])
        assert args.reference == ["image.png"]

    def test_multiple_reference_images(self):
        """参照画像を複数指定"""
        args = parse_args([
            "プロンプト",
            "--reference", "image1.png",
            "--reference", "image2.png",
            "--reference", "image3.png"
        ])
        assert args.reference == ["image1.png", "image2.png", "image3.png"]

    @patch("generate_image.genai")
    @patch("generate_image.Image")
    def test_generate_with_reference_image(self, mock_pil_image, mock_genai):
        """参照画像付きで画像生成"""
        # モックの設定
        mock_client = Mock()
        mock_genai.Client.return_value = mock_client

        mock_loaded_image = Mock()
        mock_pil_image.open.return_value = mock_loaded_image

        mock_image = Mock()
        mock_image.save = Mock()

        mock_inline_data = Mock()
        mock_inline_data.mime_type = "image/jpeg"

        mock_part = Mock()
        mock_part.text = None
        mock_part.inline_data = mock_inline_data
        mock_part.as_image.return_value = mock_image

        mock_response = Mock()
        mock_response.parts = [mock_part]
        mock_client.models.generate_content.return_value = mock_response

        with tempfile.TemporaryDirectory() as tmpdir:
            # ダミーの参照画像ファイルを作成
            ref_image_path = Path(tmpdir) / "reference.png"
            ref_image_path.touch()

            result = generate_image(
                prompt="背景を夕焼けに変更",
                resolution="2K",
                aspect_ratio="1:1",
                output_dir=tmpdir,
                reference_images=[str(ref_image_path)]
            )

            # 画像が読み込まれたことを確認
            mock_pil_image.open.assert_called_once_with(str(ref_image_path))

            # API呼び出しで画像が含まれていることを確認
            call_kwargs = mock_client.models.generate_content.call_args
            contents = call_kwargs.kwargs["contents"]
            assert mock_loaded_image in contents
            assert "背景を夕焼けに変更" in contents

            assert result is not None


class TestReferenceImageValidation:
    """参照画像の検証テスト"""

    def test_nonexistent_reference_image_returns_none(self):
        """存在しない参照画像を指定した場合はNoneを返す"""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = generate_image(
                prompt="テスト",
                resolution="2K",
                aspect_ratio="1:1",
                output_dir=tmpdir,
                reference_images=["/nonexistent/path/to/image.png"]
            )
            assert result is None

    def test_nonexistent_reference_image_prints_error(self, capsys):
        """存在しない参照画像を指定した場合はエラーメッセージを出力"""
        with tempfile.TemporaryDirectory() as tmpdir:
            generate_image(
                prompt="テスト",
                resolution="2K",
                aspect_ratio="1:1",
                output_dir=tmpdir,
                reference_images=["/nonexistent/path/to/image.png"]
            )
            captured = capsys.readouterr()
            assert "[Error]" in captured.out
            assert "参照画像が見つかりません" in captured.out
            assert "/nonexistent/path/to/image.png" in captured.out


class TestDefaultValues:
    """デフォルト値のテスト"""

    def test_default_resolution(self):
        assert DEFAULT_RESOLUTION == "2K"

    def test_default_aspect_ratio(self):
        assert DEFAULT_ASPECT_RATIO == "16:9"

    def test_default_output_dir(self):
        assert DEFAULT_OUTPUT_DIR == "./generated_images"


class TestGetOutputPathWithMimeType:
    """MIMEタイプ指定付き出力パス生成のテスト"""

    def test_output_path_png(self):
        """PNG MIMEタイプの拡張子"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = get_output_path(tmpdir, "image/png")
            assert output_path.suffix == ".png"

    def test_output_path_jpeg(self):
        """JPEG MIMEタイプの拡張子"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = get_output_path(tmpdir, "image/jpeg")
            assert output_path.suffix == ".jpg"

    def test_output_path_webp(self):
        """WebP MIMEタイプの拡張子"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = get_output_path(tmpdir, "image/webp")
            assert output_path.suffix == ".webp"

    def test_output_path_unknown_defaults_to_png(self):
        """未知のMIMEタイプはPNGにフォールバック"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = get_output_path(tmpdir, "image/unknown")
            assert output_path.suffix == ".png"


class TestMimeTypeDetection:
    """MIMEタイプ自動検出のテスト"""

    @patch("generate_image.genai")
    def test_jpeg_mime_type_detection(self, mock_genai):
        """JPEG MIMEタイプを検出して.jpg拡張子で保存"""
        mock_client = Mock()
        mock_genai.Client.return_value = mock_client

        mock_image = Mock()
        mock_image.save = Mock()

        mock_inline_data = Mock()
        mock_inline_data.mime_type = "image/jpeg"

        mock_part = Mock()
        mock_part.text = None
        mock_part.inline_data = mock_inline_data
        mock_part.as_image.return_value = mock_image

        mock_response = Mock()
        mock_response.parts = [mock_part]
        mock_client.models.generate_content.return_value = mock_response

        with tempfile.TemporaryDirectory() as tmpdir:
            result = generate_image(
                prompt="テスト画像",
                resolution="2K",
                aspect_ratio="1:1",
                output_dir=tmpdir
            )

            assert result is not None
            assert result.endswith(".jpg")

    @patch("generate_image.genai")
    def test_webp_mime_type_detection(self, mock_genai):
        """WebP MIMEタイプを検出して.webp拡張子で保存"""
        mock_client = Mock()
        mock_genai.Client.return_value = mock_client

        mock_image = Mock()
        mock_image.save = Mock()

        mock_inline_data = Mock()
        mock_inline_data.mime_type = "image/webp"

        mock_part = Mock()
        mock_part.text = None
        mock_part.inline_data = mock_inline_data
        mock_part.as_image.return_value = mock_image

        mock_response = Mock()
        mock_response.parts = [mock_part]
        mock_client.models.generate_content.return_value = mock_response

        with tempfile.TemporaryDirectory() as tmpdir:
            result = generate_image(
                prompt="テスト画像",
                resolution="2K",
                aspect_ratio="1:1",
                output_dir=tmpdir
            )

            assert result is not None
            assert result.endswith(".webp")
