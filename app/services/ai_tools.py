# services/ai_tools.py

from sqlalchemy import text
from app.database import SessionLocal
from datetime import date, datetime

def execute_read_only_query(sql_query: str):

    forbidden_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "TRUNCATE", "ALTER"]

    if any(keyword in sql_query.upper() for keyword in forbidden_keywords):
        return "Lỗi: Bạn chỉ có quyền truy vấn dữ liệu (SELECT)."

    db = SessionLocal()

    try:
        clean_query = sql_query.strip().rstrip(';')

        result = db.execute(text(clean_query))

        columns = result.keys()
        rows = result.fetchall()

        if not rows:
            return "Không tìm thấy dữ liệu phù hợp."

        data = []

        for row in rows:
            row_dict = dict(zip(columns, row))

            for k, v in row_dict.items():
                if isinstance(v, (date, datetime)):
                    row_dict[k] = v.isoformat()

            data.append(row_dict)

        if len(data) == 1 and len(columns) == 1:
            val = list(data[0].values())[0]
            return f"Kết quả: {val}"

        return data

    except Exception as e:
        return f"Lỗi thực thi SQL: {str(e)}"

    finally:
        db.close()