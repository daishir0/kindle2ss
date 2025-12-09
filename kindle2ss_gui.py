import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pyautogui
import win32gui
import win32ui
import win32con
import win32api
import time
import os
import datetime
import subprocess
import threading
import re
from PIL import Image, ImageTk, ImageDraw
import pytesseract


class RegionSelector:
    """領域選択用のオーバーレイウィンドウ"""

    def __init__(self, callback):
        self.callback = callback
        self.start_x = None
        self.start_y = None
        self.rect = None

        # 全画面オーバーレイウィンドウ
        self.root = tk.Toplevel()
        self.root.attributes('-alpha', 0.3)
        self.root.configure(bg='gray')
        self.root.attributes('-topmost', True)

        # マルチモニター対応: 仮想スクリーンのサイズを取得
        # GetSystemMetrics を使用してすべてのモニターをカバーする領域を取得
        SM_XVIRTUALSCREEN = 76
        SM_YVIRTUALSCREEN = 77
        SM_CXVIRTUALSCREEN = 78
        SM_CYVIRTUALSCREEN = 79

        x = win32api.GetSystemMetrics(SM_XVIRTUALSCREEN)
        y = win32api.GetSystemMetrics(SM_YVIRTUALSCREEN)
        width = win32api.GetSystemMetrics(SM_CXVIRTUALSCREEN)
        height = win32api.GetSystemMetrics(SM_CYVIRTUALSCREEN)

        # ウィンドウをすべてのモニターをカバーするように設定
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.overrideredirect(True)

        # オフセットを保存（座標計算用）
        self.offset_x = x
        self.offset_y = y

        # キャンバス
        self.canvas = tk.Canvas(self.root, cursor="cross", bg='gray', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # イベントバインド
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Escape>", lambda e: self.cancel())

        # 説明ラベル
        label = tk.Label(self.root, text="マウスをドラッグして領域を選択してください (ESCでキャンセル)",
                        font=('Arial', 14), bg='gray', fg='white')
        label.pack(pady=20)

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def on_drag(self, event):
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, event.x, event.y,
            outline='red', width=3
        )

    def on_release(self, event):
        end_x = event.x
        end_y = event.y

        # 座標を正規化
        left = min(self.start_x, end_x)
        top = min(self.start_y, end_y)
        right = max(self.start_x, end_x)
        bottom = max(self.start_y, end_y)

        width = right - left
        height = bottom - top

        # マルチモニター環境のオフセットを適用
        left += self.offset_x
        top += self.offset_y

        self.root.destroy()
        self.callback(left, top, width, height)

    def cancel(self):
        self.root.destroy()


class KindleScreenshotGUI:
    """Kindle スクリーンショット GUI アプリケーション"""

    def __init__(self, root):
        self.root = root
        self.root.title("Kindle Screenshot Tool")
        self.root.geometry("600x700")

        self.is_running = False
        self.capture_thread = None

        # デフォルト設定
        self.region = {"left": 480, "top": 120, "width": 600, "height": 870}
        self.page_region = {"left": 480, "top": 750, "width": 600, "height": 50}  # ページ番号検出用

        self.create_widgets()

    def create_widgets(self):
        # タイトル
        title = tk.Label(self.root, text="Kindle Screenshot Tool", font=('Arial', 16, 'bold'))
        title.pack(pady=10)

        # === 領域設定セクション ===
        region_frame = ttk.LabelFrame(self.root, text="キャプチャ領域設定", padding=10)
        region_frame.pack(fill=tk.X, padx=10, pady=5)

        # 座標表示
        self.region_label = tk.Label(region_frame,
                                     text=f"左: {self.region['left']}, 上: {self.region['top']}, "
                                          f"幅: {self.region['width']}, 高さ: {self.region['height']}",
                                     font=('Arial', 10))
        self.region_label.pack()

        # 領域選択ボタン
        select_btn = ttk.Button(region_frame, text="領域を選択", command=self.select_region)
        select_btn.pack(pady=5)

        # === ページ番号検出設定 ===
        page_frame = ttk.LabelFrame(self.root, text="ページ番号検出設定", padding=10)
        page_frame.pack(fill=tk.X, padx=10, pady=5)

        self.auto_stop_var = tk.BooleanVar(value=True)
        auto_stop_check = ttk.Checkbutton(page_frame, text="ページ番号を検出して自動停止",
                                         variable=self.auto_stop_var)
        auto_stop_check.pack()

        # ページ番号検出領域
        self.page_region_label = tk.Label(page_frame,
                                         text=f"検出領域: 左: {self.page_region['left']}, 上: {self.page_region['top']}, "
                                              f"幅: {self.page_region['width']}, 高さ: {self.page_region['height']}",
                                         font=('Arial', 9))
        self.page_region_label.pack()

        page_select_btn = ttk.Button(page_frame, text="ページ番号領域を選択",
                                     command=self.select_page_region)
        page_select_btn.pack(pady=5)

        # === キャプチャ設定 ===
        capture_frame = ttk.LabelFrame(self.root, text="キャプチャ設定", padding=10)
        capture_frame.pack(fill=tk.X, padx=10, pady=5)

        # スクショ間隔
        interval_frame = tk.Frame(capture_frame)
        interval_frame.pack(fill=tk.X, pady=2)
        tk.Label(interval_frame, text="スクショ間隔 (秒):").pack(side=tk.LEFT)
        self.interval_var = tk.StringVar(value="1")
        interval_entry = ttk.Entry(interval_frame, textvariable=self.interval_var, width=10)
        interval_entry.pack(side=tk.LEFT, padx=5)

        # 出力フォルダ
        folder_frame = tk.Frame(capture_frame)
        folder_frame.pack(fill=tk.X, pady=2)
        tk.Label(folder_frame, text="出力フォルダ名:").pack(side=tk.LEFT)
        self.folder_var = tk.StringVar(value="output")
        folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_var, width=20)
        folder_entry.pack(side=tk.LEFT, padx=5)

        # === OCR設定 ===
        ocr_frame = ttk.LabelFrame(self.root, text="Yomitoku OCR設定", padding=10)
        ocr_frame.pack(fill=tk.X, padx=10, pady=5)

        self.enable_ocr_var = tk.BooleanVar(value=True)
        ocr_check = ttk.Checkbutton(ocr_frame, text="OCR処理を有効化",
                                   variable=self.enable_ocr_var)
        ocr_check.pack()

        # OCR形式
        format_frame = tk.Frame(ocr_frame)
        format_frame.pack(fill=tk.X, pady=2)
        tk.Label(format_frame, text="出力形式:").pack(side=tk.LEFT)
        self.ocr_format_var = tk.StringVar(value="pdf")
        format_combo = ttk.Combobox(format_frame, textvariable=self.ocr_format_var,
                                   values=["pdf", "md", "html", "json", "csv"], width=10, state="readonly")
        format_combo.pack(side=tk.LEFT, padx=5)

        # 軽量モード
        self.lite_mode_var = tk.BooleanVar(value=False)
        lite_check = ttk.Checkbutton(ocr_frame, text="軽量モード (CPU最適化)",
                                    variable=self.lite_mode_var)
        lite_check.pack()

        # === プレビュー ===
        preview_frame = ttk.LabelFrame(self.root, text="プレビュー", padding=10)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.preview_label = tk.Label(preview_frame, text="プレビューはキャプチャ開始後に表示されます",
                                     bg='lightgray', width=50, height=10)
        self.preview_label.pack(fill=tk.BOTH, expand=True)

        # プレビュー更新ボタン
        preview_btn = ttk.Button(preview_frame, text="プレビューを更新", command=self.update_preview)
        preview_btn.pack(pady=5)

        # === ステータス ===
        status_frame = tk.Frame(self.root)
        status_frame.pack(fill=tk.X, padx=10, pady=5)

        self.status_label = tk.Label(status_frame, text="待機中", font=('Arial', 10))
        self.status_label.pack()

        self.progress_label = tk.Label(status_frame, text="", font=('Arial', 9))
        self.progress_label.pack()

        # === 制御ボタン ===
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        self.start_btn = ttk.Button(control_frame, text="開始", command=self.start_capture,
                                   width=15)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(control_frame, text="停止", command=self.stop_capture,
                                  width=15, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

    def select_region(self):
        """キャプチャ領域を選択"""
        RegionSelector(self.on_region_selected)

    def on_region_selected(self, left, top, width, height):
        """領域選択完了時のコールバック"""
        self.region = {"left": left, "top": top, "width": width, "height": height}
        self.region_label.config(
            text=f"左: {left}, 上: {top}, 幅: {width}, 高さ: {height}"
        )
        messagebox.showinfo("完了", "領域が設定されました")

    def select_page_region(self):
        """ページ番号検出領域を選択"""
        RegionSelector(self.on_page_region_selected)

    def on_page_region_selected(self, left, top, width, height):
        """ページ番号領域選択完了時のコールバック"""
        self.page_region = {"left": left, "top": top, "width": width, "height": height}
        self.page_region_label.config(
            text=f"検出領域: 左: {left}, 上: {top}, 幅: {width}, 高さ: {height}"
        )
        messagebox.showinfo("完了", "ページ番号検出領域が設定されました")

    def update_preview(self):
        """プレビューを更新"""
        try:
            handle = win32gui.GetForegroundWindow()
            hwindc = win32gui.GetWindowDC(handle)
            srcdc = win32ui.CreateDCFromHandle(hwindc)
            memdc = srcdc.CreateCompatibleDC()

            bmp = win32ui.CreateBitmap()
            bmp.CreateCompatibleBitmap(srcdc, self.region['width'], self.region['height'])
            memdc.SelectObject(bmp)

            memdc.BitBlt((0, 0), (self.region['width'], self.region['height']),
                        srcdc, (self.region['left'], self.region['top']), win32con.SRCCOPY)

            bmpinfo = bmp.GetInfo()
            bmpstr = bmp.GetBitmapBits(True)
            img = Image.frombuffer(
                "RGB",
                (bmpinfo["bmWidth"], bmpinfo["bmHeight"]),
                bmpstr,
                "raw",
                "BGRX",
                0,
                1,
            )

            # クリーンアップ
            srcdc.DeleteDC()
            memdc.DeleteDC()
            win32gui.ReleaseDC(handle, hwindc)
            win32gui.DeleteObject(bmp.GetHandle())

            # プレビュー表示用にリサイズ
            img.thumbnail((400, 300), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.preview_label.config(image=photo, text="")
            self.preview_label.image = photo

        except Exception as e:
            messagebox.showerror("エラー", f"プレビュー更新エラー: {e}")

    def detect_page_number(self, handle):
        """ページ番号を検出"""
        try:
            hwindc = win32gui.GetWindowDC(handle)
            srcdc = win32ui.CreateDCFromHandle(hwindc)
            memdc = srcdc.CreateCompatibleDC()

            bmp = win32ui.CreateBitmap()
            bmp.CreateCompatibleBitmap(srcdc, self.page_region['width'], self.page_region['height'])
            memdc.SelectObject(bmp)

            memdc.BitBlt((0, 0), (self.page_region['width'], self.page_region['height']),
                        srcdc, (self.page_region['left'], self.page_region['top']), win32con.SRCCOPY)

            bmpinfo = bmp.GetInfo()
            bmpstr = bmp.GetBitmapBits(True)
            img = Image.frombuffer(
                "RGB",
                (bmpinfo["bmWidth"], bmpinfo["bmHeight"]),
                bmpstr,
                "raw",
                "BGRX",
                0,
                1,
            )

            # クリーンアップ
            srcdc.DeleteDC()
            memdc.DeleteDC()
            win32gui.ReleaseDC(handle, hwindc)
            win32gui.DeleteObject(bmp.GetHandle())

            # OCRでテキスト抽出
            text = pytesseract.image_to_string(img, lang='jpn')

            # ページ番号パターンマッチング: "XX/YY" or "XXページ" or "位置No. XX"
            patterns = [
                r'(\d+)/(\d+)',  # 58/385
                r'(\d+)\s*ページ',  # 58ページ
                r'位置No\.\s*(\d+)',  # 位置No. 750-4306
            ]

            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    if len(match.groups()) >= 2:
                        current = int(match.group(1))
                        total = int(match.group(2))
                        return current, total
                    else:
                        return int(match.group(1)), None

            return None, None

        except Exception as e:
            print(f"ページ番号検出エラー: {e}")
            return None, None

    def capture_process(self):
        """キャプチャ処理"""
        try:
            # 5秒待機
            for i in range(5, 0, -1):
                if not self.is_running:
                    return
                self.update_status(f"開始まで {i} 秒...")
                time.sleep(1)

            # 出力フォルダ作成
            folder_name = self.folder_var.get() + "_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            os.mkdir(folder_name)

            self.update_status(f"キャプチャ中... フォルダ: {folder_name}")

            prev_img = None
            same_cnt = 0
            page_count = 0
            total_pages = None

            while self.is_running:
                handle = win32gui.GetForegroundWindow()
                hwindc = win32gui.GetWindowDC(handle)
                srcdc = win32ui.CreateDCFromHandle(hwindc)
                memdc = srcdc.CreateCompatibleDC()

                bmp = win32ui.CreateBitmap()
                bmp.CreateCompatibleBitmap(srcdc, self.region['width'], self.region['height'])
                memdc.SelectObject(bmp)

                memdc.BitBlt((0, 0), (self.region['width'], self.region['height']),
                           srcdc, (self.region['left'], self.region['top']), win32con.SRCCOPY)

                bmpinfo = bmp.GetInfo()
                bmpstr = bmp.GetBitmapBits(True)
                img = Image.frombuffer(
                    "RGB",
                    (bmpinfo["bmWidth"], bmpinfo["bmHeight"]),
                    bmpstr,
                    "raw",
                    "BGRX",
                    0,
                    1,
                )

                # クリーンアップ
                srcdc.DeleteDC()
                memdc.DeleteDC()
                win32gui.ReleaseDC(handle, hwindc)
                win32gui.DeleteObject(bmp.GetHandle())

                page_count += 1

                # 画像が前回と異なる場合のみ保存
                if prev_img is None or not img.tobytes() == prev_img.tobytes():
                    filename = f"picture_{str(page_count).zfill(4)}.png"
                    img.save(os.path.join(folder_name, filename))
                    prev_img = img
                    same_cnt = 0

                    # ページ番号検出
                    if self.auto_stop_var.get():
                        current_page, detected_total = self.detect_page_number(handle)
                        if detected_total:
                            total_pages = detected_total

                        if current_page and total_pages:
                            progress = f"ページ {current_page}/{total_pages} - {page_count} 枚キャプチャ済み"
                            self.update_progress(progress)

                            # 最終ページに到達
                            if current_page >= total_pages:
                                self.update_status("最終ページに到達しました")
                                break
                        else:
                            self.update_progress(f"{page_count} 枚キャプチャ済み")
                    else:
                        self.update_progress(f"{page_count} 枚キャプチャ済み")

                    # 次のページへ
                    pyautogui.keyDown('left')
                    time.sleep(float(self.interval_var.get()))
                else:
                    same_cnt += 1

                # 3回同じ画像が出現したら終了
                if same_cnt >= 3:
                    self.update_status("同じ画面が3回連続で検出されました")
                    break

            # キャプチャ完了
            self.update_status(f"キャプチャ完了: {page_count} 枚保存")

            # OCR処理
            if self.enable_ocr_var.get():
                self.update_status("Yomitoku OCR処理中...")
                ocr_output_dir = folder_name + "_ocr"

                cmd = ["yomitoku", folder_name, "-f", self.ocr_format_var.get(),
                      "-o", ocr_output_dir, "-v", "--figure"]

                if self.lite_mode_var.get():
                    cmd.extend(["--lite", "-d", "cpu"])

                try:
                    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                    self.update_status(f"完了: OCR結果は {ocr_output_dir} に保存されました")
                except subprocess.CalledProcessError as e:
                    self.update_status(f"OCRエラー: {e.stderr}")
                except FileNotFoundError:
                    self.update_status("エラー: yomitokuがインストールされていません")
            else:
                self.update_status(f"完了: {folder_name} に保存されました")

        except Exception as e:
            self.update_status(f"エラー: {e}")
            messagebox.showerror("エラー", str(e))
        finally:
            self.is_running = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)

    def update_status(self, message):
        """ステータスを更新"""
        self.status_label.config(text=message)

    def update_progress(self, message):
        """進捗を更新"""
        self.progress_label.config(text=message)

    def start_capture(self):
        """キャプチャ開始"""
        if self.is_running:
            return

        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)

        self.capture_thread = threading.Thread(target=self.capture_process)
        self.capture_thread.daemon = True
        self.capture_thread.start()

    def stop_capture(self):
        """キャプチャ停止"""
        self.is_running = False
        self.update_status("停止中...")
        self.stop_btn.config(state=tk.DISABLED)


def main():
    root = tk.Tk()
    app = KindleScreenshotGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
