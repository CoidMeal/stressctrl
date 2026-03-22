import streamlit as st
import pandas as pd
import datetime
import os

# ---------- НАСТРОЙКА СТРАНИЦЫ ----------
st.set_page_config(page_title="Контроль состояния", layout="wide")

# ---------- СТИЛЬ (бело-оранжевый) ----------
st.markdown("""
<style>
body {
    background-color: white;
}
.stButton>button {
    background-color: orange;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ---------- БАЗА (CSV) ----------
DATA_FILE = "data.csv"

if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=[
        "time","S","M","E","Sleep",
        "psych_fatigue","phys_fatigue",
        "decisions","productivity","toxicity","qol"
    ])
    df.to_csv(DATA_FILE, index=False)

# ---------- ВКЛАДКИ ----------
tab1, tab2 = st.tabs(["📋 Тесты", "📊 Графики"])

# =====================================================
# =============== ВКЛАДКА ТЕСТЫ ========================
# =====================================================
with tab1:
    st.header("Ежедневное состояние")

    # Основные показатели
    S_raw = st.slider("Стресс", 1, 10)
    M_raw = st.slider("Настроение", 1, 10)
    E_raw = st.slider("Энергия", 1, 10)
    Sleep_raw = st.slider("Качество сна", 1, 10)

    st.divider()

    # Факторы
    work = st.slider("Нагрузка (работа)", 1, 10)
    finance = st.slider("Финансы", 1, 10)
    health = st.slider("Здоровье", 1, 10)
    family = st.slider("Семья", 1, 10)

    # Среднее A
    A = (work + finance + health + family) / 4

    st.write(f"Коэффициент A: {A:.2f}")

    st.divider()

    # События
    job_change = st.checkbox("Смена работы (+стресс)")
    move = st.checkbox("Переезд (-энергия)")
    loss = st.checkbox("Потеря близкого (-сон)")
    conflict = st.checkbox("Конфликт (-настроение)")

    # ---------- ПРИМЕНЕНИЕ ЛОГИКИ ----------
    S = S_raw
    M = M_raw * A
    E = E_raw * A
    Sleep = Sleep_raw * A

    # события
    if job_change:
        S += 1
    if move:
        E -= 1
    if loss:
        Sleep -= 1
    if conflict:
        M -= 1

    # нормализация 0–100
    S = min(max(S * 10, 0), 100)
    M = min(max(M * 10, 0), 100)
    E = min(max(E * 10, 0), 100)
    Sleep = min(max(Sleep * 10, 0), 100)

    st.divider()

    if st.button("💾 Сохранить"):
        # ---------- РАСЧЁТ МЕТРИК ----------
        psych = (S * 0.5 + (100 - E) * 0.3 + (100 - M) * 0.2)
        phys = ((100 - Sleep) * 0.6 + (100 - E) * 0.4)
        decisions = (M * 0.4 + E * 0.3 + Sleep * 0.2 - S * 0.3)
        productivity = (E * 0.5 + M * 0.3 - S * 0.2)
        toxicity = (S * 0.6 + (100 - M) * 0.4)
        qol = (M * 0.25 + E * 0.25 + Sleep * 0.2 + (100 - S) * 0.3)

        # ---------- СОХРАНЕНИЕ ----------
        new_row = pd.DataFrame([{
            "time": datetime.datetime.now(),
            "S": S,
            "M": M,
            "E": E,
            "Sleep": Sleep,
            "psych_fatigue": psych,
            "phys_fatigue": phys,
            "decisions": decisions,
            "productivity": productivity,
            "toxicity": toxicity,
            "qol": qol
        }])

        df = pd.read_csv(DATA_FILE)
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)

        st.success("Данные сохранены!")

# =====================================================
# =============== ВКЛАДКА ГРАФИКИ ======================
# =====================================================
with tab2:
    st.header("Графики")

    df = pd.read_csv(DATA_FILE)

    if df.empty:
        st.warning("Нет данных")
    else:
        df["time"] = pd.to_datetime(df["time"])

        st.subheader("Основные показатели")
        st.line_chart(df.set_index("time")[["S","M","E","Sleep"]])

        st.subheader("Производные показатели")
        st.line_chart(df.set_index("time")[[
            "psych_fatigue",
            "phys_fatigue",
            "decisions",
            "productivity",
            "toxicity",
            "qol"
        ]])
