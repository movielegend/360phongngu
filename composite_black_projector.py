import cv2
import numpy as np
import json

# 1. Load pristine original for clean ceiling and current phong1_3k.jpg
orig = cv2.imread(r'D:\360\70158594.jpg')
pano = cv2.imread(r'D:\360\phong1_3k.jpg')

# Restore the projector area in ceiling to pristine original
pano[240:580, 1000:1420] = orig[240:580, 1000:1420]
print("Ceiling restored to pristine clean state.")

# 2. Load the 2400x1800 transparent render
render = cv2.imread(r'D:\360\projector_render_transparent.png', cv2.IMREAD_UNCHANGED)
rh, rw = render.shape[:2]

# Apply subtle unsharp mask to the render RGB to enhance edge acuity & mechanical details
render_rgb = render[:, :, :3].astype(np.float32)
alpha = render[:, :, 3].astype(np.float32) / 255.0

blur = cv2.GaussianBlur(render_rgb, (0, 0), sigmaX=1.0)
sharp_rgb = cv2.addWeighted(render_rgb, 1.45, blur, -0.45, 0)
sharp_rgb = np.clip(sharp_rgb, 0, 255)

# Reassemble sharpened render
render_sharp = np.dstack([sharp_rgb, render[:, :, 3]])

# 3. Load camera parameters
with open(r'D:\360\camera_params.json', 'r') as f:
    cam = json.load(f)

elements = np.array(cam['matrixWorld']).reshape((4, 4), order='F')
R_cam2world = elements[:3, :3]
R_world2cam = R_cam2world.T

fov_deg = cam['fov']
fov = np.radians(fov_deg)
aspect = cam['aspect']
focal = 1.0 / np.tan(fov * 0.5)

h_pano, w_pano = pano.shape[:2]

# Target region in panorama
px_range = np.arange(1000, 1420)
py_range = np.arange(240, 580)
grid_px, grid_py = np.meshgrid(px_range, py_range)

# 4. 4x Full-Scene Anti-Aliasing (FSAA) per panorama pixel
sub_offsets = [-0.25, 0.25]
accum_color = np.zeros((len(py_range), len(px_range), 3), dtype=np.float32)
accum_alpha = np.zeros((len(py_range), len(px_range), 1), dtype=np.float32)

for dy in sub_offsets:
    for dx in sub_offsets:
        sub_px = grid_px + dx
        sub_py = grid_py + dy

        lon = (sub_px / w_pano - 0.5) * 2.0 * np.pi
        lat = (0.5 - sub_py / h_pano) * np.pi

        rx_w = np.cos(lat) * np.sin(lon)
        ry_w = np.sin(lat)
        rz_w = np.cos(lat) * np.cos(lon)

        rays_w = np.stack([rx_w, ry_w, rz_w], axis=-1)
        rays_cam = np.einsum('ij,abj->abi', R_world2cam, rays_w)

        valid = rays_cam[:, :, 2] < -0.05

        u_scr = (-rays_cam[:, :, 0] / rays_cam[:, :, 2]) * (focal / (2.0 * aspect)) + 0.5
        v_scr = 0.5 - (-rays_cam[:, :, 1] / rays_cam[:, :, 2]) * (focal / 2.0)

        x_rend = u_scr * rw
        y_rend = v_scr * rh

        inside = valid & (x_rend >= 0) & (x_rend < rw - 1) & (y_rend >= 0) & (y_rend < rh - 1)

        # Bilinear sample from render_sharp
        samp_x = np.clip(x_rend, 0, rw - 1.001)
        samp_y = np.clip(y_rend, 0, rh - 1.001)

        x0 = np.floor(samp_x).astype(int)
        y0 = np.floor(samp_y).astype(int)
        x1 = np.minimum(x0 + 1, rw - 1)
        y1 = np.minimum(y0 + 1, rh - 1)

        fx = (samp_x - x0)[:, :, None]
        fy = (samp_y - y0)[:, :, None]

        I00 = render_sharp[y0, x0].astype(np.float32)
        I01 = render_sharp[y1, x0].astype(np.float32)
        I10 = render_sharp[y0, x1].astype(np.float32)
        I11 = render_sharp[y1, x1].astype(np.float32)

        samp_rgba = (1.0 - fx)*(1.0 - fy)*I00 + (1.0 - fx)*fy*I01 + fx*(1.0 - fy)*I10 + fx*fy*I11

        sub_alpha = (samp_rgba[:, :, 3:] / 255.0) * inside[:, :, None]
        sub_rgb = samp_rgba[:, :, :3]

        accum_color += sub_rgb * sub_alpha
        accum_alpha += sub_alpha

# Average across the 4 sub-pixels
mask = accum_alpha > 0.001
avg_color = np.zeros_like(accum_color)
avg_color[mask[:, :, 0]] = accum_color[mask[:, :, 0]] / accum_alpha[mask[:, :, 0]]
avg_alpha = accum_alpha / 4.0

# Blend onto panorama
pano_region = pano[240:580, 1000:1420].astype(np.float32)
blended = pano_region * (1.0 - avg_alpha) + avg_color * avg_alpha
pano[240:580, 1000:1420] = np.clip(blended, 0, 255).astype(np.uint8)

# Save result
cv2.imwrite(r'D:\360\phong1_3k.jpg', pano, [cv2.IMWRITE_JPEG_QUALITY, 94])
print("Updated D:\\360\\phong1_3k.jpg with high-res deep black K9!")

# Verify: crop the exact projector view
crop_verify = pano[280:550, 1050:1350]
cv2.imwrite(r'D:\360\black_projector_verify.jpg', crop_verify)
print("Saved black_projector_verify.jpg!")
