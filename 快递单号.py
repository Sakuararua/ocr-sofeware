import os
import base64
import requests

# 定义包含所有jpg图片的文件夹路径
folder_path = r"D:\Users\ASUS Vivobook\Desktop\ocr软件体系结构\ocr_lable"

# 设置请求的URL
url = "http://127.0.0.1:1224/api/ocr"

# 遍历文件夹中的所有文件
for filename in os.listdir(folder_path):
    # 检查文件是否为jpg格式
    if filename.endswith(".jpg"):
        # 获取图片的完整路径
        image_path = os.path.join(folder_path, filename)
        
        # 打开并读取图片文件
        with open(image_path, "rb") as image_file:
            # 将图片转换为Base64编码
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        # 设置请求的json数据
        data = {
            "base64": base64_image,
            "options": {
                "ocr.language": "models/config_chinese.txt",
                "ocr.cls": True,
                "ocr.limit_side_len": 4320,
                "tbpu.parser": "multi_none",
                "data.format": "text"
            }
        }
        
        # 发送POST请求到OCR服务
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()  # 检查请求是否成功
            result = response.json()  # 假设返回JSON格式
            
            # 打印当前图片的文件名和识别结果
            print(f"Image: {filename}")
            print(result["data"])  # 输出OCR结果中的文本
            print("-" * 50)  # 分隔线

        except requests.exceptions.RequestException as e:
            print(f"Error processing {filename}: {e}")
