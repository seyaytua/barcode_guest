from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

class CheckInDialog(QDialog):
    """チェックイン結果表示ダイアログ"""
    
    def __init__(self, name: str, is_first_visit: bool, visit_count: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("来場確認")
        self.setModal(True)
        
        # ウィンドウサイズを大きく
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(30)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # 来場者名
        name_label = QLabel(name)
        name_label.setAlignment(Qt.AlignCenter)
        name_font = QFont()
        name_font.setPointSize(36)
        name_font.setBold(True)
        name_label.setFont(name_font)
        layout.addWidget(name_label)
        
        # 初回/再来場表示
        if is_first_visit:
            status_label = QLabel("🎉 初回来場 🎉")
            status_label.setStyleSheet("""
                QLabel {
                    background-color: #4CAF50;
                    color: white;
                    border-radius: 15px;
                    padding: 40px;
                }
            """)
        else:
            status_label = QLabel(f"🔄 {visit_count}回目の来場")
            status_label.setStyleSheet("""
                QLabel {
                    background-color: #2196F3;
                    color: white;
                    border-radius: 15px;
                    padding: 40px;
                }
            """)
        
        status_label.setAlignment(Qt.AlignCenter)
        status_font = QFont()
        status_font.setPointSize(48)
        status_font.setBold(True)
        status_label.setFont(status_font)
        layout.addWidget(status_label)
        
        # メッセージ
        message = "ようこそ！" if is_first_visit else "お帰りなさい！"
        message_label = QLabel(message)
        message_label.setAlignment(Qt.AlignCenter)
        message_font = QFont()
        message_font.setPointSize(24)
        message_label.setFont(message_font)
        layout.addWidget(message_label)
        
        # 3秒後に自動的に閉じる
        QTimer.singleShot(3000, self.accept)
