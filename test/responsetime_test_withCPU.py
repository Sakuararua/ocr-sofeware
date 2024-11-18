import time
import psutil
import requests
import os

# 服务器地址
SERVER_URL = "http://127.0.0.1:5000/"  # 替换为 Flask 服务的实际地址
UPLOAD_ENDPOINT = SERVER_URL

# 测试图片目录
TEST_IMAGE_DIR = r"D:\Users\ASUS Vivobook\Desktop\ocr软件体系结构\img"
MAX_TEST_IMAGES = 5

def get_test_images(directory, max_images):
    """
    获取指定目录中的前 max_images 张图片路径
    """
    valid_extensions = {".jpg", ".jpeg", ".png"}
    images = [os.path.join(directory, f) for f in os.listdir(directory) 
              if os.path.splitext(f)[1].lower() in valid_extensions]
    return images[:max_images]

def monitor_resources(duration=1, interval=0.1):
    """
    监控系统资源（CPU 和内存），在指定的时间内定期采样
    - duration: 总采样时间（秒）
    - interval: 每次采样间隔时间（秒）
    """
    cpu_usage = []
    mem_usage = []
    samples = int(duration / interval)

    for _ in range(samples):
        cpu_usage.append(psutil.cpu_percent(interval=interval))
        mem_usage.append(psutil.virtual_memory().percent)

    avg_cpu_usage = sum(cpu_usage) / len(cpu_usage)
    avg_mem_usage = sum(mem_usage) / len(mem_usage)

    return avg_cpu_usage, avg_mem_usage

def test_response_time(image_paths):
    """
    测试上传多张图片的响应时间
    """
    try:
        # 准备上传的文件
        files = [('images', (os.path.basename(path), open(path, 'rb'), 'image/jpeg')) for path in image_paths]
        
        # 发起 POST 请求上传图片
        start_time = time.time()
        response = requests.post(UPLOAD_ENDPOINT, files=files)
        end_time = time.time()
        
        # 计算响应时间
        response_time = end_time - start_time
        
        # 检查响应状态码
        if response.status_code == 200:
            print(f"上传 {len(image_paths)} 张图片成功，响应时间：{response_time:.2f} 秒")
        else:
            print(f"上传图片失败，状态码：{response.status_code}")
        
        return response_time
    except Exception as e:
        print(f"测试响应时间时出错: {e}")
        return None

def batch_test():
    """
    批量测试，统计 3 次的平均响应时间，并打印详细信息
    """
    test_images = get_test_images(TEST_IMAGE_DIR, MAX_TEST_IMAGES)
    if not test_images:
        print(f"目录 {TEST_IMAGE_DIR} 中未找到有效的图片文件")
        return
    
    print(f"开始测试上传 {len(test_images)} 张图片的响应时间...")
    
    total_time = 0
    for i in range(3):
        print(f"\n第 {i + 1} 次测试：")
        
        # 记录上传前的资源使用情况
        avg_cpu_before, avg_mem_before = monitor_resources(duration=1, interval=0.1)
        print(f"上传前 CPU 平均使用率：{avg_cpu_before:.2f}%，内存平均使用率：{avg_mem_before:.2f}%")
        
        # 上传图片并计算响应时间
        response_time = test_response_time(test_images)
        
        # 记录上传后的资源使用情况
        avg_cpu_after, avg_mem_after = monitor_resources(duration=1, interval=0.1)
        print(f"上传后 CPU 平均使用率：{avg_cpu_after:.2f}%，内存平均使用率：{avg_mem_after:.2f}%")
        
        if response_time is not None:
            total_time += response_time
            average_time_image = response_time / len(test_images) if len(test_images) > 0 else -1
            print(f"第 {i + 1} 次响应时间：{response_time:.2f} 秒")
            print(f"每张图片的平均响应时间：{average_time_image:.2f} 秒")
    
    # 计算并输出平均响应时间
    average_time = total_time / 3 if total_time > 0 else 0
    average_time_per_image = average_time / len(test_images) if len(test_images) > 0 else -1

    print(f"平均响应时间（3 次）：{average_time:.2f} 秒")
    print(f"每张图片的平均响应时间：{average_time_per_image:.2f} 秒")

if __name__ == "__main__":
    # 执行批量测试
    batch_test()
