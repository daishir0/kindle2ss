# Kindle Screenshot Automation Tool

This tool automatically takes screenshots of your Kindle screen and saves them as files.

**New!** GUI version with region selection and automatic page detection is now available!

※日本語のREADMEは下部にあります。

## Requirements

- Python3
- pip
- The following Python libraries
  - pyautogui
  - win32gui
  - win32ui
  - win32con
  - win32api
  - PIL
  - yomitoku (optional, for OCR functionality)
  - pytesseract (for GUI version page number detection)

**Note:** For GUI version, you also need to install Tesseract OCR:
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Install and add to PATH
- Install Japanese language data (jpn.traineddata)

## Usage

### GUI Version (Recommended)

The GUI version provides an easy-to-use interface with the following features:
- **Visual region selection**: Select capture area by dragging with mouse
- **Automatic page detection**: Detects page numbers and stops automatically at the last page
- **Live preview**: Preview the capture area before starting
- **OCR settings**: Configure Yomitoku OCR settings through the GUI

To use the GUI version:

1. Run the GUI application:

```
python kindle2ss_gui.py
```

2. Configure settings:
   - Click "領域を選択" (Select Region) to choose the capture area by dragging
   - Click "ページ番号領域を選択" (Select Page Number Region) to choose the area where page numbers appear
   - Enable "ページ番号を検出して自動停止" to automatically stop at the last page
   - Configure OCR settings if needed

3. Click "開始" (Start) button to begin capturing

4. The tool will automatically:
   - Capture screenshots
   - Detect page numbers
   - Stop at the last page
   - Run OCR processing (if enabled)

### CLI Version (Original)

1. Clone this repository.

```
git clone https://github.com/daishir0/kindle2ss.git
```

2. Install the required Python libraries.

```
pip install -r requirements.txt
```

Or install manually:

```
pip install pyautogui win32gui win32ui win32con win32api Pillow yomitoku
```

Note: `yomitoku` is optional. Install it only if you want to use OCR functionality.

3. Open a terminal or command prompt, and navigate to the repository directory.

```
cd kindle-screenshot
```

4. Navigate to the Kindle screen you want to screenshot.

5. Run the following command.

```
python kindle-screenshot.py
```

6. The screenshot is taken and saved in a folder named `output_YYYYMMDDHHmmss`.

7. Check the captured screenshot.

## Configuration

You can change the coordinates of the area to be screenshot, the interval between screenshots, the output folder name, and the initial characters of the output file name.

```python
# Coordinates of the area to be screenshot
left, top, width, height = (480, 120, 600, 870)
# Screenshot interval (seconds)
span = 1
# Output folder initial characters
h_foldername = "output"
# Output file initial characters
h_filename = "picture"
```

### Yomitoku OCR Configuration

You can enable/disable OCR processing and configure OCR settings:

```python
# Enable Yomitoku OCR processing (True: enabled, False: disabled)
enable_ocr = True
# OCR output format (md: Markdown, html: HTML, json: JSON, csv: CSV)
ocr_format = "md"
# Yomitoku lite mode (True: CPU optimized, False: normal mode)
ocr_lite_mode = False
```

When `enable_ocr` is set to `True`, the tool will automatically run Yomitoku OCR on all captured screenshots after the capture is complete. The OCR results will be saved in a folder named `{output_folder}_ocr`.

Also, the screenshot process will automatically stop if the same screen appears three times in a row. You can change this number.

```python
# Terminate when the same image appears 3 times
if same_cnt >= 3:
    break
```

## Precautions

- This tool only works in a Windows environment.
- When using this tool, use it only for Kindle screens.
- When using this tool, please comply with terms of use and copyright laws.

---

# Kindleスクリーンショット自動取得ツール

Kindleの画面を自動的にスクリーンショットし、ファイルとして保存するツールです。

**New!** 領域選択とページ番号自動検出機能を備えたGUI版が利用可能になりました！

## 必要なもの

- Python3
- pip
- 以下のPythonライブラリ
  - pyautogui
  - win32gui
  - win32ui
  - win32con
  - win32api
  - PIL
  - yomitoku (オプション、OCR機能を使用する場合)
  - pytesseract (GUI版のページ番号検出用)

**注意:** GUI版を使用する場合は、Tesseract OCRのインストールが必要です:
- ダウンロード: https://github.com/UB-Mannheim/tesseract/wiki
- インストール後、PATHに追加してください
- 日本語言語データ (jpn.traineddata) をインストールしてください

## 使い方

### GUI版（推奨）

GUI版では以下の機能を備えた使いやすいインターフェースを提供します:
- **ビジュアル領域選択**: マウスドラッグでキャプチャ領域を簡単に選択
- **自動ページ検出**: ページ番号を検出し、最終ページで自動停止
- **ライブプレビュー**: キャプチャ開始前に領域をプレビュー
- **OCR設定**: GUI上でYomitoku OCR設定を簡単に調整

GUI版の使い方:

1. GUIアプリケーションを起動:

```
python kindle2ss_gui.py
```

2. 設定を行う:
   - 「領域を選択」ボタンをクリックして、マウスドラッグでキャプチャ領域を選択
   - 「ページ番号領域を選択」ボタンをクリックして、ページ番号が表示される領域を選択
   - 「ページ番号を検出して自動停止」を有効化すると、最終ページで自動停止
   - 必要に応じてOCR設定を調整

3. 「開始」ボタンをクリックしてキャプチャを開始

4. ツールは自動的に以下を実行します:
   - スクリーンショットの取得
   - ページ番号の検出
   - 最終ページでの自動停止
   - OCR処理の実行（有効化している場合）

### CLI版（従来版）

1. 本リポジトリをクローンします。

```
git clone https://github.com/daishir0/kindle2ss.git
```

2. 必要なPythonライブラリをインストールします。

```
pip install -r requirements.txt
```

または手動でインストール:

```
pip install pyautogui win32gui win32ui win32con win32api Pillow yomitoku
```

注意: `yomitoku`はオプションです。OCR機能を使用する場合のみインストールしてください。

3. ターミナルまたはコマンドプロンプトを開き、リポジトリのディレクトリに移動します。

```
cd kindle-screenshot
```

4. スクリーンショットを取得したいKindleの画面に移動します。

5. 以下のコマンドを実行します。

```
python kindle-screenshot.py
```

6. スクリーンショットが取得され、`output_年月日時分秒`という名前のフォルダに保存されます。

7. 取得されたスクリーンショットを確認します。

## 設定

スクリーンショットを取得したい範囲の座標、スクショ間隔、出力フォルダ名、出力ファイル名の頭文字を変更することができます。

```python
# スクリーンショットを取得したい範囲の座標
left, top, width, height = (480, 120, 600, 870)
# スクショ間隔(秒)
span = 1
# 出力フォルダ頭文字
h_foldername = "output"
# 出力ファイル頭文字
h_filename = "picture"
```

### Yomitoku OCR設定

OCR処理の有効化/無効化とOCR設定を変更できます:

```python
# Yomitoku OCR処理を有効化 (True: 有効, False: 無効)
enable_ocr = True
# OCR出力形式 (md: Markdown, html: HTML, json: JSON, csv: CSV)
ocr_format = "md"
# Yomitoku軽量モード (True: CPU最適化, False: 通常モード)
ocr_lite_mode = False
```

`enable_ocr`を`True`に設定すると、スクリーンショット取得完了後に自動的にYomitoku OCRが実行されます。OCR結果は`{出力フォルダ}_ocr`という名前のフォルダに保存されます。

また、3ページ連続で同じ画面が出現した場合に自動的にスクリーンショットを停止するようになっています。この回数を変更することができます。

```python
# 3回同じ画像が出現した場合は終了
if same_cnt >= 3:
    break
```

## 注意事項

- このツールはWindows環境でのみ動作します。
- このツールを使用する際には、Kindleの画面に対してのみ使用してください。
- このツールを使用する際には、利用規約や著作権に関する法律を遵守してください。
