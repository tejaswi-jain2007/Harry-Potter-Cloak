import cv2
import numpy as np

def detect_cloak(frame, background, color='green', sensitivity=20, feather=True):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Define HSV ranges for different colors
    color_ranges = {
        'green': {
            'lower': np.array([30, 30, 30]),
            'upper': np.array([100, 255, 255])
        },
        'red': [
            {'lower': np.array([0, 120, 70]), 'upper': np.array([sensitivity, 255, 255])},
            {'lower': np.array([180 - sensitivity, 120, 70]), 'upper': np.array([180, 255, 255])}
        ],
        'blue': {
            'lower': np.array([100 - sensitivity, 150, 0]),
            'upper': np.array([140 + sensitivity, 255, 255])
        }
    }
    
    # Generate mask for cloak color
    if color == 'red':
        mask1 = cv2.inRange(hsv, color_ranges['red'][0]['lower'], color_ranges['red'][0]['upper'])
        mask2 = cv2.inRange(hsv, color_ranges['red'][1]['lower'], color_ranges['red'][1]['upper'])
        mask = mask1 + mask2
    else:
        lower = color_ranges.get(color, color_ranges['green'])['lower']
        upper = color_ranges.get(color, color_ranges['green'])['upper']
        mask = cv2.inRange(hsv, lower, upper)
    
    # Strong morphological operations for smoother mask
    kernel = np.ones((7,7), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask = cv2.dilate(mask, kernel, iterations=3)
    mask = cv2.GaussianBlur(mask, (13, 13), 0)
    mask_inv = cv2.bitwise_not(mask)

    if feather:
        # Alpha blend for softer transitions (reduces outline)
        alpha_mask = cv2.GaussianBlur(mask/255.0, (31, 31), 0)
        res1 = (background.astype(float) * alpha_mask[..., None]).astype(np.uint8)
        res2 = (frame.astype(float) * (1 - alpha_mask[..., None])).astype(np.uint8)
        combined = cv2.addWeighted(res1, 1, res2, 1, 0)
        return combined
    else:
        # Standard abrupt mask (may show more outline)
        res1 = cv2.bitwise_and(background, background, mask=mask)
        res2 = cv2.bitwise_and(frame, frame, mask=mask_inv)
        combined = cv2.addWeighted(res1, 1, res2, 1, 0)
        return combined
