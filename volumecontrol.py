# Controls system volume using hand gestures detected through real-time tracking.  
# Built with MediaPipe and OpenCV for seamless, touch-free interaction.
import cv2
import time
import numpy as np
import HandTrackingModule as htm
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# ======== Setup volume control ========
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

minVol, maxVol = volume.GetVolumeRange()[:2]

# ======== Configuration ========
wCam, hCam = 640, 480
frameR = 100  # Active frame margin for hand tracking

# ======== Variables ========
pTime = 0
pinch_active = False
pinch_fixed = False
fixedVol = 0

# ======== Setup webcam and hand detector ========
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

    # Black background for sleek UI
    overlay = np.zeros_like(img)
    
    if len(lmList) != 0:
        fingers = detector.fingersUp()
        x1, y1 = lmList[4][1], lmList[4][2]   # Thumb tip
        x2, y2 = lmList[8][1], lmList[8][2]   # Index tip

        # Draw active frame rectangle (slightly transparent)
        cv2.rectangle(overlay, (frameR, frameR), (wCam - frameR, hCam - frameR), (40, 40, 40), -1)
        alpha = 0.6
        img = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)

        # Calculate distance between thumb and index finger (pinch)
        length = np.hypot(x2 - x1, y2 - y1)

        # If index and middle fingers are both down => fix volume
        if fingers[1] == 0 and fingers[2] == 0 and pinch_active:
            pinch_fixed = True
            fixedVol = volume.GetMasterVolumeLevel()
            pinch_active = False

        # If middle finger or index finger open => allow volume control
        if fingers[1] == 1 or fingers[2] == 1:
            pinch_fixed = False

        # Adjust volume if not fixed and pinch (thumb+index) close enough
        if length < 220 and not pinch_fixed:
            vol = np.interp(length, [15, 220], [maxVol, minVol])  # Inverse mapping for natural control
            volume.SetMasterVolumeLevel(vol, None)
            pinch_active = True

        # Visuals: Circles and line between thumb and index
        cv2.circle(img, (x1, y1), 10, (255, 255, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (255, 255, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 3)

        # Volume Bar background (dark grey)
        cv2.rectangle(img, (50, 150), (85, 400), (30, 30, 30), cv2.FILLED)

        # Volume Bar fill based on current or fixed volume
        currentVol = fixedVol if pinch_fixed else volume.GetMasterVolumeLevel()
        volBar = np.interp(currentVol, [minVol, maxVol], [400, 150])
        cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 180, 255), cv2.FILLED)

        # Volume percentage text
        volPercent = int(np.interp(currentVol, [minVol, maxVol], [0, 100]))
        cv2.putText(img, f'{volPercent} %', (40, 440), cv2.FONT_HERSHEY_DUPLEX, 1.5, (255, 255, 255), 3)

        # Status text
        status = "Volume Fixed" if pinch_fixed else "Adjusting Volume"
        cv2.putText(img, status, (200, 50), cv2.FONT_HERSHEY_DUPLEX, 1, (200, 200, 200), 2)

    # Show FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime) if (cTime - pTime) > 0 else 0
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (10, 30), cv2.FONT_HERSHEY_DUPLEX, 0.7, (200, 200, 200), 2)

    cv2.imshow("Sleek Volume Control", img)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
