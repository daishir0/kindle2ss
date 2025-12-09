import sys
import os
import time
import datetime
import subprocess
import threading
import re
from typing import Optional, Tuple

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSpinBox, QLineEdit, QCheckBox, QComboBox,
    QGroupBox, QProgressBar, QMessageBox, QTextEdit, QSplitter
)
from PySide6.QtCore import Qt, QTimer, Signal, QThread, QRect
from PySide6.QtGui import QPixmap, QImage, QPainter, QPen, QColor, QFont

import pyautogui
import win32gui
import win32ui
import win32con
import win32api
from PIL import Image
import pytesseract


class RegionSelectorWindow(QWidget):
    """領域選択用のオーバーレイウィンドウ"""
    region_selected = Signal(int, int, int, int)

    def __init__(self):
        super().__init__()
        self.start_pos = None
        self.current_pos = None
        self.setup_ui()

    def setup_ui(self):
        # フルスクリーン設定
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.showFullScreen()

        # カーソル設定
        self.setCursor(Qt.CrossCursor)

        # 背景色
        self.setStyleSheet("background-color: rgba(0, 0, 0, 100);")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))

        if self.start_pos and self.current_pos:
            # 選択領域を描画
            rect = QRect(self.start_pos, self.current_pos).normalized()

            # 選択領域をクリア
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.fillRect(rect, Qt.transparent)

            # 枠線を描画
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            pen = QPen(QColor(255, 0, 0), 3)
            painter.setPen(pen)
            painter.drawRect(rect)

            # 座標情報を表示
            info_text = f"領域: {rect.x()}, {rect.y()} - {rect.width()}x{rect.height()}"
            painter.setPen(QColor(255, 255, 255))
            font = QFont("Arial", 12, QFont.Bold)
            painter.setFont(font)
            painter.drawText(20, 30, info_text)

        # ヘルプテキスト
        painter.setPen(QColor(255, 255, 255))
        font = QFont("Arial", 14, QFont.Bold)
        painter.setFont(font)
        help_text = "マウスをドラッグして領域を選択してください (ESCでキャンセル)"
        text_rect = painter.fontMetrics().boundingRect(help_text)
        x = (self.width() - text_rect.width()) // 2
        painter.drawText(x, 60, help_text)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_pos = event.pos()
            self.current_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.start_pos:
            self.current_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.start_pos:
            rect = QRect(self.start_pos, self.current_pos).normalized()
            self.region_selected.emit(rect.x(), rect.y(), rect.width(), rect.height())
            self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()


class CaptureThread(QThread):
    """キャプチャ処理スレッド"""
    status_updated = Signal(str)
    progress_updated = Signal(str)
    capture_completed = Signal(str, int)
    error_occurred = Signal(str)

    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.is_running = True

    def run(self):
        try:
            # 5秒待機
            for i in range(5, 0, -1):
                if not self.is_running:
                    return
                self.status_updated.emit(f"開始まで {i} 秒...")
                time.sleep(1)

            # 出力フォルダ作成
            folder_name = (self.settings['folder_prefix'] + "_" +
                          datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
            os.mkdir(folder_name)

            self.status_updated.emit(f"キャプチャ中... フォルダ: {folder_name}")

            prev_img = None
            same_cnt = 0
            page_count = 0
            total_pages = None

            while self.is_running:
                # スクリーンショット取得
                img = self.capture_screenshot()
                if img is None:
                    break

                page_count += 1

                # 画像が前回と異なる場合のみ保存
                if prev_img is None or not img.tobytes() == prev_img.tobytes():
                    filename = f"picture_{str(page_count).zfill(4)}.png"
                    img.save(os.path.join(folder_name, filename))
                    prev_img = img
                    same_cnt = 0

                    # ページ番号検出
                    if self.settings['auto_stop']:
                        current_page, detected_total = self.detect_page_number()
                        if detected_total:
                            total_pages = detected_total

                        if current_page and total_pages:
                            progress = f"ページ {current_page}/{total_pages} - {page_count} 枚キャプチャ済み"
                            self.progress_updated.emit(progress)

                            # 最終ページに到達
                            if current_page >= total_pages:
                                self.status_updated.emit("最終ページに到達しました")
                                break
                        else:
                            self.progress_updated.emit(f"{page_count} 枚キャプチャ済み")
                    else:
                        self.progress_updated.emit(f"{page_count} 枚キャプチャ済み")

                    # 次のページへ
                    pyautogui.keyDown('left')
                    time.sleep(self.settings['interval'])
                else:
                    same_cnt += 1

                # 3回同じ画像が出現したら終了
                if same_cnt >= 3:
                    self.status_updated.emit("同じ画面が3回連続で検出されました")
                    break

            # キャプチャ完了
            self.capture_completed.emit(folder_name, page_count)

        except Exception as e:
            self.error_occurred.emit(str(e))

    def capture_screenshot(self) -> Optional[Image.Image]:
        """スクリーンショットを取得"""
        try:
            region = self.settings['region']
            handle = win32gui.GetForegroundWindow()
            hwindc = win32gui.GetWindowDC(handle)
            srcdc = win32ui.CreateDCFromHandle(hwindc)
            memdc = srcdc.CreateCompatibleDC()

            bmp = win32ui.CreateBitmap()
            bmp.CreateCompatibleBitmap(srcdc, region['width'], region['height'])
            memdc.SelectObject(bmp)

            memdc.BitBlt((0, 0), (region['width'], region['height']),
                        srcdc, (region['left'], region['top']), win32con.SRCCOPY)

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

            return img

        except Exception as e:
            print(f"スクリーンショット取得エラー: {e}")
            return None

    def detect_page_number(self) -> Tuple[Optional[int], Optional[int]]:
        """ページ番号を検出"""
        try:
            page_region = self.settings['page_region']
            handle = win32gui.GetForegroundWindow()
            hwindc = win32gui.GetWindowDC(handle)
            srcdc = win32ui.CreateDCFromHandle(hwindc)
            memdc = srcdc.CreateCompatibleDC()

            bmp = win32ui.CreateBitmap()
            bmp.CreateCompatibleBitmap(srcdc, page_region['width'], page_region['height'])
            memdc.SelectObject(bmp)

            memdc.BitBlt((0, 0), (page_region['width'], page_region['height']),
                        srcdc, (page_region['left'], page_region['top']), win32con.SRCCOPY)

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

            # ページ番号パターンマッチング
            patterns = [
                r'(\d+)/(\d+)',
                r'(\d+)\s*ページ',
                r'位置No\.\s*(\d+)',
            ]

            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    if len(match.groups()) >= 2:
                        return int(match.group(1)), int(match.group(2))
                    else:
                        return int(match.group(1)), None

            return None, None

        except Exception as e:
            print(f"ページ番号検出エラー: {e}")
            return None, None

    def stop(self):
        """スレッド停止"""
        self.is_running = False


class OCRThread(QThread):
    """OCR処理スレッド"""
    status_updated = Signal(str)
    ocr_completed = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, folder_name, settings):
        super().__init__()
        self.folder_name = folder_name
        self.settings = settings

    def run(self):
        try:
            self.status_updated.emit("Yomitoku OCR処理中...")
            ocr_output_dir = self.folder_name + "_ocr"

            cmd = ["yomitoku", self.folder_name, "-f", self.settings['ocr_format'],
                  "-o", ocr_output_dir, "-v", "--figure"]

            if self.settings['ocr_lite']:
                cmd.extend(["--lite", "-d", "cpu"])

            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            self.ocr_completed.emit(ocr_output_dir)

        except subprocess.CalledProcessError as e:
            self.error_occurred.emit(f"OCRエラー: {e.stderr}")
        except FileNotFoundError:
            self.error_occurred.emit("エラー: yomitokuがインストールされていません")
        except Exception as e:
            self.error_occurred.emit(str(e))


class MainWindow(QMainWindow):
    """メインウィンドウ"""

    def __init__(self):
        super().__init__()
        self.region = {"left": 480, "top": 120, "width": 600, "height": 870}
        self.page_region = {"left": 480, "top": 750, "width": 600, "height": 50}
        self.capture_thread = None
        self.ocr_thread = None
        self.preview_pixmap = None

        self.setup_ui()
        self.apply_stylesheet()

    def setup_ui(self):
        self.setWindowTitle("Kindle Screenshot Tool - Qt Edition")
        self.setMinimumSize(800, 900)

        # 中央ウィジェット
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # タイトル
        title = QLabel("Kindle Screenshot Tool")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; padding: 10px;")
        main_layout.addWidget(title)

        # スプリッター（左：設定、右：プレビュー）
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter, 1)

        # 左側：設定パネル
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(10)

        # キャプチャ領域設定
        region_group = self.create_region_group()
        left_layout.addWidget(region_group)

        # ページ番号検出設定
        page_group = self.create_page_detection_group()
        left_layout.addWidget(page_group)

        # キャプチャ設定
        capture_group = self.create_capture_settings_group()
        left_layout.addWidget(capture_group)

        # OCR設定
        ocr_group = self.create_ocr_settings_group()
        left_layout.addWidget(ocr_group)

        left_layout.addStretch()
        splitter.addWidget(left_widget)

        # 右側：プレビューとログ
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(10)

        # プレビュー
        preview_group = self.create_preview_group()
        right_layout.addWidget(preview_group, 2)

        # ログ
        log_group = self.create_log_group()
        right_layout.addWidget(log_group, 1)

        splitter.addWidget(right_widget)
        splitter.setSizes([400, 400])

        # ステータスバー
        self.status_label = QLabel("待機中")
        self.status_label.setStyleSheet("font-size: 14px; padding: 5px;")
        main_layout.addWidget(self.status_label)

        # プログレスバー
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMaximum(0)
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # 制御ボタン
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.start_btn = QPushButton("開始")
        self.start_btn.setMinimumHeight(50)
        self.start_btn.clicked.connect(self.start_capture)
        button_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("停止")
        self.stop_btn.setMinimumHeight(50)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_capture)
        button_layout.addWidget(self.stop_btn)

        main_layout.addLayout(button_layout)

    def create_region_group(self) -> QGroupBox:
        """キャプチャ領域設定グループ"""
        group = QGroupBox("キャプチャ領域設定")
        layout = QVBoxLayout()

        self.region_label = QLabel(self.get_region_text())
        self.region_label.setStyleSheet("font-size: 11px; padding: 5px;")
        layout.addWidget(self.region_label)

        select_btn = QPushButton("領域を選択")
        select_btn.clicked.connect(self.select_region)
        layout.addWidget(select_btn)

        group.setLayout(layout)
        return group

    def create_page_detection_group(self) -> QGroupBox:
        """ページ番号検出設定グループ"""
        group = QGroupBox("ページ番号検出設定")
        layout = QVBoxLayout()

        self.auto_stop_check = QCheckBox("ページ番号を検出して自動停止")
        self.auto_stop_check.setChecked(True)
        layout.addWidget(self.auto_stop_check)

        self.page_region_label = QLabel(self.get_page_region_text())
        self.page_region_label.setStyleSheet("font-size: 10px; padding: 5px;")
        layout.addWidget(self.page_region_label)

        page_select_btn = QPushButton("ページ番号領域を選択")
        page_select_btn.clicked.connect(self.select_page_region)
        layout.addWidget(page_select_btn)

        group.setLayout(layout)
        return group

    def create_capture_settings_group(self) -> QGroupBox:
        """キャプチャ設定グループ"""
        group = QGroupBox("キャプチャ設定")
        layout = QVBoxLayout()

        # スクショ間隔
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("スクショ間隔 (秒):"))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 10)
        self.interval_spin.setValue(1)
        interval_layout.addWidget(self.interval_spin)
        interval_layout.addStretch()
        layout.addLayout(interval_layout)

        # 出力フォルダ
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(QLabel("出力フォルダ名:"))
        self.folder_edit = QLineEdit("output")
        folder_layout.addWidget(self.folder_edit)
        layout.addLayout(folder_layout)

        group.setLayout(layout)
        return group

    def create_ocr_settings_group(self) -> QGroupBox:
        """OCR設定グループ"""
        group = QGroupBox("Yomitoku OCR設定")
        layout = QVBoxLayout()

        self.enable_ocr_check = QCheckBox("OCR処理を有効化")
        self.enable_ocr_check.setChecked(True)
        layout.addWidget(self.enable_ocr_check)

        # OCR形式
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("出力形式:"))
        self.ocr_format_combo = QComboBox()
        self.ocr_format_combo.addItems(["md", "html", "json", "csv"])
        format_layout.addWidget(self.ocr_format_combo)
        format_layout.addStretch()
        layout.addLayout(format_layout)

        # 軽量モード
        self.lite_mode_check = QCheckBox("軽量モード (CPU最適化)")
        layout.addWidget(self.lite_mode_check)

        group.setLayout(layout)
        return group

    def create_preview_group(self) -> QGroupBox:
        """プレビューグループ"""
        group = QGroupBox("プレビュー")
        layout = QVBoxLayout()

        self.preview_label = QLabel("プレビューはキャプチャ開始後に表示されます")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(400, 300)
        self.preview_label.setStyleSheet("background-color: #ecf0f1; border: 1px solid #bdc3c7;")
        layout.addWidget(self.preview_label)

        preview_btn = QPushButton("プレビューを更新")
        preview_btn.clicked.connect(self.update_preview)
        layout.addWidget(preview_btn)

        group.setLayout(layout)
        return group

    def create_log_group(self) -> QGroupBox:
        """ロググループ"""
        group = QGroupBox("ログ")
        layout = QVBoxLayout()

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        layout.addWidget(self.log_text)

        group.setLayout(layout)
        return group

    def apply_stylesheet(self):
        """スタイルシート適用"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f6fa;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #2c3e50;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
            QLineEdit, QSpinBox, QComboBox {
                padding: 5px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox {
                spacing: 5px;
            }
            QProgressBar {
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
            }
        """)

    def get_region_text(self) -> str:
        """領域テキスト取得"""
        return (f"左: {self.region['left']}, 上: {self.region['top']}, "
                f"幅: {self.region['width']}, 高さ: {self.region['height']}")

    def get_page_region_text(self) -> str:
        """ページ領域テキスト取得"""
        return (f"検出領域: 左: {self.page_region['left']}, 上: {self.page_region['top']}, "
                f"幅: {self.page_region['width']}, 高さ: {self.page_region['height']}")

    def select_region(self):
        """領域選択"""
        selector = RegionSelectorWindow()
        selector.region_selected.connect(self.on_region_selected)
        selector.show()

    def on_region_selected(self, left, top, width, height):
        """領域選択完了"""
        self.region = {"left": left, "top": top, "width": width, "height": height}
        self.region_label.setText(self.get_region_text())
        self.log("領域が設定されました")
        QMessageBox.information(self, "完了", "領域が設定されました")

    def select_page_region(self):
        """ページ番号領域選択"""
        selector = RegionSelectorWindow()
        selector.region_selected.connect(self.on_page_region_selected)
        selector.show()

    def on_page_region_selected(self, left, top, width, height):
        """ページ番号領域選択完了"""
        self.page_region = {"left": left, "top": top, "width": width, "height": height}
        self.page_region_label.setText(self.get_page_region_text())
        self.log("ページ番号検出領域が設定されました")
        QMessageBox.information(self, "完了", "ページ番号検出領域が設定されました")

    def update_preview(self):
        """プレビュー更新"""
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

            # QPixmapに変換
            img_rgb = img.convert("RGB")
            data = img_rgb.tobytes("raw", "RGB")
            qimage = QImage(data, img_rgb.width, img_rgb.height, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimage)

            # プレビュー表示用にスケール
            scaled_pixmap = pixmap.scaled(
                self.preview_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.preview_label.setPixmap(scaled_pixmap)
            self.log("プレビューを更新しました")

        except Exception as e:
            QMessageBox.critical(self, "エラー", f"プレビュー更新エラー: {e}")
            self.log(f"エラー: {e}")

    def start_capture(self):
        """キャプチャ開始"""
        if self.capture_thread and self.capture_thread.isRunning():
            return

        # 設定を収集
        settings = {
            'region': self.region,
            'page_region': self.page_region,
            'auto_stop': self.auto_stop_check.isChecked(),
            'interval': self.interval_spin.value(),
            'folder_prefix': self.folder_edit.text(),
            'enable_ocr': self.enable_ocr_check.isChecked(),
            'ocr_format': self.ocr_format_combo.currentText(),
            'ocr_lite': self.lite_mode_check.isChecked(),
        }

        # スレッド開始
        self.capture_thread = CaptureThread(settings)
        self.capture_thread.status_updated.connect(self.update_status)
        self.capture_thread.progress_updated.connect(self.update_progress)
        self.capture_thread.capture_completed.connect(self.on_capture_completed)
        self.capture_thread.error_occurred.connect(self.on_error)
        self.capture_thread.start()

        # UI更新
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.log("キャプチャを開始しました")

    def stop_capture(self):
        """キャプチャ停止"""
        if self.capture_thread:
            self.capture_thread.stop()
            self.capture_thread.wait()
            self.update_status("停止しました")
            self.log("キャプチャを停止しました")
            self.reset_ui()

    def on_capture_completed(self, folder_name, page_count):
        """キャプチャ完了"""
        self.update_status(f"キャプチャ完了: {page_count} 枚保存")
        self.log(f"キャプチャ完了: {folder_name} に {page_count} 枚保存")

        # OCR処理
        if self.enable_ocr_check.isChecked():
            settings = {
                'ocr_format': self.ocr_format_combo.currentText(),
                'ocr_lite': self.lite_mode_check.isChecked(),
            }
            self.ocr_thread = OCRThread(folder_name, settings)
            self.ocr_thread.status_updated.connect(self.update_status)
            self.ocr_thread.ocr_completed.connect(self.on_ocr_completed)
            self.ocr_thread.error_occurred.connect(self.on_error)
            self.ocr_thread.start()
        else:
            self.reset_ui()

    def on_ocr_completed(self, output_dir):
        """OCR完了"""
        self.update_status(f"完了: OCR結果は {output_dir} に保存されました")
        self.log(f"OCR処理完了: {output_dir}")
        QMessageBox.information(self, "完了", f"すべての処理が完了しました\n結果: {output_dir}")
        self.reset_ui()

    def on_error(self, error_message):
        """エラー発生"""
        self.update_status(f"エラー: {error_message}")
        self.log(f"エラー: {error_message}")
        QMessageBox.critical(self, "エラー", error_message)
        self.reset_ui()

    def update_status(self, message):
        """ステータス更新"""
        self.status_label.setText(message)

    def update_progress(self, message):
        """進捗更新"""
        self.log(message)

    def log(self, message):
        """ログ追加"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")

    def reset_ui(self):
        """UI リセット"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)

    def closeEvent(self, event):
        """ウィンドウクローズイベント"""
        if self.capture_thread and self.capture_thread.isRunning():
            reply = QMessageBox.question(
                self,
                "確認",
                "キャプチャ処理が実行中です。終了しますか？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.stop_capture()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Kindle Screenshot Tool")
    app.setOrganizationName("Kindle2SS")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
