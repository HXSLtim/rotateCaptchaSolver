# 生成 20 张纹理背景（cd server && mkdir bg && python3 genbg.py）
import cv2, numpy as np, os
rng = np.random.default_rng(7)
os.makedirs("bg", exist_ok=True)
for i in range(20):
    img = np.zeros((480, 480, 3), np.uint8)
    c1, c2 = rng.integers(40, 220, 3), rng.integers(40, 220, 3)
    for y in range(480):
        t = y / 480
        img[y] = (c1 * (1-t) + c2 * t).astype(np.uint8)
    for _ in range(rng.integers(12, 25)):
        kind = rng.integers(0, 4)
        col = tuple(int(v) for v in rng.integers(0, 255, 3))
        pt = tuple(int(v) for v in rng.integers(0, 480, 2))
        if kind == 0:
            cv2.circle(img, pt, int(rng.integers(10, 90)), col, -1)
        elif kind == 1:
            cv2.rectangle(img, pt, (pt[0]+int(rng.integers(20,120)), pt[1]+int(rng.integers(20,120))), col, -1)
        elif kind == 2:
            cv2.line(img, pt, (pt[0]+int(rng.integers(-150,150)), pt[1]+int(rng.integers(-150,150))), col, int(rng.integers(2,10)))
        else:
            pts = np.array([[pt[0]+dx, pt[1]+dy] for dx, dy in rng.integers(-80, 80, (3,2))], np.int32)
            cv2.fillPoly(img, [pts], col)
    cv2.imwrite(f"bg/{i:02d}.png", cv2.GaussianBlur(img, (3,3), 0))
print("bg/ 20 张完成")
