from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

print("Danh sách model khả dụng trên Key của bạn:")
# Chỉ in ra tên model để tránh lỗi thuộc tính
for m in client.models.list():
    print(f"- {m.name}")