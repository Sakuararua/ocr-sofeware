import os
import base64
import requests
from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler
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

# OCR 服务器URL
ocr_url = "http://127.0.0.1:1224/api/ocr"

# 发送图片进行 OCR 识别的函数
def ocr_recognition(image_path):
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
    response = requests.post(ocr_url, json=data)
    if response.status_code == 200:
        result = response.json()
        if result["code"] == 100:
            return result["data"]
        else:
            print(f"识别失败，错误原因：{result['data']}")
    else:
        print("OCR 请求失败，状态码：", response.status_code)
    return None

# 使用大模型提取关键信息的函数
def extract_delivery_info(ocr_text):
    messages = [ChatMessage(
        role="user",
        content=f"请从以下文本中提取快递单号、收件人姓名、地址和联系方式，并以key:value的形式返回,如果没有找到相关的值，则填充为null,
                    下面给出示例，假设我给出文本
                    Purchase Order No 6300094399 X000007725 162 X000007725017 VN BetaLightweightJacketM Remark Madein VietNam Color Chloris AmerSportsShanghaiTradingLtd 3F,Building2,759YangGaoRoad(S) PudongNewDistrict,Shanghai China200127 0623555 Qtytotal 22 Size L Factory 216991 EAN 421924 623555142192(01)00623555421924(20)VN(30)22 UPC
                    那这里的快递单号就是Purchase Order后面的6300094399，那返回结果以json的格式：\n\n{ocr_text}"
    )]
    handler = ChunkPrintHandler()
    response = spark.generate([messages], callbacks=[handler])
    return response  # 提取生成的文本内容

# 主函数，整合 OCR 和大模型处理
def main():
    image_folder = r"D:\Users\ASUS Vivobook\Desktop\ocr软件体系结构\ocr_lable"
    output_path = "ocr_extracted_results.txt"

    # 打开文件，准备写入结果
    with open(output_path, "w", encoding="utf-8") as output_file:
        # 读取文件夹中的前10个 JPG 文件
        images = [f for f in os.listdir(image_folder) if f.lower().endswith(".jpg")][:10]
        
        for image_file in images:
            image_path = os.path.join(image_folder, image_file)
            print(f"正在处理图片: {image_file}")

            # OCR 识别
            ocr_text = ocr_recognition(image_path)
            if ocr_text:
                # 大模型提取信息
                extracted_info = extract_delivery_info(ocr_text)
                output_file.write(f"图片: {image_file}\n")
                output_file.write(f"OCR 识别文本:\n{ocr_text}\n")
                output_file.write(f"提取的关键信息:\n{extracted_info}\n")
                output_file.write("\n" + "="*50 + "\n\n")
            else:
                output_file.write(f"图片: {image_file}\n")
                output_file.write("OCR 识别失败\n")
                output_file.write("\n" + "="*50 + "\n\n")

    print(f"所有处理结果已保存到 {output_path}")

if __name__ == '__main__':
    main()
