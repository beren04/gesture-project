import cv2

cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)

if not cap.isOpened():
    print("Kamera acilamadi.")
    exit()

window_name = "Camera Test"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window_name, 960, 720)

while True:
    ret, frame = cap.read()

    if not ret:
        print("Goruntu alinamadi.")
        break

    cv2.imshow(window_name, frame)

    if cv2.waitKey(10) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()