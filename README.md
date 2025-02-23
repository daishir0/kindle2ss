# Kindle Screenshot Automation Tool

This tool automatically takes screenshots of your Kindle screen and saves them as files.

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

## Usage

1. Clone this repository.

```
git clone https://github.com/daishir0/kindle2ss.git
```

2. Install the required Python libraries.

```
pip install pyautogui win32gui win32ui win32con win32api Pillow
```

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

## 使い方

1. 本リポジトリをクローンします。

```
git clone https://github.com/daishir0/kindle2ss.git
```

2. 必要なPythonライブラリをインストールします。

```
pip install pyautogui win32gui win32ui win32con win32api Pillow
```

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
