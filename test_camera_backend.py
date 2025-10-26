import cv2

print("=" * 60)
print("カメラバックエンド別テスト")
print("=" * 60)

backends = [
    (cv2.CAP_AVFOUNDATION, "AVFoundation (macOS標準)"),
    (cv2.CAP_ANY, "自動選択"),
]

for backend_id, backend_name in backends:
    print(f"\n【{backend_name}】")
    for i in range(5):
        cap = cv2.VideoCapture(i, backend_id)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"  カメラ {i}: 動作OK ({frame.shape[1]}x{frame.shape[0]})")
            else:
                print(f"  カメラ {i}: 開けるが映像なし")
            cap.release()
        else:
            print(f"  カメラ {i}: 利用不可")

print("\n" + "=" * 60)
