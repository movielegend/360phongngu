# 360° Virtual Tour & 3D Cinema Experience

Trình xem ảnh 360° Panorama chất lượng cao tích hợp mô hình 3D máy chiếu K9, màn chiếu điện ảnh 3D và luồng sáng máy chiếu (volumetric light beam & lens flare) dựng bằng WebGL/GLSL shader trực tiếp trên trình duyệt.

## Tính năng nổi bật
- **WebGL Panorama Viewer**: Tự động xoay 360°, làm nét ảnh (sharpening), điều khiển góc nhìn tự do, hỗ trợ xoay, zoom và kéo thả ảnh panorama mới.
- **3D Screen & Video Cinema**: Phát video trực tiếp lên màn chiếu 3D gắn trên tường phòng, đồng bộ tỷ lệ 16:9 sắc nét.
- **Projector Volumetric Light Beam**: Shader GLSL mô phỏng luồng sáng quang học hình nón và ánh chói ống kính (lens flare) phát từ ống kính máy chiếu K9 tới màn chiếu.
- **Điều khiển tiện lợi**: Nút Mute/Unmute trên thanh công cụ, phím tắt `M`, hoặc chạm trực tiếp vào màn chiếu trên tường 3D để bật/tắt tiếng và tạm dừng/phát phim.

## Hướng dẫn Deploy

### Cách 1: Deploy lên Vercel (Khuyến nghị)
1. Cài đặt Vercel CLI (nếu có): `npm i -g vercel`
2. Chạy lệnh: `vercel`
3. Hoặc liên kết trực tiếp repository GitHub này trên Dashboard [vercel.com](https://vercel.com).

### Cách 2: Deploy lên GitHub Pages
1. Đẩy mã nguồn lên repository GitHub của bạn:
   ```bash
   git remote add origin https://github.com/<your-username>/<your-repo>.git
   git branch -M main
   git push -u origin main
   ```
2. Vào **Settings** > **Pages** trên GitHub repository.
3. Chọn nguồn **Deploy from a branch** > branch `main` / root (`/`) > bấm **Save**.

### Cách 3: Chạy trên máy cục bộ (Local Server)
```bash
python -m http.server 8110
```
Truy cập: [http://localhost:8110](http://localhost:8110)
