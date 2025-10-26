import serial
import serial.tools.list_ports
from PySide6.QtCore import QThread, Signal

class ScannerReaderThread(QThread):
    """バーコードスキャナー読み取りスレッド（USB/シリアルポート用）"""
    barcode_detected = Signal(str)
    error_occurred = Signal(str)
    
    def __init__(self, port: str = None, baudrate: int = 9600):
        super().__init__()
        self.running = False
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None
    
    @staticmethod
    def list_available_ports():
        """利用可能なシリアルポートをリストアップ"""
        ports = serial.tools.list_ports.comports()
        return [(port.device, port.description) for port in ports]
    
    def run(self):
        """シリアルポートからバーコードを読み取る"""
        self.running = True
        
        try:
            if not self.port:
                ports = self.list_available_ports()
                if not ports:
                    self.error_occurred.emit("利用可能なシリアルポートが見つかりません")
                    return
                self.port = ports[0][0]
            
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1
            )
            
            buffer = ""
            
            while self.running:
                if self.serial_conn.in_waiting > 0:
                    try:
                        data = self.serial_conn.read(self.serial_conn.in_waiting)
                        decoded = data.decode('utf-8', errors='ignore')
                        buffer += decoded
                        
                        if '\n' in buffer or '\r' in buffer:
                            lines = buffer.split('\n')
                            for line in lines[:-1]:
                                line = line.strip().replace('\r', '')
                                if line:
                                    self.barcode_detected.emit(line)
                            buffer = lines[-1]
                    except Exception as e:
                        self.error_occurred.emit(f"読み取りエラー: {str(e)}")
                
        except serial.SerialException as e:
            self.error_occurred.emit(f"シリアルポート接続エラー: {str(e)}")
        except Exception as e:
            self.error_occurred.emit(f"予期しないエラー: {str(e)}")
        finally:
            if self.serial_conn and self.serial_conn.is_open:
                self.serial_conn.close()
    
    def stop(self):
        """スレッドを停止"""
        self.running = False
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
        self.wait()
