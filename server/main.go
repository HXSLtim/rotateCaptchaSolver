package main

import (
	"encoding/json"
	"fmt"
	"image"
	"net/http"
	"os"
	"path/filepath"
	"sync"

	"github.com/admpub/go-captcha/v2/base/codec"
	"github.com/admpub/go-captcha/v2/rotate"
)

var (
	capt    rotate.Captcha
	mu      sync.Mutex
	sessions = map[string]int{} // key -> dAngle
	keySeq  int
)

func main() {
	// 载入素材目录
	var imgs []image.Image
	files, _ := filepath.Glob("bg/*.png")
	for _, f := range files {
		b, err := os.ReadFile(f)
		if err != nil { continue }
		img, err := codec.DecodeByteToPng(b)
		if err != nil { continue }
		imgs = append(imgs, img)
	}
	if len(imgs) == 0 {
		fmt.Println("no bg images in ./bg")
		os.Exit(1)
	}
	b := rotate.NewBuilder()
	b.SetResources(rotate.WithImages(imgs))
	capt = b.Make()

	http.HandleFunc("/api/rotate", func(w http.ResponseWriter, r *http.Request) {
		mu.Lock(); defer mu.Unlock()
		data, err := capt.Generate()
		if err != nil {
			json.NewEncoder(w).Encode(map[string]any{"code": 1, "msg": err.Error()})
			return
		}
		key := fmt.Sprintf("k%d", keySeq); keySeq++
		dAngle := data.GetData().Angle
		sessions[key] = dAngle
		mb64, _ := data.GetMasterImage().ToBase64()
		tb64, _ := data.GetThumbImage().ToBase64()
		json.NewEncoder(w).Encode(map[string]any{
			"code": 0,
			"data": map[string]any{
				"key":   key,
				"image": mb64,
				"thumb": tb64,
				"block": data.GetData(),
			},
		})
	})

	http.HandleFunc("/api/verify", func(w http.ResponseWriter, r *http.Request) {
		var req struct{ Key string `json:"key"`; Angle int `json:"angle"` }
		json.NewDecoder(r.Body).Decode(&req)
		mu.Lock(); d, ok := sessions[req.Key]; mu.Unlock()
		if !ok {
			json.NewEncoder(w).Encode(map[string]any{"code": 1, "msg": "no session"})
			return
		}
		ok2 := rotate.Validate(req.Angle, d, 10)
		json.NewEncoder(w).Encode(map[string]any{"code": 0, "data": map[string]any{
			"pass": ok2, "angle": req.Angle, "dangle": d,
		}})
	})

	fmt.Println("go-captcha rotate 靶场 :9901")
	http.ListenAndServe("127.0.0.1:9901", nil)
}
