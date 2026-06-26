import numpy as np

def onCook(scriptOp):

    bg = scriptOp.inputs[0].numpyArray(delayed=False)
    stamp = scriptOp.inputs[1].numpyArray(delayed=False)

    if bg is None:
        return

    out = bg.copy()

    if stamp is None:
        scriptOp.copyNumpyArray(out)
        return

    data = op('/project1/chopto1')

    H, W = out.shape[:2]
    text_img = stamp.copy()

    if text_img.shape[2] < 4:
        alpha = np.ones(text_img.shape[:2] + (1,), dtype=text_img.dtype)
        text_img = np.concatenate([text_img[:, :, :3], alpha], axis=2)

    th, tw = text_img.shape[:2]

    MAX_TEXTS = 100
    X_LIMIT = W * 0.95

    drawn = 3

    if data is not None:
        for i in range(1, data.numRows):

            if drawn >= MAX_TEXTS:
                break

            try:
                y = float(data[i, 1].val)
                x = float(data[i, 2].val)
            except:
                continue

            if x > X_LIMIT:
                continue

            if x < 20 or y < 20 or y > H - 20:
                continue

            x = int(np.clip(x, 0, W - 1))
            y = int(np.clip(y, 0, H - 1))

            x0 = x - tw // 2
            y0 = y - int(th * 0.5)
            x1 = x0 + tw
            y1 = y0 + th

            sx0 = max(0, -x0)
            sy0 = max(0, -y0)
            sx1 = tw - max(0, x1 - W)
            sy1 = th - max(0, y1 - H)

            dx0 = max(0, x0)
            dy0 = max(0, y0)
            dx1 = dx0 + (sx1 - sx0)
            dy1 = dy0 + (sy1 - sy0)

            if dx1 <= dx0 or dy1 <= dy0:
                continue

            src = text_img[sy0:sy1, sx0:sx1, :]
            dst = out[dy0:dy1, dx0:dx1, :]

            alpha = src[:, :, 3:4]

            out[dy0:dy1, dx0:dx1, :3] = (
                src[:, :, :3] * alpha +
                dst[:, :, :3] * (1 - alpha)
            )

            drawn += 1

    scriptOp.copyNumpyArray(out)