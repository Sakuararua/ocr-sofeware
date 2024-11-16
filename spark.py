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

# 模板化提取内容函数
def extract_delivery_info(ocr_text):
    # 格式化消息请求内容
    messages = [ChatMessage(
        role="user",
        content=f"请从以下文本中提取快递单号、收件人姓名、地址和联系方式，并以key:value的形式返回,如果没有找到相关的值，则填充为null,返回结果以json的格式：\n\n{ocr_text}"
    )]
    handler = ChunkPrintHandler()  # 用于打印分块响应
    response = spark.generate([messages], callbacks=[handler])
    return response

# 示例OCR结果列表
ocr_results = [
 "PurchaseOrderNo 6300094579 X00000605701 X000006057002 HELIAD15LBACKPACK Remark VN AmerSportsShanghai TradingLtd 3F,Building2,759YangGaoRoad(S) PudongNewDistrict,Shanghal China200127 Madein VIETNAM Color BLACK QtyTotal 35 Size ONESIZE Factory 152504 0686487724457 68648772445 7 (01)00686487724457(20)VN(30)35 EAN UPC"
   
]

# 批量处理每条 OCR 结果
for ocr_text in ocr_results:
    extracted_info = extract_delivery_info(ocr_text)
    print(f"提取结果:\n{extracted_info}\n")
