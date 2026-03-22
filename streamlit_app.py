import streamlit as st
import pandas as pd
import datetime
import os

st.set_page_config(page_title="Контроль состояния", layout="wide")

# ---------- СТИЛЬ ----------
st.markdown("""
<style>
.stButton>button {
    background-color: orange;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ---------- БАЗА ----------
DATA_FILE = "data.csv"

if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["time","S","A","M"])
    df.to_csv(DATA_FILE, index=False)

# ---------- ВКЛАДКИ ----------
tab1, tab2 = st.tabs(["📋 Тест САН", "📊 График"])

# =====================================================
# ================= ТЕСТ САН ===========================
# =====================================================
with tab1:
    st.header("Оцените своё состояние")

    scale = [-3, -2, -1, 0, 1, 2, 3]

    st.subheader("Самочувствие")
    s1 = st.select_slider("Чувствую себя здоровым", options=scale)
    s2 = st.select_slider("Есть силы", options=scale)
    s3 = st.select_slider("Чувствую усталость", options=scale)

    st.subheader("Активность")
    a1 = st.select_slider("Я активен", options=scale)
    a2 = st.select_slider("Легко работать", options=scale)
    a3 = st.select_slider("Я вялый", options=scale)

    st.subheader("Настроение")
    m1 = st.select_slider("Я счастлив", options=scale)
    m2 = st.select_slider("Доволен собой", options=scale)
    m3 = st.select_slider("Мне грустно", options=scale)

    # ---------- ИНВЕРСИЯ НЕГАТИВНЫХ ----------
    s3 = -s3
    a3 = -a3
    m3 = -m3

    # ---------- РАСЧЁТ САН ----------
    S = (s1 + s2 + s3) / 3
    A = (a1 + a2 + a3) / 3
    M = (m1 + m2 + m3) / 3

    # перевод в 0–100
    def normalize(x):
        return (x + 3) / 6 * 100

    S = normalize(S)
    A = normalize(A)
    M = normalize(M)

    st.divider()

    if st.button("💾 Сохранить"):
        new_row = pd.DataFrame([{
            "time": datetime.datetime.now(),
            "S": S,
            "A": A,
            "M": M
        }])

        df = pd.read_csv(DATA_FILE)
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)

        st.success("Сохранено")

# =====================================================
# ================= ГРАФИК =============================
# =====================================================
with tab2:
    st.header("График состояния")

    df = pd.read_csv(DATA_FILE)

    if len(df) < 2:
        st.info("Нужно минимум 2 записи")
    else:
        df["time"] = pd.to_datetime(df["time"])

        st.subheader("Самочувствие, Активность, Настроение")
        st.caption("Чем выше значение - тем лучше состояние")

        st.line_chart(
            df.set_index("time")[["S", "A", "M"]]
    )
