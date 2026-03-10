from google import genai
from sqlalchemy.orm import Session
import os
import json

from dotenv import load_dotenv

from app.services.ai_tools import execute_read_only_query
from app.prompts.prompts import SYSTEM_PROMPT

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


def clean_sql(raw_sql: str) -> str:
    """
    Loại bỏ markdown từ câu SQL do LLM sinh ra
    """
    clean = raw_sql.replace("```sql", "").replace("```", "")
    clean = clean.replace("\n", " ").strip()
    # FIX SQLite syntax -> PostgreSQL
    clean = clean.replace("STRFTIME('%Y',", "EXTRACT(YEAR FROM")
    return clean.rstrip(";")


def ask_student_agent(user_question: str, db: Session):

    try:

        # =============================
        # BƯỚC 1: LLM sinh SQL
        # =============================

        response_sql = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            config={"system_instruction": SYSTEM_PROMPT},
            contents=user_question
        )

        sql_query = clean_sql(response_sql.text)

        print("\n===== GENERATED SQL =====")
        print(sql_query)
        print("=========================\n")
        # =============================
        # BƯỚC 2: Query Database
        # =============================

        data = execute_read_only_query(sql_query)

        if not data or data == "Không tìm thấy dữ liệu phù hợp.":
            return "Hệ thống không tìm thấy dữ liệu phù hợp."

        # =============================
        # BƯỚC 3: LLM tổng hợp câu trả lời
        # =============================

        final_prompt = f"""
Bạn là trợ lý giáo vụ của hệ thống quản lý sinh viên.

Câu hỏi của người dùng:
{user_question}

Dữ liệu từ hệ thống (JSON):
{json.dumps(data, ensure_ascii=False)}

Hãy trả lời câu hỏi dựa trên dữ liệu trên.
Trả lời ngắn gọn, rõ ràng, bằng tiếng Việt.
"""

        response_final = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=final_prompt
        )

        return response_final.text

    except Exception as e:

        error_msg = str(e)

        if "429" in error_msg:
            return "Hệ thống đang quá tải, vui lòng thử lại sau."

        if "503" in error_msg:
            return "Dịch vụ AI tạm thời không khả dụng."

        return f"Lỗi hệ thống: {error_msg}"