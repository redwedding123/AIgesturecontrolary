# Enables cursor control using hand gestures via real-time hand tracking.  
# Ideal for touchless interaction; built on MediaPipe and OpenCV.
import cv2
import numpy as np
import HandTrackingModule as htm
import time
import autopy

# ======== Configuration ========
wCam, hCam = 640, 480          # Webcam resolution
frameR = 50                   # Frame Reduction for active area
smoothening = 4                # Smoothing factor for mouse movement

# ======== Variables ========
pTime = 0                     # Previous time for FPS calculation
plocX, plocY = 0, 0           # Previous location of mouse
clocX, clocY = 0, 0           # Current location of mouse

# ======== Setup webcam ========
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

detector = htm.handDetector(maxHands=1)
wScr, hScr = autopy.screen.size()  # Screen size

while True:
    success, img = cap.read()
    if not success:
        break
    
    img = cv2.flip(img, 1)

    # 1. Detect hands and landmarks
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)

    if len(lmList) != 0:
        # 2. Get coordinates of index and middle finger tips
        x1, y1 = lmList[8][1], lmList[8][2]
        x2, y2 = lmList[12][1], lmList[12][2]

        # 3. Check which fingers are up
        fingers = detector.fingersUp()
        
        # Draw active frame rectangle
        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR),
                      (0, 140, 255), 2)

        # 4. Moving mode: Only index finger is up
        if fingers[1] == 1 and fingers[2] == 0:
            # Convert coordinates from webcam frame to screen size
            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))


            
            print(f"Finger Y: {y1} -> Cursor Y: {int(y3)}")


            # Smooth the mouse movement
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening

            # Move mouse
            autopy.mouse.move(int(clocX), int(clocY))

            # Visual feedback: circle on the index finger tip
            cv2.circle(img, (x1, y1), 15, (0, 140, 255), cv2.FILLED)

            # Update previous location
            plocX, plocY = clocX, clocY

        # 5. Clicking mode: Both index and middle fingers up
        elif fingers[1] == 1 and fingers[2] == 1:
            length, img, lineInfo = detector.findDistance(8, 12, img)
            # Visualize distance and print for debugging
            # print(length)

            # Click mouse if distance between fingers is short
            if length < 40:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                autopy.mouse.click()

    # 6. Calculate and display FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime) if (cTime - pTime) > 0 else 0
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)


    # 7. Show the image
    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == 27:  # Exit on 'ESC'
        break

cap.release()
cv2.destroyAllWindows()
