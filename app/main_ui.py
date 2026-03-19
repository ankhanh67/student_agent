import streamlit as st
import requests
import uuid
import base64

st.set_page_config(page_title="Hệ thống Trợ lý Giáo vụ AI", layout="wide")

st.title("🤖 AI Student Data Agent")
st.markdown("---")


# =============================
# 1. SESSION STATE
# =============================

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []


# =============================
# 2. BUILD HISTORY
# =============================

def build_history(messages):
    history = ""
    for m in messages:
        role = "User" if m["role"] == "user" else "Assistant"
        history += f"{role}: {m['content']}\n"
    return history


# =============================
# 3. HIỂN THỊ LỊCH SỬ CHAT
# =============================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if message.get("chart"):
            st.image(base64.b64decode(message["chart"]))


# =============================
# 4. XỬ LÝ INPUT
# =============================

if prompt := st.chat_input("Bạn muốn hỏi gì về dữ liệu sinh viên?"):

    # Hiển thị user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # Tạo history
    history = build_history(st.session_state.messages)

    with st.chat_message("assistant"):

        with st.spinner("AI đang truy vấn dữ liệu..."):

            try:

                response = requests.post(
                    "http://127.0.0.1:8000/ai/chat",
                    json={
                        "question": prompt,
                        "thread_id": st.session_state.thread_id,
                        "history": history
                    },
                    timeout=60
                )

                if response.status_code == 200:

                    data = response.json()

                    answer = data.get("answer", "Không có câu trả lời.")
                    chart = data.get("chart")

                    st.markdown(answer)

                    if chart:
                        st.image(base64.b64decode(chart))

                    # lưu history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "chart": chart
                    })

                else:

                    st.error(
                        f"Lỗi hệ thống: {response.status_code} - {response.text}"
                    )

            except Exception as e:

                st.error(
                    f"Không thể kết nối tới Backend: {str(e)}"
                )


# =============================
# 5. SIDEBAR
# =============================

with st.sidebar:

    st.header("Thông tin hệ thống")

    st.info(f"Thread ID:\n{st.session_state.thread_id}")

    st.divider()

    if st.button("🗑 Xóa lịch sử chat"):

        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())

        st.rerun()

    st.divider()

    # Debug
    with st.expander("🔎 Debug Messages"):

        st.write(st.session_state.messages)
