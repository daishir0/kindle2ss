import pyautogui
import win32gui
import win32ui
import win32con
import win32api
import time
import os
import datetime
from PIL import Image


# スクリーンショットを取得したい範囲の座標
left, top, width, height = (480, 120, 600, 870)
# スクショ間隔(秒)
span = 1
# 出力フォルダ頭文字
h_foldername = "output"
# 出力ファイル頭文字
h_filename = "picture"

# ５秒の間に、スクショしたいkindleの画面に移動
time.sleep(5)

# 出力フォルダ作成(フォルダ名：頭文字_年月日時分秒)
folder_name = h_foldername + "_" + str(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
os.mkdir(folder_name)

# スクショ処理
prev_img = None
same_cnt = 0
p = 0
while True:
    # アクティブなウィンドウのハンドルを取得する
    handle = win32gui.GetForegroundWindow()
    # デバイスコンテキストを作成する
    hwindc = win32gui.GetWindowDC(handle)
    srcdc = win32ui.CreateDCFromHandle(hwindc)
    memdc = srcdc.CreateCompatibleDC()
    # ビットマップオブジェクトを作成する
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(srcdc, width, height)
    memdc.SelectObject(bmp)
    # スクリーンショットを取得する
    memdc.BitBlt((0, 0), (width, height), srcdc, (left, top), win32con.SRCCOPY)
    # ビットマップを画像に変換する
    bmpinfo = bmp.GetInfo()
    bmpstr = bmp.GetBitmapBits(True)
    s = Image.frombuffer(
        "RGB",
        (bmpinfo["bmWidth"], bmpinfo["bmHeight"]),
        bmpstr,
        "raw",
        "BGRX",
        0,
        1,
    )
    # デバイスコンテキストを解放する
    srcdc.DeleteDC()
    memdc.DeleteDC()
    win32gui.ReleaseDC(handle, hwindc)
    win32gui.DeleteObject(bmp.GetHandle())

    p = p + 1
    # 前回の画像と同じか判定
    if prev_img is None or not s.tobytes() == prev_img.tobytes():
        # 前回の画像と異なる場合はスクリーンショットを保存
        out_filename = h_filename + "_" + str(p).zfill(4) + '.png'
        s.save(folder_name + "/" + out_filename)
        prev_img = s
        same_cnt = 0
        # 次のページ
        pyautogui.keyDown('left')
        # 画面の動作待ち
        time.sleep(span)
    else:
        # 前回の画像と同じ場合はカウンタを増やす
        same_cnt += 1

    # 3回同じ画像が出現した場合は終了
    if same_cnt >= 3:
        break

    # 処理中のページ番号を画面に出力
    print(f"Processing page {p}")
