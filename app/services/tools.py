from langchain_core.tools import tool
from sqlalchemy import inspect
from app.database import SessionLocal
from app.services.ai_tools import execute_read_only_query

@tool
def get_database_schema() -> str:
    """
    Tra cứu cấu trúc Database. Trả về tên bảng và tên các cột thực tế. 
    Sử dụng công cụ này đầu tiên để tránh lỗi sai tên cột (như tenNganh vs tennganh).
    """
    db = SessionLocal()
    try:
        inspector = inspect(db.bind)
        schema_info = "Cấu trúc Database hiện tại:\n"
        for table in ["khoa", "nganh", "sinh_vien", "mon_hoc", "hoc_ky", "fact_diem"]:
            columns = [c["name"] for c in inspector.get_columns(table)]
            schema_info += f"- Bảng '{table}': [{', '.join(columns)}]\n"
        return schema_info
    finally:
        db.close()

@tool
def db_query_tool(sql_query: str) -> str:
    """
    Thực thi câu lệnh SQL SELECT đã được chuẩn hóa. 
    Chỉ nhận vào câu lệnh SELECT, không nhận các lệnh thay đổi dữ liệu.
    """
    return str(execute_read_only_query(sql_query))