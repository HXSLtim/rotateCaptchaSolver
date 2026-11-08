# -*- coding: utf-8 -*-
"""
rotateSolver.py —— 旋转滑块（圆盘对齐）解法
======================================================
方案（边缘像素色差法）：
  ① thumb（内盘，被随机旋转 dAngle）按候选角 θ 均匀步进旋转
  ② 每个 θ：取圆盘边界半径 R±dis 处的像素环
     - 内侧环 ← 旋转后的 thumb
     - 外侧环 ← master（挖孔背景）
     对应角度位置求色差，全环求和
  ③ 色差和最小的 θ 即对齐角 → 提交
靶场：127.0.0.1:9901（go-captcha 本地服务，angle 已知可回归）
"""
import base64, json, urllib.request
import cv2
import numpy as np

API = "http://127.0.0.1:9901"

def fetch():
    with urllib.request.urlopen(f"{API}/api/rotate", timeout=10) as r:
        d = json.loads(r.read())["data"]
    master = b64png(d["image"])
    thumb = b64png(d["thumb"])
    return d["key"], master, thumb, d["block"]

def verify(key, angle):
    body = json.dumps({"key": key, "angle": int(angle)}).encode()
    req = urllib.request.Request(f"{API}/api/verify", data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())["data"]

def b64png(dataurl):
    raw = base64.b64decode(dataurl.split(",", 1)[1])
    img = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_UNCHANGED)
    if img.ndim == 3 and img.shape[2] == 4:
        # alpha 合成到白底
        a = img[:, :, 3:4].astype(float) / 255
        rgb = img[:, :, :3].astype(float)
        img = (rgb * a + 255 * (1 - a)).astype(np.uint8)
    return img

def solve(master, thumb, step=1, dis=2, r_frac=0.94):
    """均匀角度步进 + 边缘色差和最小
    内环：thumb 自己的中心 (tw/2, th/2)，半径 R_in = 盘半径 - dis
    外环：master 中心 (W/2, H/2)，半径 R_out = 盘半径 + dis（孔外侧）
    盘半径 = thumb 边长/2（go-captcha 孔径与 thumb 同尺寸）"""
    H, W = master.shape[:2]
    th, tw = thumb.shape[:2]
    tcy, tcx = th / 2, tw / 2          # thumb 中心
    mcy, mcx = H / 2, W / 2            # master 中心
    disc_r = min(tw, th) / 2
    r_in = int(disc_r * r_frac) - dis          # 内环：盘内靠边
    r_out = int(disc_r) + dis + 1              # 外环：孔外靠边
    phis = np.arange(0, 2 * np.pi, np.pi / 180.0)
    xi = (tcx + r_in * np.cos(phis)).astype(int).clip(0, tw - 1)
    yi = (tcy + r_in * np.sin(phis)).astype(int).clip(0, th - 1)
    xo = (mcx + r_out * np.cos(phis)).astype(int).clip(0, W - 1)
    yo = (mcy + r_out * np.sin(phis)).astype(int).clip(0, H - 1)
    outer = master[yo, xo].astype(np.int16)

    best_theta, best_diff = 0, np.inf
    curve = []
    for theta in range(0, 360, step):
        M = cv2.getRotationMatrix2D((tcx, tcy), theta, 1.0)
        rot = cv2.warpAffine(thumb, M, (tw, th), borderValue=(255, 255, 255))
        inner = rot[yi, xi].astype(np.int16)
        diff = float(np.abs(inner - outer).sum())
        curve.append((theta, diff))
        if diff < best_diff:
            best_diff, best_theta = diff, theta
    return best_theta, best_diff, curve

def main(n=20):
    ok, errs = 0, []
    for i in range(n):
        key, master, thumb, block = fetch()
        theta, diff, _ = solve(master, thumb)
        submit = (360 - theta) % 360      # cv2 与 go-captcha 旋转方向相反
        res = verify(key, submit)
        dangle = res["dangle"]
        err = (submit - (360 - dangle)) % 360
        err = min(err, 360 - err)
        errs.append(err)
        if res["pass"]:
            ok += 1
        print(f"[{i+1:>2}] 检测θ={theta:>3}° 提交{submit:>3}°  真值{360-dangle:>3}°  "
              f"误差{err:>2}°  {'✅' if res['pass'] else '❌'}", flush=True)
    print(f"\n通过率: {ok}/{n} = {ok/n*100:.0f}%   角度误差中位数: {np.median(errs):.0f}°  最大: {max(errs)}°")

if __name__ == "__main__":
    main()
