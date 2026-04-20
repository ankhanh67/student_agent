import sys
import os
import ast
import io
import base64
import pandas as pd
from sqlalchemy import text
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# --- 1. SỬA ĐƯỜNG DẪN THÀNH TUYỆT ĐỐI ---
# Lấy chính xác đường dẫn thư mục mcp_server và thư mục gốc của dự án
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

sys.path.insert(0, PROJECT_ROOT)
from app.database import SessionLocal
from mcp.server.fastmcp import FastMCP

# 3. KHỞI TẠO MCP SERVER
mcp = FastMCP("StudentManagementMCP", host="127.0.0.1", port=5000)

@mcp.tool()
def execute_read_only_query(sql_query: str) -> str:
    """Chạy câu lệnh SQL SELECT và trả về dữ liệu."""
    if not (sql_query.strip().lower().startswith("select") or sql_query.strip().lower().startswith("with")):
        return "Lỗi: Chỉ cho phép SELECT và WITH."

    db = SessionLocal()
    try:
        result = db.execute(text(sql_query.strip().rstrip(";")))
        columns = result.keys()
        return str([dict(zip(columns, row)) for row in result.fetchall()])
    except Exception as e:
        return f"Lỗi SQL: {str(e)}"
    finally:
        db.close()

@mcp.tool()
def plot_chart_tool(data: str, chart_type: str = "bar") -> str:
    """Vẽ chart từ data. Tham số chart_type: 'bar', 'pie', 'line'."""
    try:
        data_list = ast.literal_eval(data)
        df = pd.DataFrame(data_list)

        if df.empty or len(df.columns) < 2:
            return "Dữ liệu không đủ để vẽ biểu đồ."

        x, y = df.columns[0], df.columns[1]

        plt.clf()
        plt.figure(figsize=(8, 5))

        if chart_type == "pie":
            plt.pie(df[y], labels=df[x], autopct="%1.1f%%")
        elif chart_type == "line":
            plt.plot(df[x], df[y], marker='o', linestyle='-')
            plt.grid(True)
        else:
            plt.bar(df[x], df[y])
            plt.xticks(rotation=45, ha='right')

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        plt.close()
        buf.seek(0)
        
        # Mã hóa hình ảnh thành chuỗi Base64
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()

        # Trả về chuỗi Base64 trực tiếp cho AI
        return image_base64
        
    except Exception as e:
        return f"Lỗi vẽ biểu đồ: {str(e)}"

@mcp.resource("schema://database")
def get_db_schema() -> str:
    # Sửa lỗi: Cần dùng đường dẫn tuyệt đối khi đọc file Schema
    schema_path = os.path.join(PROJECT_ROOT, "app", "docs", "schema_database.md")
    with open(schema_path, "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    if "--sse" in sys.argv:
        print("🚀 Đang khởi chạy MCP Server (SSE Transport) tại http://127.0.0.1:5000/sse ...")
        mcp.run(transport="sse")
    else:
        mcp.run()
