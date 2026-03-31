import streamlit as st
import requests
import uuid
import base64

st.set_page_config(page_title="Hệ thống Quản lý Sinh viên AI", layout="wide", page_icon="🤖")

# 1. QUẢN LÝ TRẠNG THÁI (SESSION STATE)
# Khởi tạo các biến để lưu thông tin đăng nhập và lịch sử chat
if "token" not in st.session_state:
    st.session_state.token = None
if "role" not in st.session_state:
    st.session_state.role = None
if "username" not in st.session_state:
    st.session_state.username = None
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

def clear_chat():
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.messages = []

# 2. MÀN HÌNH ĐĂNG NHẬP (Chỉ hiện khi chưa có Token)
if st.session_state.token is None:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔐 Đăng nhập Hệ thống")
        st.markdown("Vui lòng đăng nhập để sử dụng AI Agent.")
        
        with st.form("login_form"):
            username = st.text_input("Tên đăng nhập (VD: admin, SV001, GV001)")
            password = st.text_input("Mật khẩu", type="password")
            submit_button = st.form_submit_button("Đăng nhập", use_container_width=True)
            
            if submit_button:
                if username and password:
                    with st.spinner("Đang xác thực..."):
                        try:
                            response = requests.post(
                                "http://127.0.0.1:8000/login",
                                data={"username": username, "password": password}
                            )
                            
                            if response.status_code == 200:
                                data = response.json()
                                # CẤT THẺ VÀO TÚI (Session State)
                                st.session_state.token = data["access_token"]
                                st.session_state.role = data.get("role", "Khach")
                                st.session_state.username = data.get("username", username)
                                clear_chat() # Reset chat cũ
                                st.rerun()   # Tải lại trang để vào màn hình chính
                            else:
                                st.error("❌ Tài khoản hoặc mật khẩu không chính xác!")
                        except Exception as e:
                            st.error(f"❌ Không thể kết nối tới Backend FastAPI: {e}")
                else:
                    st.warning("Vui lòng nhập đầy đủ thông tin.")

# 3. MÀN HÌNH CHÍNH (Chỉ hiện khi ĐÃ ĐĂNG NHẬP)
else:
    with st.sidebar:
        st.header("👤 Thông tin tài khoản")
        st.info(f"**Tài khoản:** {st.session_state.username}\n\n**Quyền hạn:** {st.session_state.role}")
        st.markdown("---")
        
        if st.button("🗑️ Xóa lịch sử chat", use_container_width=True):
            clear_chat()
            st.rerun()
            
        # Đăng xuất
        if st.button("🚪 Đăng xuất", type="primary", use_container_width=True):
            st.session_state.token = None
            st.session_state.role = None
            st.session_state.username = None
            clear_chat()
            st.rerun()

    # --- KHU VỰC CHAT CHÍNH ---
    st.title("🤖 AI Student Data Agent")
    
    # Hiển thị câu chào tùy theo quyền
    if st.session_state.role == "Admin":
        st.success("Bạn đang truy cập với quyền **Admin**. Bạn có thể tra cứu toàn bộ dữ liệu hệ thống.")
    else:
        st.warning(f"Bạn đang truy cập với quyền **{st.session_state.role}**. AI sẽ chỉ cung cấp dữ liệu liên quan trực tiếp đến bạn.")
    st.markdown("---")

    # In lại lịch sử chat lên màn hình
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("chart"):
                st.image(base64.b64decode(message["chart"]))

    # Khung nhập câu hỏi mới
    if prompt := st.chat_input("Hỏi AI về dữ liệu (VD: Điểm của tôi là bao nhiêu?)..."):
        # 1. In câu hỏi của User ra màn hình
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Gửi câu hỏi cho AI (BẮT BUỘC PHẢI KẸP THẺ)
        with st.chat_message("assistant"):
            with st.spinner("AI đang truy xuất dữ liệu an toàn..."):
                try:
                    # 🚀 BƯỚC QUAN TRỌNG NHẤT: Dán thẻ (Token) vào Header
                    headers = {
                        "Authorization": f"Bearer {st.session_state.token}"
                    }
                    
                    response = requests.post(
                        "http://127.0.0.1:8000/ai/chat",
                        json={
                            "question": prompt,
                            "thread_id": st.session_state.thread_id
                        },
                        headers=headers, # Chìa khóa qua cổng
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        answer = data.get("answer", "Không có câu trả lời.")
                        chart = data.get("chart")
                        
                        st.markdown(answer)
                        if chart:
                            st.image(base64.b64decode(chart))
                            
                        # Lưu câu trả lời vào lịch sử
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer,
                            "chart": chart
                        })
                        
                    # Xử lý các lỗi bảo mật Bác bảo vệ ném ra
                    elif response.status_code == 401:
                        st.error("Phiên đăng nhập đã hết hạn. Vui lòng đăng xuất và đăng nhập lại.")
                    elif response.status_code == 403:
                        st.error("Bạn không có quyền thực hiện thao tác này.")
                    else:
                        st.error(f"Lỗi hệ thống: {response.status_code} - {response.text}")
                except Exception as e:
                    st.error(f"Không thể kết nối Backend: {str(e)}")
