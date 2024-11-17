import base64
import requests
from sparkai.llm.llm import ChatSparkLLM
from sparkai.core.messages import ChatMessage

# 配置信息
SPARKAI_URL = 'wss://spark-api.xf-yun.com/v4.0/chat'
SPARKAI_APP_ID = 'd64c2933'
SPARKAI_API_SECRET = 'YTRlZTI0OWRlNzYxMDY3MTNkNTJmOWEz'
SPARKAI_API_KEY = '87b3978f5b7cdbdfa9aec79f2f1234dc'
SPARKAI_DOMAIN = '4.0Ultra'

# 初始化大模型客户端
spark = ChatSparkLLM(
    spark_api_url=SPARKAI_URL,
    spark_app_id=SPARKAI_APP_ID,
    spark_api_key=SPARKAI_API_KEY,
    spark_api_secret=SPARKAI_API_SECRET,
    spark_llm_domain=SPARKAI_DOMAIN,
    streaming=False,
)

OCR_URL = "http://127.0.0.1:1224/api/ocr"


# OCR识别
def ocr_recognition(image_path):
    try:
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
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
        response = requests.post(OCR_URL, json=data)
        if response.status_code == 200:
            result = response.json()
            if result["code"] == 100:
                return result["data"]
    except Exception as e:
        from logger import log_error
        log_error(f"OCR识别失败: {e}")
    return None

# 大模型处理
def extract_delivery_info(ocr_text):
    messages = [ChatMessage(
        role="user",
        content=f"请从以下文本中提取快递单号、收件人姓名、地址和联系方式，并以key:value的形式返回,注意快递单号不是订单号，通常在XX快递后面，联系方式可以是电话或者email,如果没有找到相关的值，则填充为null,这是我需要你处理的文本：\n\n{ocr_text}"
    )]
    try:
        response = spark.generate([messages])
        return response.generations[0][0].text if response else None
    except Exception as e:
        from logger import log_error
        log_error(f"大模型处理失败: {e}")
    return None

import re

def parse_extracted_info(extracted_info):
    """
    解析大模型返回的文本，提取快递单号、收件人姓名、地址和联系方式
    """
    data = {
        "快递单号": re.search(r"快递单号[:：]\s*(.+)", extracted_info).group(1).strip() if re.search(r"快递单号[:：]\s*(.+)", extracted_info) else "null",
        "收件人姓名": re.search(r"收件人姓名[:：]\s*(.+)", extracted_info).group(1).strip() if re.search(r"收件人姓名[:：]\s*(.+)", extracted_info) else "null",
        "地址": re.search(r"地址[:：]\s*(.+)", extracted_info).group(1).strip() if re.search(r"地址[:：]\s*(.+)", extracted_info) else "null",
        "联系方式": re.search(r"联系方式[:：]\s*(.+)", extracted_info).group(1).strip() if re.search(r"联系方式[:：]\s*(.+)", extracted_info) else "null",
    }

    # 提取电话和邮箱（如果有）
    # if "联系方式" in data and data["联系方式"] != "null":
    #     phone_match = re.search(r"TEL[:：]?\s*([\d-]+)", data["联系方式"])
    #     email_match = re.search(r"Email[:：]?\s*([\w.-]+@[\w.-]+)", data["联系方式"])
    #     data["电话"] = phone_match.group(1) if phone_match else "null"
    #     data["邮箱"] = email_match.group(1) if email_match else "null"
    # else:
    #     data["电话"] = "null"
    #     data["邮箱"] = "null"

    return data





