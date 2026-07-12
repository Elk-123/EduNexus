import os
from dotenv import load_dotenv

# 1. 首先加载 .env 文件中的配置
load_dotenv()

# ========================================================
# 2. 自动修复 Windows 系统的 SSL_CERT_FILE 路径失效问题
# ========================================================
import certifi
if "SSL_CERT_FILE" in os.environ:
    current_cert_path = os.environ["SSL_CERT_FILE"]
    # 如果环境变量中设置了路径，但是该路径下的文件不存在
    if not os.path.exists(current_cert_path):
        # 将其重置为当前 Python 环境内置的、绝对存在的证书文件路径
        os.environ["SSL_CERT_FILE"] = certifi.where()
else:
    os.environ["SSL_CERT_FILE"] = certifi.where()
# ========================================================

# 3. 之后再正常导入 LangChain 代码（以 DeepSeek 为例）
from langchain_openai import ChatOpenAI

print("当前测试项目:", os.getenv("LANGCHAIN_PROJECT"))

# 初始化 DeepSeek 
llm = ChatOpenAI(
    model=os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash"),
    openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
    openai_api_base="https://api.deepseek.com/v1" 
)

try:
    print("正在发送请求到 DeepSeek...")
    response = llm.invoke("你好，这是一次测试连接。")
    print("模型回复:", response.content)
    print("\n--- [成功] 请登录 LangSmith 网页端查看数据 ---")
except Exception as e:
    print("发送失败，错误信息:", e)