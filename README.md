# rotate —— 旋转滑块（圆盘对齐）

## 状态：✅ 100%（本地靶场 20/20，角度误差中位 2°）

## 方案：边缘像素色差法（均匀角度步进）
thumb（被随机旋转的内盘）按 1° 步进转 360 圈，每个角度取盘边界内外两圈
像素（R±2px，360 个采样点），与 master 孔外侧像素求色差和，最小者即对齐角。
提交角 = (360 - θ) % 360（cv2 与 go-captcha 旋转正方向相反）。

## 哪里出现
- 网易易盾（增强滑块/旋转）、顶象、Vaptcha 手势
- 自建系：go-captcha（本靶场）、tianai-captcha（政务/校园站常见）

## 文件
- rotateSolver.py   求解器（fetch/solve/verify，20 轮回归）
- server/           本地 go-captcha 靶场（真值已知，可回归）
