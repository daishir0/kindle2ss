# Kindle Screenshot Automation Tool

This tool automatically takes screenshots of your Kindle screen and saves them as files.

**New!** Qt 6.10 version with modern UI and enhanced features is now available!
- Modern, professional UI design
- Split-pane layout for better workspace management
- Real-time logging and status updates
- Thread-based processing for smooth performance

※日本語のREADMEは下部にあります。

## Requirements

- Python 3.10 or higher
- pip
- **PyTorch 2.5+ with CUDA 13.0** (for GPU acceleration) or CPU version
- The following Python libraries
  - pyautogui
  - pywin32
  - Pillow
  - yomitoku (optional, for OCR functionality)
  - pytesseract (for GUI version page number detection)
  - PySide6 >= 6.10.0 (for Qt GUI version)

**Note:** For GUI versions, you also need to install Tesseract OCR:
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Install and add to PATH
- Install Japanese language data (jpn.traineddata)

## Quick Start

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/daishir0/kindle2ss.git
   cd kindle2ss
   ```

2. **Install PyTorch (Required for Yomitoku OCR)**

   Choose based on your hardware:

   **GPU with CUDA 13.0:**
   ```bash
   pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu130
   ```

   **CPU only:**
   ```bash
   pip3 install torch torchvision
   ```

3. **Install other dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Tesseract OCR** (for page number detection)
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Install Japanese language pack

5. **Run the application**
   ```bash
   # Qt GUI (Recommended)
   python kindle2ss_qt.py

   # Tkinter GUI (Alternative)
   python kindle2ss_gui.py

   # CLI version
   python kindle2ss.py
   ```

## Usage

### Qt GUI Version (Recommended - Modern UI)

The Qt version provides a modern, professional interface built with Qt 6.10:
- **Modern UI design**: Professional look with custom styling and smooth animations
- **Split-pane layout**: Settings on left, preview and logs on right
- **Real-time logging**: Monitor all activities in dedicated log area
- **Thread-based processing**: Non-blocking UI for smooth user experience
- **Progress tracking**: Visual progress bar and detailed status updates

To use the Qt GUI version:

1. Run the Qt GUI application:

```
python kindle2ss_qt.py
```

2. Configure settings in the left panel:
   - **Capture Region**: Click "領域を選択" to visually select the area
   - **Page Detection**: Select page number area for automatic stopping
   - **Capture Settings**: Set interval and output folder
   - **OCR Settings**: Configure Yomitoku options

3. Monitor in the right panel:
   - **Preview**: See the capture area before starting
   - **Logs**: Watch real-time progress and status updates

4. Click "開始" (Start) to begin

### Tkinter GUI Version (Alternative)

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

2. Install PyTorch (required for Yomitoku OCR).

**For GPU users (CUDA 13.0):**
```
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu130
```

**For CPU-only users:**
```
pip3 install torch torchvision
```

3. Install other required Python libraries.

```
pip install -r requirements.txt
```

Or install manually:

```
pip install pyautogui pywin32 Pillow pytesseract PySide6 yomitoku
```

**Note:**
- PyTorch must be installed before yomitoku
- For GPU acceleration, ensure you have CUDA 13.0 or compatible version installed
- `yomitoku` is optional but recommended for OCR functionality

4. Open a terminal or command prompt, and navigate to the repository directory.

```
cd kindle2ss
```

5. Navigate to the Kindle screen you want to screenshot.

6. Run the following command.

```
python kindle2ss.py
```

7. The screenshot is taken and saved in a folder named `output_YYYYMMDDHHmmss`.

8. Check the captured screenshot.

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

**New!** Qt 6.10による最新のモダンUIを備えたバージョンが利用可能になりました！
- モダンでプロフェッショナルなUIデザイン
- スプリットペインレイアウトによる効率的な作業環境
- リアルタイムログとステータス更新
- スレッドベース処理によるスムーズなパフォーマンス

## 必要なもの

- Python 3.10 以上
- pip
- **PyTorch 2.5+ (CUDA 13.0対応版)** （GPU高速化の場合）またはCPU版
- 以下のPythonライブラリ
  - pyautogui
  - pywin32
  - Pillow
  - yomitoku (オプション、OCR機能を使用する場合)
  - pytesseract (GUI版のページ番号検出用)
  - PySide6 >= 6.10.0 (Qt GUI版用)

**注意:** GUI版を使用する場合は、Tesseract OCRのインストールが必要です:
- ダウンロード: https://github.com/UB-Mannheim/tesseract/wiki
- インストール後、PATHに追加してください
- 日本語言語データ (jpn.traineddata) をインストールしてください

## クイックスタート

### インストール手順

1. **リポジトリをクローン**
   ```bash
   git clone https://github.com/daishir0/kindle2ss.git
   cd kindle2ss
   ```

2. **PyTorchをインストール（Yomitoku OCRに必要）**

   ハードウェアに応じて選択:

   **CUDA 13.0対応GPUの場合:**
   ```bash
   pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu130
   ```

   **CPUのみの場合:**
   ```bash
   pip3 install torch torchvision
   ```

3. **その他の依存関係をインストール**
   ```bash
   pip install -r requirements.txt
   ```

4. **Tesseract OCRをインストール**（ページ番号検出用）
   - ダウンロード: https://github.com/UB-Mannheim/tesseract/wiki
   - 日本語言語パックをインストール

5. **アプリケーションを起動**
   ```bash
   # Qt GUI版（推奨）
   python kindle2ss_qt.py

   # Tkinter GUI版（代替）
   python kindle2ss_gui.py

   # CLI版
   python kindle2ss.py
   ```

## 使い方

### Qt GUI版（推奨 - モダンUI）

Qt版はQt 6.10を使用したモダンでプロフェッショナルなインターフェースを提供します:
- **モダンUIデザイン**: カスタムスタイリングとスムーズなアニメーション
- **スプリットペインレイアウト**: 左に設定、右にプレビューとログ
- **リアルタイムログ**: 専用ログエリアですべてのアクティビティを監視
- **スレッドベース処理**: ノンブロッキングUIでスムーズなユーザー体験
- **進捗トラッキング**: ビジュアルプログレスバーと詳細なステータス更新

Qt GUI版の使い方:

1. Qt GUIアプリケーションを起動:

```
python kindle2ss_qt.py
```

2. 左パネルで設定:
   - **キャプチャ領域**: 「領域を選択」をクリックして視覚的に選択
   - **ページ検出**: ページ番号領域を選択して自動停止を設定
   - **キャプチャ設定**: 間隔と出力フォルダを設定
   - **OCR設定**: Yomitokuオプションを構成

3. 右パネルで監視:
   - **プレビュー**: キャプチャ開始前に領域を確認
   - **ログ**: リアルタイムで進捗とステータスを確認

4. 「開始」ボタンをクリックして実行

### Tkinter GUI版（代替）

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

2. PyTorchをインストールします（Yomitoku OCRに必要）。

**GPU使用の場合 (CUDA 13.0):**
```
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu130
```

**CPU のみの場合:**
```
pip3 install torch torchvision
```

3. その他の必要なPythonライブラリをインストールします。

```
pip install -r requirements.txt
```

または手動でインストール:

```
pip install pyautogui pywin32 Pillow pytesseract PySide6 yomitoku
```

**注意:**
- PyTorchはyomitokuより先にインストールする必要があります
- GPU高速化を使用する場合は、CUDA 13.0または互換バージョンがインストールされていることを確認してください
- `yomitoku`はオプションですが、OCR機能のため推奨されます

4. ターミナルまたはコマンドプロンプトを開き、リポジトリのディレクトリに移動します。

```
cd kindle2ss
```

5. スクリーンショットを取得したいKindleの画面に移動します。

6. 以下のコマンドを実行します。

```
python kindle2ss.py
```

7. スクリーンショットが取得され、`output_年月日時分秒`という名前のフォルダに保存されます。

8. 取得されたスクリーンショットを確認します。

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
