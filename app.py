from flask import Flask, request, jsonify , render_template
from rembg import remove
from PIL import Image, ImageOps
import io
import base64
from flask_cors import CORS  # 导入 CORS

app = Flask(__name__)
CORS(app)  # 允许所有来源的请求

def base64_to_image(base64_str):
    image_data = base64.b64decode(base64_str)
    return Image.open(io.BytesIO(image_data))


def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

from PIL import Image

def blend_images(foreground, background, max_fg_scale=0.5, ground_y_ratio=0.8):
    # 获取前景和背景图像的尺寸
    fg_width, fg_height = foreground.size
    bg_width, bg_height = background.size

    # 计算前景图像缩放比例
    scale_factor = min(bg_width / fg_width, bg_height / fg_height)

    # 应用最大缩放比例限制
    scale_factor = min(scale_factor, max_fg_scale)

    # 计算缩放后的前景图像尺寸
    new_fg_width = int(fg_width * scale_factor)
    new_fg_height = int(fg_height * scale_factor)

    # 调整前景图像的大小
    resized_foreground = foreground.resize((new_fg_width, new_fg_height), Image.LANCZOS)

    # 计算前景图像底部对齐到背景图像的地面位置
    ground_y = int(bg_height * ground_y_ratio)
    fg_bottom_y = new_fg_height
    top = ground_y - fg_bottom_y

    # 调试输出
    print(f"Foreground size: {fg_width}x{fg_height}")
    print(f"Background size: {bg_width}x{bg_height}")
    print(f"Scale factor: {scale_factor}")
    print(f"Resized foreground size: {new_fg_width}x{new_fg_height}")
    print(f"Ground Y position: {ground_y}")
    print(f"Foreground bottom Y position: {fg_bottom_y}")
    print(f"Top position: {top}")

    # 确保 top 值不小于 0
    if top < 0:
        top = 0

    # 计算前景图像在背景图像中的位置（水平居中）
    left = (bg_width - new_fg_width) // 2

    # 创建一个新的背景图像用于合成
    background_with_fg = background.copy()

    # 在背景图像上粘贴调整后的前景图像
    background_with_fg.paste(resized_foreground, (left, top), resized_foreground)

    return background_with_fg
@app.route('/')
def index():
    return render_template('test.html')

@app.route('/blend', methods=['POST'])
def blend():
    try:
        data = request.json
        foreground_image = base64_to_image(data['foreground'])
        background_image = base64_to_image(data['background'])

        # 使用更新的 `blend_images` 函数
        foreground_no_bg = remove(foreground_image)
        blended_image = blend_images(foreground_no_bg, background_image,
                                     data['max_fg_scale'],
                                     data['ground_y_ratio'])

        result_image_base64 = image_to_base64(blended_image)
        return jsonify({'result': result_image_base64})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
