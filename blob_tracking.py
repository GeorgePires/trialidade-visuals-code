import cv2
import numpy as np

kernel = np.ones((3, 3), np.uint8)

def onCook(scriptOp):
    #refactor (????
    RECT_W     = 1
    RECT_H     = 1
    MODE       = 'area'
    COLOR_MODE = 'rgb'
    THRESH_VAL = 70
    MIN_AREA   = 100
    MAX_AREA   = 1500
    MAX_BLOBS  = 20   

    input_top = scriptOp.inputs[0].numpyArray(delayed=True)
    if input_top is None:
        return

    h_img, w_img = input_top.shape[:2]

    img_rgb = input_top[:, :, :3]

    img_u8 = (img_rgb * 255).astype(np.uint8)

    gray = cv2.cvtColor(img_u8, cv2.COLOR_RGB2GRAY)

    _, thresh = cv2.threshold(gray, THRESH_VAL, 255, cv2.THRESH_BINARY)

    cv2.dilate(thresh, kernel, iterations=1, dst=thresh)

    # contours
    contours, _ = cv2.findContours(
        thresh,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    rects = []
    values = []

    limit_x = int(w_img * 0.75)

    for c in contours:
        x, y, w, h = cv2.boundingRect(c)

        if x > limit_x:
            continue

        area = cv2.contourArea(c)

        if area < MIN_AREA or area > MAX_AREA:
            continue

        if MODE == 'area':
            val = w * h
        elif MODE == 'width':
            val = w
        elif MODE == 'height':
            val = h
        else:
            val = w * h

        rects.append((x, y, w, h))
        values.append(val)

        if len(rects) >= MAX_BLOBS:
            break
 
    out = np.zeros((h_img, w_img, 4), dtype=np.float32)
    out[:, :, 3] = 1.0

    if values:
        vals = np.array(values, dtype=np.float32)
        vmin = vals.min()
        vmax = vals.max()

        if vmax - vmin == 0:
            norm_vals = np.zeros_like(vals)
        else:
            norm_vals = (vals - vmin) / (vmax - vmin)

        for i, (x, y, w, h) in enumerate(rects):
            cx = x + w // 2
            cy = y + h // 2

            x1 = max(cx - RECT_W // 2, 0)
            y1 = max(cy - RECT_H // 2, 0)
            x2 = min(cx + RECT_W // 2, w_img - 1)
            y2 = min(cy + RECT_H // 2, h_img - 1)

            v = float(norm_vals[i])

            if COLOR_MODE == 'grayscale':
                color = (v, v, v, 1.0)
            else:
                hue = int(v * 179)
                hsv_pixel = np.uint8([[[hue, 220, 255]]])
                bgr_pixel = cv2.cvtColor(hsv_pixel, cv2.COLOR_HSV2BGR)
                b, g, r = bgr_pixel[0, 0]
                color = (r / 255.0, g / 255.0, b / 255.0, 1.0)

            out[y1:y2+1, x1:x2+1] = color

    scriptOp.copyNumpyArray(out)