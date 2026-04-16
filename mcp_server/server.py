import sys
import os
import ast
import uuid
import pandas as pd
import threading
import http.server
import socketserver
import functools
from datetime import date, datetime
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

# 2. CẤU HÌNH MINI FILE SERVER CHO MCP (Dùng đường dẫn tuyệt đối)
MCP_CHART_DIR = os.path.join(CURRENT_DIR, "charts") # Tạo thư mục charts bên trong mcp_server
os.makedirs(MCP_CHART_DIR, exist_ok=True)
MCP_IMAGE_PORT = 8001 

# THÊM CLASS NÀY: Tắt toàn bộ log của HTTP Server để không làm hỏng Stdio của MCP
class QuietHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass # Bỏ qua, không in ra màn hình console

def start_static_file_server():
    """Chạy một HTTP Server nhỏ trên port 8001 (Chế độ im lặng)"""
    try:
        handler = functools.partial(QuietHTTPHandler, directory=MCP_CHART_DIR)
        # Cho phép dùng lại port để tránh lỗi "Address already in use" khi restart
        socketserver.TCPServer.allow_reuse_address = True 
        
        # Đổi "" thành "127.0.0.1" để Windows không bị nhầm lẫn
        with socketserver.TCPServer(("127.0.0.1", MCP_IMAGE_PORT), handler) as httpd:
            httpd.serve_forever()
    except Exception as e:
        # Ghi log ra file txt thay vì print để dễ debug nếu vẫn lỗi
        error_log_path = os.path.join(PROJECT_ROOT, "mcp_server_error.log")
        with open(error_log_path, "a") as f:
            f.write(f"HTTP Server Error: {str(e)}\n")

# Chạy File Server ở một luồng (thread) ngầm
threading.Thread(target=start_static_file_server, daemon=True).start()


# 3. KHỞI TẠO MCP SERVER
mcp = FastMCP("StudentManagementMCP")

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
        
        # Lưu file vào thư mục riêng của MCP Server
        filename = f"chart_{uuid.uuid4().hex}.png"
        filepath = os.path.join(MCP_CHART_DIR, filename)
        plt.savefig(filepath, format="png")
        plt.close()

        # TRẢ VỀ ĐƯỜNG DẪN MẠNG (HTTP URL)
        return f"http://127.0.0.1:{MCP_IMAGE_PORT}/{filename}"
        
    except Exception as e:
        return f"Lỗi vẽ biểu đồ: {str(e)}"

@mcp.resource("schema://database")
def get_db_schema() -> str:
    # Sửa lỗi: Cần dùng đường dẫn tuyệt đối khi đọc file Schema
    schema_path = os.path.join(PROJECT_ROOT, "app", "docs", "schema_database.md")
    with open(schema_path, "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    # Đây chính là lệnh chạy STDIO để giao tiếp với Claude
    mcp.run()
    