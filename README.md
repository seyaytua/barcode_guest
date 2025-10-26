# 来場管理システム

バーコード/QRコードを使用した来場者管理アプリケーション

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)

## 機能

### 読み取りモード
- **手動入力モード**: キーボードでバーコードと氏名を入力
- **USBスキャナーモード**: USBバーコードスキャナーで高速読み取り

### 主要機能
- 来場者の自動認識（初回/再来場の判定）
- リアルタイム統計表示
- 来場履歴の記録
- Excelエクスポート
- 大画面表示（USBスキャナーモード時）

## インストール

### 必要要件
- Python 3.11以上
- macOS / Windows

### セットアップ

```bash
# リポジトリをクローン
git clone https://github.com/seyaytua/barcode_guest.git
cd barcode_guest

# 仮想環境を作成
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存パッケージをインストール
pip install -r requirements.txt
使い方
Copy# アプリケーションを起動
python main.py
手動入力モード
バーコード値を入力
新規来場者の場合は氏名も入力
「チェックイン」ボタンをクリック
USBスキャナーモード
USBバーコードスキャナーを接続
「USBスキャナー」モードを選択
ポートを選択して「スキャナー起動」
バーコードをスキャン
プロジェクト構造
barcode_guest/
├── main.py                    # エントリーポイント
├── requirements.txt           # 依存パッケージ
├── core/
│   ├── __init__.py
│   ├── database.py           # データベース管理
│   └── barcode_reader.py     # バーコード読み取り
└── gui/
    ├── __init__.py
    ├── main_window.py        # メインウィンドウ
    ├── check_in_dialog.py    # チェックイン表示
    └── statistics_window.py  # 統計ウィンドウ
ビルド
macOS用実行ファイル
Copypip install pyinstaller
pyinstaller --onefile --windowed --name "来場管理システム" main.py
実行ファイルは dist/ フォルダに生成されます。

Windows用実行ファイル
Copypip install pyinstaller
pyinstaller --onefile --windowed --name "来場管理システム" --icon=icon.ico main.py
データベース
SQLite3を使用してデータを管理します。

テーブル構造
visitors - 来場者マスタ

barcode (TEXT, PRIMARY KEY)
name (TEXT)
first_visit_date (TEXT)
visit_count (INTEGER)
last_visit_date (TEXT)
visit_history - 来場履歴

id (INTEGER, PRIMARY KEY)
barcode (TEXT)
name (TEXT)
visit_date (TEXT)
visit_time (TEXT)
is_first_visit (INTEGER)
技術スタック
GUI: PySide6 (Qt for Python)
Database: SQLite3
Serial Communication: pyserial
Excel: openpyxl
Image Processing: Pillow
ライセンス
MIT License

貢献
プルリクエストを歓迎します！

サポート
問題が発生した場合は、Issuesで報告してください。

作者
@seyaytua
