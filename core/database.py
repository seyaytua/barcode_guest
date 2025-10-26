import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Tuple
import os

class VisitorDatabase:
    def __init__(self, db_path: str = "visitors.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """データベースとテーブルを初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 来場者マスタテーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS visitors (
                barcode TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                first_visit_date TEXT NOT NULL,
                visit_count INTEGER DEFAULT 1,
                last_visit_date TEXT NOT NULL
            )
        ''')
        
        # 来場履歴テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS visit_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT NOT NULL,
                name TEXT NOT NULL,
                visit_date TEXT NOT NULL,
                visit_time TEXT NOT NULL,
                is_first_visit INTEGER NOT NULL,
                FOREIGN KEY (barcode) REFERENCES visitors(barcode)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def check_in(self, barcode: str, name: str) -> Tuple[bool, int, str]:
        """
        来場チェックイン処理
        
        Returns:
            Tuple[is_first_visit, visit_count, last_visit_date]
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        current_date = datetime.now().strftime('%Y-%m-%d')
        current_time = datetime.now().strftime('%H:%M:%S')
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            # 既存の来場者かチェック
            cursor.execute(
                'SELECT visit_count, last_visit_date FROM visitors WHERE barcode = ?',
                (barcode,)
            )
            result = cursor.fetchone()
            
            if result is None:
                # 初回来場
                cursor.execute('''
                    INSERT INTO visitors (barcode, name, first_visit_date, visit_count, last_visit_date)
                    VALUES (?, ?, ?, 1, ?)
                ''', (barcode, name, current_datetime, current_datetime))
                
                cursor.execute('''
                    INSERT INTO visit_history (barcode, name, visit_date, visit_time, is_first_visit)
                    VALUES (?, ?, ?, ?, 1)
                ''', (barcode, name, current_date, current_time))
                
                conn.commit()
                return True, 1, current_datetime
            else:
                # 再来場
                visit_count, last_visit = result
                new_count = visit_count + 1
                
                cursor.execute('''
                    UPDATE visitors 
                    SET visit_count = ?, last_visit_date = ?
                    WHERE barcode = ?
                ''', (new_count, current_datetime, barcode))
                
                cursor.execute('''
                    INSERT INTO visit_history (barcode, name, visit_date, visit_time, is_first_visit)
                    VALUES (?, ?, ?, ?, 0)
                ''', (barcode, name, current_date, current_time))
                
                conn.commit()
                return False, new_count, last_visit
                
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_visitor_info(self, barcode: str) -> Optional[Dict]:
        """来場者情報を取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT barcode, name, first_visit_date, visit_count, last_visit_date
            FROM visitors WHERE barcode = ?
        ''', (barcode,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'barcode': result[0],
                'name': result[1],
                'first_visit_date': result[2],
                'visit_count': result[3],
                'last_visit_date': result[4]
            }
        return None
    
    def get_today_visitors(self) -> List[Dict]:
        """本日の来場者リストを取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT barcode, name, visit_time, is_first_visit
            FROM visit_history
            WHERE visit_date = ?
            ORDER BY visit_time DESC
        ''', (today,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'barcode': r[0],
                'name': r[1],
                'visit_time': r[2],
                'is_first_visit': bool(r[3])
            }
            for r in results
        ]
    
    def get_statistics(self) -> Dict:
        """統計情報を取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 総来場者数
        cursor.execute('SELECT COUNT(*) FROM visitors')
        total_visitors = cursor.fetchone()[0]
        
        # 本日の来場者数
        cursor.execute('''
            SELECT COUNT(*) FROM visit_history WHERE visit_date = ?
        ''', (today,))
        today_visitors = cursor.fetchone()[0]
        
        # 本日の初回来場者数
        cursor.execute('''
            SELECT COUNT(*) FROM visit_history 
            WHERE visit_date = ? AND is_first_visit = 1
        ''', (today,))
        today_first_visitors = cursor.fetchone()[0]
        
        # 総来場回数
        cursor.execute('SELECT COUNT(*) FROM visit_history')
        total_visits = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_visitors': total_visitors,
            'today_visitors': today_visitors,
            'today_first_visitors': today_first_visitors,
            'today_returning_visitors': today_visitors - today_first_visitors,
            'total_visits': total_visits
        }
    
    def export_to_excel(self, file_path: str):
        """データをExcelにエクスポート"""
        import openpyxl
        from openpyxl import Workbook
        
        wb = Workbook()
        
        # 来場者マスタシート
        ws_visitors = wb.active
        ws_visitors.title = "来場者マスタ"
        ws_visitors.append(['バーコード', '氏名', '初回来場日時', '来場回数', '最終来場日時'])
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM visitors ORDER BY first_visit_date DESC')
        for row in cursor.fetchall():
            ws_visitors.append(row)
        
        # 来場履歴シート
        ws_history = wb.create_sheet("来場履歴")
        ws_history.append(['ID', 'バーコード', '氏名', '来場日', '来場時刻', '初回来場'])
        
        cursor.execute('SELECT * FROM visit_history ORDER BY visit_date DESC, visit_time DESC')
        for row in cursor.fetchall():
            ws_history.append(list(row[:5]) + ['初回' if row[5] else '再来場'])
        
        conn.close()
        
        # 列幅調整
        for ws in [ws_visitors, ws_history]:
            for column in ws.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column_letter].width = adjusted_width
        
        wb.save(file_path)
