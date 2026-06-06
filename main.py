import cv2 as cv
import matplotlib.pyplot as plt




eye1 = cv.imread('eye1.jpg', cv.IMREAD_GRAYSCALE)
eye2 = cv.imread('eye2.jpg', cv.IMREAD_GRAYSCALE)

import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt

# REGISTER eye2 TO eye1 (MATLAB SURF EQUIVALENT)

sift = cv.SIFT_create()

kp1, des1 = sift.detectAndCompute(eye1, None)
kp2, des2 = sift.detectAndCompute(eye2, None)

matcher = cv.BFMatcher()

matches = matcher.knnMatch(des1, des2, k=2)

good_matches = []

for m, n in matches:
    if m.distance < 0.85 * n.distance:
        good_matches.append(m)

pts1 = np.float32(
    [kp1[m.queryIdx].pt for m in good_matches]
).reshape(-1, 1, 2)

pts2 = np.float32(
    [kp2[m.trainIdx].pt for m in good_matches]
).reshape(-1, 1, 2)

M, _ = cv.estimateAffinePartial2D(
    pts2,
    pts1,
    method=cv.RANSAC
)

h, w = eye1.shape

eye2_registered = cv.warpAffine(
    eye2,
    M,
    (w, h)
)

# PUPIL DIAMETER FUNCTION

def get_pupil_diameter(img):

    blur = cv.GaussianBlur(img, (7, 7), 0)

    _, thresh = cv.threshold(
        blur,
        50,
        255,
        cv.THRESH_BINARY_INV
    )

    contours, _ = cv.findContours(
        thresh,
        cv.RETR_EXTERNAL,
        cv.CHAIN_APPROX_SIMPLE
    )

    largest = max(contours, key=cv.contourArea)

    (x, y), radius = cv.minEnclosingCircle(largest)

    diameter = 2 * radius

    return diameter, (int(x), int(y)), int(radius)

# MEASURE BOTH PUPILS


diam1, center1, radius1 = get_pupil_diameter(eye1)
diam2, center2, radius2 = get_pupil_diameter(eye2_registered)

# CALCULATE DILATION

dilation_percent = ((diam2 - diam1) / diam1) * 100

print(f"Eye 1 Diameter : {diam1:.2f} pixels")
print(f"Eye 2 Diameter : {diam2:.2f} pixels")
print(f"Dilation       : {dilation_percent:.2f}%")

# VISUALIZATION


eye1_vis = cv.cvtColor(eye1, cv.COLOR_GRAY2BGR)
eye2_vis = cv.cvtColor(eye2_registered, cv.COLOR_GRAY2BGR)

cv.circle(eye1_vis, center1, radius1, (0,255,0), 2)
cv.circle(eye2_vis, center2, radius2, (0,255,0), 2)

plt.figure(figsize=(12,6))

plt.subplot(1,2,1)
plt.imshow(cv.cvtColor(eye1_vis, cv.COLOR_BGR2RGB))
plt.title(f"Eye 1\nDiameter = {diam1:.2f}px")
plt.axis("off")

plt.subplot(1,2,2)
plt.imshow(cv.cvtColor(eye2_vis, cv.COLOR_BGR2RGB))
plt.title(f"Eye 2 Registered\nDiameter = {diam2:.2f}px")
plt.axis("off")

plt.tight_layout()
plt.show()


plt.figure(figsize=(15,5))

plt.subplot(131)
plt.imshow(eye1,cmap='gray')
plt.title("Fixed")

plt.subplot(132)
plt.imshow(eye2,cmap='gray')
plt.title("Moving")

plt.subplot(133)
plt.imshow(eye2_registered,cmap='gray')
plt.title("Registered")

plt.show()