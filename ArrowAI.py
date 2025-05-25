# Control arrow keys with just a wave—gesture-powered navigation using computer vision.  
# Perfect for touchless gaming, slick slideshows, or futuristic UI hacks.
import cv2
import time
import pyautogui
import HandTrackingModule as htm

# ======== Configuration ========
wCam, hCam = 640, 480
cooldown = 0.3               # Delay between key presses
label_display_time = 0.7     # Time to show direction label (in seconds)

# ======== Initialization ========
pTime = 0
lastPressTime = 0
lastLabelTime = 0
lastLabel = ""
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
detector = htm.handDetector(maxHands=1)

while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)
    currentTime = time.time()

    if len(lmList) != 0:
        fingers = detector.fingersUp()

        if currentTime - lastPressTime > cooldown:
            if fingers == [0, 1, 0, 0, 0]:  # Index up
                pyautogui.press('up')
                lastLabel = "UP"
                lastPressTime = currentTime
                lastLabelTime = currentTime

            elif fingers == [0, 0, 1, 0, 0]:  # Middle up
                pyautogui.press('down')
                lastLabel = "DOWN"
                lastPressTime = currentTime
                lastLabelTime = currentTime

            elif fingers == [0, 1, 1, 0, 0]:  # Index + Middle
                pyautogui.press('right')
                lastLabel = "RIGHT"
                lastPressTime = currentTime
                lastLabelTime = currentTime

            elif fingers == [1, 1, 1, 1, 0]:  # Thumb + Index + Middle + Ring
                pyautogui.press('left')
                lastLabel = "LEFT"
                lastPressTime = currentTime
                lastLabelTime = currentTime

    # ======== Show Direction Label ========
    if currentTime - lastLabelTime < label_display_time:
        cv2.putText(img, lastLabel, (220, 80), cv2.FONT_HERSHEY_SIMPLEX,
                    1.5, (0, 140, 255), 3)

    # ======== FPS Display ========
    cTime = currentTime
    fps = 1 / (cTime - pTime) if (cTime - pTime) > 0 else 0
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

    # ======== Show Image ========
    cv2.imshow("Arrow Key Controller", img)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
        break

cap.release()
cv2.destroyAllWindows()
