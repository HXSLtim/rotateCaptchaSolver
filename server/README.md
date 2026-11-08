# go-captcha rotate 本地靶场

```bash
cd server
python3 genbg.py        # 生成 bg/ 素材
go mod init gcserver && go mod tidy
go build -o gcserver . && ./gcserver   # :9901
```

- GET  /api/rotate  → {image: master b64, thumb: 盘 b64, block.angle: 真值}
- POST /api/verify  {key, angle} → pass = angle+dAngle ∈ 360±10
