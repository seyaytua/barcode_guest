from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                                QPushButton, QLabel, QLineEdit, QGroupBox,
                                QMessageBox, QTextEdit, QComboBox, QRadioButton,
                                QButtonGroup, QFrame)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from core.database import VisitorDatabase
from core.barcode_reader import ScannerReaderThread
from gui.check_in_dialog import CheckInDialog
from gui.statistics_window import StatisticsWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("来場管理システム")
        self.setGeometry(100, 100, 1200, 700)
        
        self.db = VisitorDatabase()
        self.scanner_reader = None
        self.scanner_active = False
        self.current_mode = 'manual'
        
        self.init_ui()
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # タイトル
        title_label = QLabel("来場管理システム")
        title_font = QFont()
        title_font.setPointSize(28)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 読み取りモード選択
        mode_group = QGroupBox("読み取りモード")
        mode_layout = QHBoxLayout()
        
        self.mode_button_group = QButtonGroup()
        
        self.radio_manual = QRadioButton("手動入力")
        self.radio_manual.setChecked(True)
        self.radio_manual.toggled.connect(lambda: self.switch_mode('manual'))
        self.mode_button_group.addButton(self.radio_manual)
        mode_layout.addWidget(self.radio_manual)
        
        self.radio_scanner = QRadioButton("USBスキャナー")
        self.radio_scanner.toggled.connect(lambda: self.switch_mode('scanner'))
        self.mode_button_group.addButton(self.radio_scanner)
        mode_layout.addWidget(self.radio_scanner)
        
        mode_layout.addStretch()
        
        hint_label = QLabel("💡 推奨: USBバーコードスキャナーを使用すると高速で確実です")
        hint_label.setStyleSheet("QLabel { color: #2196F3; font-size: 11px; }")
        mode_layout.addWidget(hint_label)
        
        mode_group.setLayout(mode_layout)
        main_layout.addWidget(mode_group)
        
        # 統計情報（読み取りモードの下に配置）
        stats_group = QGroupBox("本日の来場状況")
        stats_layout = QHBoxLayout()
        
        self.lbl_today_total = QLabel("本日: 0人")
        self.lbl_today_total.setStyleSheet("QLabel { font-size: 20px; font-weight: bold; }")
        stats_layout.addWidget(self.lbl_today_total)
        
        stats_layout.addWidget(QLabel("|"))
        
        self.lbl_today_first = QLabel("初回: 0人")
        self.lbl_today_first.setStyleSheet("QLabel { font-size: 20px; color: #4CAF50; font-weight: bold; }")
        stats_layout.addWidget(self.lbl_today_first)
        
        stats_layout.addWidget(QLabel("|"))
        
        self.lbl_today_returning = QLabel("再来場: 0人")
        self.lbl_today_returning.setStyleSheet("QLabel { font-size: 20px; color: #2196F3; font-weight: bold; }")
        stats_layout.addWidget(self.lbl_today_returning)
        
        stats_layout.addStretch()
        
        btn_statistics = QPushButton("📊 詳細統計")
        btn_statistics.clicked.connect(self.show_statistics)
        btn_statistics.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                font-size: 14px;
                padding: 8px 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        stats_layout.addWidget(btn_statistics)
        
        stats_group.setLayout(stats_layout)
        main_layout.addWidget(stats_group)
        
        # スキャナー用大画面表示エリア
        self.scanner_display_group = QGroupBox("読み取り表示")
        scanner_display_layout = QVBoxLayout()
        scanner_display_layout.setSpacing(8)
        
        # 読み取ったバーコード表示
        self.lbl_scanned_barcode = QLabel("バーコードをスキャンしてください")
        self.lbl_scanned_barcode.setAlignment(Qt.AlignCenter)
        self.lbl_scanned_barcode.setStyleSheet("""
            QLabel {
                background-color: #f5f5f5;
                border: 3px solid #2196F3;
                border-radius: 10px;
                padding: 25px;
                font-size: 48px;
                font-weight: bold;
                color: #2196F3;
                min-height: 100px;
                max-height: 120px;
            }
        """)
        scanner_display_layout.addWidget(self.lbl_scanned_barcode)
        
        # 読み取った氏名表示
        self.lbl_scanned_name = QLabel("")
        self.lbl_scanned_name.setAlignment(Qt.AlignCenter)
        self.lbl_scanned_name.setStyleSheet("""
            QLabel {
                font-size: 64px;
                font-weight: bold;
                color: #333;
                padding: 15px;
                min-height: 90px;
                max-height: 110px;
            }
        """)
        scanner_display_layout.addWidget(self.lbl_scanned_name)
        
        # ステータス表示
        self.lbl_scanned_status = QLabel("")
        self.lbl_scanned_status.setAlignment(Qt.AlignCenter)
        self.lbl_scanned_status.setStyleSheet("""
            QLabel {
                font-size: 36px;
                font-weight: bold;
                padding: 12px;
                border-radius: 8px;
                min-height: 60px;
                max-height: 80px;
            }
        """)
        scanner_display_layout.addWidget(self.lbl_scanned_status)
        
        self.scanner_display_group.setLayout(scanner_display_layout)
        self.scanner_display_group.setVisible(False)
        main_layout.addWidget(self.scanner_display_group)
        
        # スキャナー設定
        self.scanner_group = QGroupBox("USBスキャナー設定")
        scanner_layout = QVBoxLayout()
        scanner_layout.setSpacing(8)
        
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("ポート:"))
        self.combo_port = QComboBox()
        self.combo_port.setMinimumWidth(400)
        port_layout.addWidget(self.combo_port)
        
        btn_refresh_ports = QPushButton("🔄 ポート更新")
        btn_refresh_ports.clicked.connect(self.refresh_ports)
        port_layout.addWidget(btn_refresh_ports)
        port_layout.addStretch()
        scanner_layout.addLayout(port_layout)
        
        scanner_control_layout = QHBoxLayout()
        self.btn_start_scanner = QPushButton("スキャナー起動")
        self.btn_start_scanner.clicked.connect(self.toggle_scanner)
        self.btn_start_scanner.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        scanner_control_layout.addWidget(self.btn_start_scanner)
        scanner_control_layout.addStretch()
        scanner_layout.addLayout(scanner_control_layout)
        
        self.lbl_scanner_status = QLabel("スキャナー: 停止中")
        self.lbl_scanner_status.setStyleSheet("QLabel { font-weight: bold; font-size: 14px; }")
        scanner_layout.addWidget(self.lbl_scanner_status)
        
        scanner_hint = QLabel("ℹ️ USBバーコードスキャナーを接続してポートを更新してください")
        scanner_hint.setStyleSheet("QLabel { color: #757575; font-size: 11px; }")
        scanner_layout.addWidget(scanner_hint)
        
        self.scanner_group.setLayout(scanner_layout)
        self.scanner_group.setVisible(False)
        main_layout.addWidget(self.scanner_group)
        
        # 手動入力
        self.manual_group = QGroupBox("手動入力")
        manual_layout = QVBoxLayout()
        manual_layout.setSpacing(5)
        
        input_row = QHBoxLayout()
        input_row.addWidget(QLabel("バーコード:"))
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("バーコードを入力してEnter")
        self.barcode_input.returnPressed.connect(self.manual_check_in)
        self.barcode_input.setStyleSheet("QLineEdit { font-size: 14px; padding: 8px; }")
        input_row.addWidget(self.barcode_input)
        
        input_row.addWidget(QLabel("氏名:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("氏名を入力（新規のみ）")
        self.name_input.setStyleSheet("QLineEdit { font-size: 14px; padding: 8px; }")
        input_row.addWidget(self.name_input)
        
        btn_manual_checkin = QPushButton("✓ チェックイン")
        btn_manual_checkin.clicked.connect(self.manual_check_in)
        btn_manual_checkin.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-size: 14px;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        input_row.addWidget(btn_manual_checkin)
        
        manual_layout.addLayout(input_row)
        
        manual_hint = QLabel("ℹ️ 既存の来場者はバーコードのみで自動認識されます")
        manual_hint.setStyleSheet("QLabel { color: #757575; font-size: 11px; }")
        manual_layout.addWidget(manual_hint)
        
        self.manual_group.setLayout(manual_layout)
        main_layout.addWidget(self.manual_group)
        
        # ログ表示
        log_group = QGroupBox("来場ログ")
        log_layout = QVBoxLayout()
        log_layout.setContentsMargins(5, 5, 5, 5)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(120)
        self.log_text.setStyleSheet("QTextEdit { font-family: monospace; font-size: 12px; }")
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)
        
        # 初期化
        self.refresh_ports()
        
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_stats)
        self.stats_timer.start(5000)
        
        self.update_stats()
        self.add_log("システムを起動しました")
        self.barcode_input.setFocus()
    
    def switch_mode(self, mode: str):
        if self.current_mode == 'scanner' and self.scanner_active:
            self.stop_scanner()
        
        self.current_mode = mode
        self.scanner_group.setVisible(mode == 'scanner')
        self.scanner_display_group.setVisible(mode == 'scanner')
        self.manual_group.setVisible(mode == 'manual')
        
        mode_names = {'manual': '手動入力', 'scanner': 'USBスキャナー'}
        self.add_log(f"モード切り替え: {mode_names.get(mode, mode)}")
        
        if mode == 'manual':
            self.barcode_input.setFocus()
        elif mode == 'scanner':
            self.lbl_scanned_barcode.setText("バーコードをスキャンしてください")
            self.lbl_scanned_name.setText("")
            self.lbl_scanned_status.setText("")
    
    def refresh_ports(self):
        self.combo_port.clear()
        ports = ScannerReaderThread.list_available_ports()
        
        if ports:
            for port, description in ports:
                self.combo_port.addItem(f"{port} - {description}", port)
            if hasattr(self, 'log_text'):
                self.add_log(f"シリアルポート: {len(ports)}個検出")
        else:
            self.combo_port.addItem("利用可能なポートがありません", None)
            if hasattr(self, 'log_text'):
                self.add_log("シリアルポートが見つかりません")
    
    def toggle_scanner(self):
        if not self.scanner_active:
            self.start_scanner()
        else:
            self.stop_scanner()
    
    def start_scanner(self):
        selected_port = self.combo_port.currentData()
        if not selected_port:
            QMessageBox.warning(self, "エラー", "有効なポートを選択してください")
            return
        
        self.scanner_reader = ScannerReaderThread(port=selected_port)
        self.scanner_reader.barcode_detected.connect(self.on_barcode_detected)
        self.scanner_reader.error_occurred.connect(self.on_scanner_error)
        self.scanner_reader.start()
        
        self.scanner_active = True
        self.btn_start_scanner.setText("⏹ スキャナー停止")
        self.btn_start_scanner.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-size: 14px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        self.lbl_scanner_status.setText(f"スキャナー: 起動中 ({selected_port})")
        self.lbl_scanner_status.setStyleSheet("QLabel { font-weight: bold; font-size: 14px; color: #4CAF50; }")
        self.add_log(f"スキャナーを起動: {selected_port}")
        
        self.lbl_scanned_barcode.setText("バーコードをスキャンしてください")
        self.lbl_scanned_barcode.setStyleSheet("""
            QLabel {
                background-color: #f5f5f5;
                border: 3px solid #2196F3;
                border-radius: 10px;
                padding: 25px;
                font-size: 48px;
                font-weight: bold;
                color: #2196F3;
                min-height: 100px;
                max-height: 120px;
            }
        """)
        self.lbl_scanned_name.setText("")
        self.lbl_scanned_status.setText("")
    
    def stop_scanner(self):
        if self.scanner_reader:
            self.scanner_reader.stop()
            self.scanner_reader = None
        
        self.scanner_active = False
        self.btn_start_scanner.setText("スキャナー起動")
        self.btn_start_scanner.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.lbl_scanner_status.setText("スキャナー: 停止中")
        self.lbl_scanner_status.setStyleSheet("QLabel { font-weight: bold; font-size: 14px; }")
        self.add_log("スキャナーを停止しました")
    
    def on_scanner_error(self, error_message: str):
        self.add_log(f"❌ スキャナーエラー: {error_message}")
        QMessageBox.warning(self, "スキャナーエラー", error_message)
        if self.scanner_active:
            self.stop_scanner()
    
    def on_barcode_detected(self, barcode: str):
        self.lbl_scanned_barcode.setText(f"ID: {barcode}")
        self.lbl_scanned_barcode.setStyleSheet("""
            QLabel {
                background-color: #E3F2FD;
                border: 3px solid #2196F3;
                border-radius: 10px;
                padding: 25px;
                font-size: 48px;
                font-weight: bold;
                color: #1976D2;
                min-height: 100px;
                max-height: 120px;
            }
        """)
        
        visitor_info = self.db.get_visitor_info(barcode)
        
        if visitor_info:
            name = visitor_info['name']
            self.process_check_in_with_display(barcode, name)
        else:
            self.lbl_scanned_name.setText("新規来場者")
            self.lbl_scanned_name.setStyleSheet("""
                QLabel {
                    font-size: 64px;
                    font-weight: bold;
                    color: #FF9800;
                    padding: 15px;
                    min-height: 90px;
                    max-height: 110px;
                }
            """)
            self.lbl_scanned_status.setText("⚠️ スタッフに氏名を伝えてください")
            self.lbl_scanned_status.setStyleSheet("""
                QLabel {
                    background-color: #FFF3E0;
                    font-size: 36px;
                    font-weight: bold;
                    color: #F57C00;
                    padding: 12px;
                    border-radius: 8px;
                    min-height: 60px;
                    max-height: 80px;
                }
            """)
            
            self.add_log(f"⚠️ 新規来場者 ({barcode}) - 名前を入力してください")
            QTimer.singleShot(3000, self.clear_scanner_display)
            
            self.radio_manual.setChecked(True)
            self.barcode_input.setText(barcode)
            self.name_input.setFocus()
    
    def process_check_in_with_display(self, barcode: str, name: str):
        try:
            is_first_visit, visit_count, last_visit = self.db.check_in(barcode, name)
            
            self.lbl_scanned_name.setText(name)
            self.lbl_scanned_name.setStyleSheet("""
                QLabel {
                    font-size: 72px;
                    font-weight: bold;
                    color: #333;
                    padding: 15px;
                    min-height: 90px;
                    max-height: 110px;
                }
            """)
            
            if is_first_visit:
                status_text = "🎉 初回来場 - ようこそ！"
                status_style = """
                    QLabel {
                        background-color: #C8E6C9;
                        font-size: 42px;
                        font-weight: bold;
                        color: #2E7D32;
                        padding: 12px;
                        border-radius: 8px;
                        min-height: 60px;
                        max-height: 80px;
                    }
                """
            else:
                status_text = f"🔄 {visit_count}回目の来場 - お帰りなさい！"
                status_style = """
                    QLabel {
                        background-color: #BBDEFB;
                        font-size: 42px;
                        font-weight: bold;
                        color: #1565C0;
                        padding: 12px;
                        border-radius: 8px;
                        min-height: 60px;
                        max-height: 80px;
                    }
                """
            
            self.lbl_scanned_status.setText(status_text)
            self.lbl_scanned_status.setStyleSheet(status_style)
            
            status = "初回来場" if is_first_visit else f"{visit_count}回目の来場"
            status_icon = "🎉" if is_first_visit else "🔄"
            self.add_log(f"{status_icon} {name} ({barcode}) - {status}")
            
            self.update_stats()
            QTimer.singleShot(5000, self.clear_scanner_display)
            
        except Exception as e:
            self.lbl_scanned_name.setText("エラー")
            self.lbl_scanned_status.setText(f"❌ {str(e)}")
            self.lbl_scanned_status.setStyleSheet("""
                QLabel {
                    background-color: #FFCDD2;
                    font-size: 36px;
                    font-weight: bold;
                    color: #C62828;
                    padding: 12px;
                    border-radius: 8px;
                    min-height: 60px;
                    max-height: 80px;
                }
            """)
            self.add_log(f"❌ エラー: {str(e)}")
            QTimer.singleShot(3000, self.clear_scanner_display)
    
    def clear_scanner_display(self):
        if self.current_mode == 'scanner':
            self.lbl_scanned_barcode.setText("バーコードをスキャンしてください")
            self.lbl_scanned_barcode.setStyleSheet("""
                QLabel {
                    background-color: #f5f5f5;
                    border: 3px solid #2196F3;
                    border-radius: 10px;
                    padding: 25px;
                    font-size: 48px;
                    font-weight: bold;
                    color: #2196F3;
                    min-height: 100px;
                    max-height: 120px;
                }
            """)
            self.lbl_scanned_name.setText("")
            self.lbl_scanned_status.setText("")
    
    def manual_check_in(self):
        barcode = self.barcode_input.text().strip()
        name = self.name_input.text().strip()
        
        if not barcode:
            QMessageBox.warning(self, "入力エラー", "バーコードを入力してください")
            self.barcode_input.setFocus()
            return
        
        visitor_info = self.db.get_visitor_info(barcode)
        if visitor_info:
            name = visitor_info['name']
        elif not name:
            QMessageBox.warning(self, "入力エラー", "新規来場者の場合、氏名を入力してください")
            self.name_input.setFocus()
            return
        
        self.process_check_in(barcode, name)
        self.barcode_input.clear()
        self.name_input.clear()
        self.barcode_input.setFocus()
    
    def process_check_in(self, barcode: str, name: str):
        try:
            is_first_visit, visit_count, last_visit = self.db.check_in(barcode, name)
            
            dialog = CheckInDialog(name, is_first_visit, visit_count, self)
            dialog.exec()
            
            status = "初回来場" if is_first_visit else f"{visit_count}回目の来場"
            status_icon = "🎉" if is_first_visit else "🔄"
            self.add_log(f"{status_icon} {name} ({barcode}) - {status}")
            
            self.update_stats()
            
        except Exception as e:
            QMessageBox.critical(self, "エラー", f"チェックイン処理中にエラーが発生しました:\n{str(e)}")
            self.add_log(f"❌ エラー: {str(e)}")
    
    def update_stats(self):
        stats = self.db.get_statistics()
        self.lbl_today_total.setText(f"本日: {stats['today_visitors']}人")
        self.lbl_today_first.setText(f"初回: {stats['today_first_visitors']}人")
        self.lbl_today_returning.setText(f"再来場: {stats['today_returning_visitors']}人")
    
    def show_statistics(self):
        dialog = StatisticsWindow(self.db, self)
        dialog.exec()
    
    def add_log(self, message: str):
        from datetime import datetime
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.append(f"[{timestamp}] {message}")
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def closeEvent(self, event):
        if self.scanner_active:
            self.stop_scanner()
        event.accept()
