import os
import json
import time
import requests

# 设置路径
pdf_dir = r"D:\Users\ASUS Vivobook\Desktop\数据挖掘\A_document"
output_dir = r"D:\Users\ASUS Vivobook\Desktop\OCR-API\test"
base_url = "http://127.0.0.1:1224"

# 创建输出目录
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 遍历pdf目录下的所有文件
for file_name in os.listdir(pdf_dir):
    if file_name.endswith(".pdf"):
        file_path = os.path.join(pdf_dir, file_name)
        
        # Step 1: 上传文件，获取任务ID
        url_upload = f"{base_url}/api/doc/upload"
        with open(file_path, "rb") as file:
            response = requests.post(url_upload, files={"file": file}, data={"json": json.dumps({"doc.extractionMode": "mixed"})})
        response.raise_for_status()
        res_data = response.json()
        
        # 检查上传是否成功
        if res_data["code"] != 100:
            print(f"文件 {file_name} 上传失败: {res_data}")
            continue
        task_id = res_data["data"]
        print(f"文件 {file_name} 上传成功，任务ID: {task_id}")
        
        # Step 2: 轮询任务状态
        url_status = f"{base_url}/api/doc/result"
        while True:
            time.sleep(1)
            response = requests.post(url_status, json={"id": task_id, "is_data": True, "format": "text"})
            response.raise_for_status()
            res_data = response.json()
            
            if res_data["code"] != 100:
                print(f"查询任务状态失败：{res_data}")
                break
            
            # 检查任务是否完成
            if res_data["is_done"]:
                if res_data["state"] == "success":
                    print(f"文件 {file_name} 的OCR任务完成")
                else:
                    print(f"文件 {file_name} 的OCR任务失败: {res_data.get('message', '未知错误')}")
                break
        
        # Step 3: 获取下载链接
        url_download = f"{base_url}/api/doc/download"
        download_options = {
            "id": task_id,
            "file_types": ["txt"],
            "ingore_blank": False
        }
        response = requests.post(url_download, json=download_options)
        response.raise_for_status()
        res_data = response.json()
        
        if res_data["code"] != 100:
            print(f"获取下载链接失败: {res_data}")
            continue
        download_url = res_data["data"]
        
        # Step 4: 下载识别结果并保存为txt
        response = requests.get(download_url, stream=True)
        response.raise_for_status()
        
        output_path = os.path.join(output_dir, f"{os.path.splitext(file_name)[0]}.txt")
        with open(output_path, "wb") as output_file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    output_file.write(chunk)
        
        print(f"文件 {file_name} 的OCR结果保存成功: {output_path}")

        # Step 5: 清理任务
        url_clear = f"{base_url}/api/doc/clear/{task_id}"
        response = requests.get(url_clear)
        response.raise_for_status()
        print(f"任务 {task_id} 已清理\n")
