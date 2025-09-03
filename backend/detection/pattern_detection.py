import cv2
import numpy as np

def detect_pattern(frame, background, template):
    # Detect features in template and frame
    orb = cv2.ORB_create()
    kp1, des1 = orb.detectAndCompute(template, None)
    kp2, des2 = orb.detectAndCompute(frame, None)

    # Match features with brute force matcher
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    matches = sorted(matches, key = lambda x:x.distance)
    
    # If enough matches, estimate location and mask
    if len(matches) > 10:
        src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1,1,2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1,1,2)
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        h,w = template.shape[:2]
        pts = np.float32([[0,0],[0,h],[w,h],[w,0]]).reshape(-1,1,2)
        dst = cv2.perspectiveTransform(pts, M)
        mask_img = np.zeros(frame.shape[:2], dtype=np.uint8)
        cv2.fillConvexPoly(mask_img, np.int32(dst), 255)
        mask_inv = cv2.bitwise_not(mask_img)
        
        res1 = cv2.bitwise_and(background, background, mask=mask_img)
        res2 = cv2.bitwise_and(frame, frame, mask=mask_inv)
        combined = cv2.addWeighted(res1, 1, res2, 1, 0)
        return combined
    else:
        return frame
