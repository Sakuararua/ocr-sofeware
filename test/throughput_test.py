import time
import requests
import os
from concurrent.futures import ThreadPoolExecutor

# 服务器地址
SERVER_URL = "http://127.0.0.1:5000/"  # 替换为实际的 Flask 服务地址
UPLOAD_ENDPOINT = SERVER_URL

# 测试图片目录
TEST_IMAGE_DIR = r"D:\Users\ASUS Vivobook\Desktop\ocr软件体系结构\img"
MAX_TEST_IMAGES = 5  # 每次最多测试5张图片
REQUEST_COUNT = 200
# 吞吐量测试的总请求数
CONCURRENCY = 40     # 吞吐量测试的并发数量


def get_test_images(directory, max_images):
    """
    获取指定目录中的前 max_images 张图片路径
    """
    valid_extensions = {".jpg", ".jpeg", ".png"}
    images = [os.path.join(directory, f) for f in os.listdir(directory) 
              if os.path.splitext(f)[1].lower() in valid_extensions]
    return images[:max_images]


def test_throughput(image_paths, total_requests, concurrency):
    """
    测试吞吐量
    """
    def send_request(path):
        """
        发送单个请求
        """
        try:
            files = {'images': (os.path.basename(path), open(path, 'rb'), 'image/jpeg')}
            response = requests.post(UPLOAD_ENDPOINT, files=files)
            return response.status_code == 200
        except Exception as e:
            print(f"请求出错：{e}")
            return False

    print("\n开始测试吞吐量...")

    start_time = time.time()

    # 使用线程池进行并发请求
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(send_request, image_paths[i % len(image_paths)]) for i in range(total_requests)]
        results = [future.result() for future in futures]

    end_time = time.time()

    # 统计测试结果
    total_time = end_time - start_time
    successful_requests = sum(results)
    throughput = successful_requests / total_time if total_time > 0 else 0

    print(f"\n吞吐量测试结果：")
    print(f"总请求数：{total_requests}")
    print(f"成功请求数：{successful_requests}")
    print(f"总耗时：{total_time:.2f} 秒")
    print(f"吞吐量：{throughput:.2f} 图片请求/秒")


if __name__ == "__main__":
    # 准备测试图片
    test_images = get_test_images(TEST_IMAGE_DIR, MAX_TEST_IMAGES)
    if not test_images:
        print(f"目录 {TEST_IMAGE_DIR} 中未找到有效的图片文件")
    else:
        # 测试吞吐量
        test_throughput(test_images, REQUEST_COUNT, CONCURRENCY)
