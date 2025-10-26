from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                QGroupBox, QTableWidget, QTableWidgetItem,
                                QPushButton, QFileDialog, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from core.database import VisitorDatabase

class StatisticsWindow(QDialog):
    """統計情報表示ウィンドウ"""
    
    def __init__(self, db: VisitorDatabase, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("来場統計")
        self.setMinimumSize(800, 600)
        
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 統計情報グループ
        stats_group = QGroupBox("統計情報")
        stats_layout = QVBoxLayout()
        
        self.stats_labels = {}
        stats_items = [
            ('total_visitors', '総来場者数'),
            ('today_visitors', '本日の来場者数'),
            ('today_first_visitors', '本日の初回来場者数'),
            ('today_returning_visitors', '本日の再来場者数'),
            ('total_visits', '総来場回数')
        ]
        
        for key, label_text in stats_items:
            h_layout = QHBoxLayout()
            label = QLabel(f"{label_text}:")
            label.setMinimumWidth(200)
            h_layout.addWidget(label)
            
            value_label = QLabel("0")
            value_label.setStyleSheet("QLabel { font-weight: bold; font-size: 16px; }")
            h_layout.addWidget(value_label)
            h_layout.addStretch()
            
            stats_layout.addLayout(h_layout)
            self.stats_labels[key] = value_label
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # 本日の来場者リスト
        list_group = QGroupBox("本日の来場者")
        list_layout = QVBoxLayout()
        
        self.visitors_table = QTableWidget()
        self.visitors_table.setColumnCount(4)
        self.visitors_table.setHorizontalHeaderLabels(['時刻', 'バーコード', '氏名', '状態'])
        self.visitors_table.horizontalHeader().setStretchLastSection(True)
        list_layout.addWidget(self.visitors_table)
        
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)
        
        # ボタン
        button_layout = QHBoxLayout()
        
        btn_export = QPushButton("Excelエクスポート")
        btn_export.clicked.connect(self.export_data)
        button_layout.addWidget(btn_export)
        
        btn_refresh = QPushButton("更新")
        btn_refresh.clicked.connect(self.load_data)
        button_layout.addWidget(btn_refresh)
        
        btn_close = QPushButton("閉じる")
        btn_close.clicked.connect(self.accept)
        button_layout.addWidget(btn_close)
        
        layout.addLayout(button_layout)
    
    def load_data(self):
        """データを読み込んで表示"""
        # 統計情報を更新
        stats = self.db.get_statistics()
        for key, value in stats.items():
            if key in self.stats_labels:
                self.stats_labels[key].setText(str(value))
        
        # 本日の来場者リストを更新
        visitors = self.db.get_today_visitors()
        self.visitors_table.setRowCount(len(visitors))
        
        for i, visitor in enumerate(visitors):
            self.visitors_table.setItem(i, 0, QTableWidgetItem(visitor['visit_time']))
            self.visitors_table.setItem(i, 1, QTableWidgetItem(visitor['barcode']))
            self.visitors_table.setItem(i, 2, QTableWidgetItem(visitor['name']))
            
            status = '初回来場' if visitor['is_first_visit'] else '再来場'
            status_item = QTableWidgetItem(status)
            if visitor['is_first_visit']:
                status_item.setBackground(Qt.green)
            self.visitors_table.setItem(i, 3, status_item)
    
    def export_data(self):
        """データをExcelにエクスポート"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "エクスポート先を選択", "", "Excel Files (*.xlsx)"
        )
        
        if file_path:
            try:
                self.db.export_to_excel(file_path)
                QMessageBox.information(self, "成功", f"データをエクスポートしました:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "エラー", f"エクスポート中にエラーが発生しました:\n{str(e)}")
