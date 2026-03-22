import streamlit as st
import pandas as pd
import datetime
import os
import altair as alt

st.set_page_config(page_title="Стресс", layout="wide")

DATA_FILE = "data.csv"

if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["time","stress"])
    df.to_csv(DATA_FILE, index=False)

tab1, tab2, tab3 = st.tabs(["📋 Тест", "📊 График", "🎯 Сегодня"])

# =====================================================
# ================= ТЕСТ ===============================
# =====================================================
with tab1:
    st.header("Оцените состояние")

    q1 = st.slider("Уровень стресса", 1, 10)
    q2 = st.slider("Энергия", 1, 10)
    q3 = st.slider("Мышечная болезненность", 1, 10)
    q4 = st.slider("Сколько вы спали", 1, 10)
    q5 = st.slider("Качество сна", 1, 10)

    st.divider()

    q6 = st.radio("Настроение", [1,2])
    q7 = st.radio("Аппетит", [1,2])
    q8 = st.radio("Мотивация", [1,2])
    q9 = st.radio("Конфликт с близкими", [1,2])

    # ---------- РЕВЕРС ----------
    q2 = 11 - q2
    q4 = 11 - q4
    q5 = 11 - q5

    # ---------- РАСЧЁТ ----------
    base = (q1 + q2 + q3 + q4 + q5) / 50 * 100
    modifier = (q6 + q7 + q8 + q9) / 4

    stress = base * modifier / 2
    stress = min(max(stress, 0), 100)

    if st.button("💾 Сохранить"):
        new_row = pd.DataFrame([{
            "time": datetime.datetime.now(),
            "stress": stress
        }])

        df = pd.read_csv(DATA_FILE)
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)

        st.success("Сохранено")

# =====================================================
# ================= ГРАФИК =============================
# =====================================================
with tab2:
    st.header("График по дням")

    df = pd.read_csv(DATA_FILE)

    if df.empty:
        st.warning("Нет данных")
    else:
        df["time"] = pd.to_datetime(df["time"])
        df["date"] = df["time"].dt.date

        # среднее за день
        df_day = df.groupby("date")["stress"].mean().reset_index()

        chart = alt.Chart(df_day).mark_line(point=True).encode(
            x="date:T",
            y="stress:Q"
        ).properties(height=400)

        st.altair_chart(chart, use_container_width=True)

# =====================================================
# ================= СЕГОДНЯ ============================
# =====================================================
with tab3:
    st.header("Сегодня")

    df = pd.read_csv(DATA_FILE)

    if df.empty:
        st.warning("Нет данных")
    else:
        df["time"] = pd.to_datetime(df["time"])
        today = datetime.date.today()

        df_today = df[df["time"].dt.date == today]

        if df_today.empty:
            st.info("Сегодня нет данных")
        else:
            stress_today = df_today["stress"].mean()

            # цвет
            if stress_today >= 70:
                color = "red"
            elif stress_today >= 50:
                color = "orange"
            else:
                color = "green"

            # круг
            st.markdown(f"""
            <div style="
                width:300px;
                height:300px;
                border-radius:50%;
                border:15px solid {color};
                display:flex;
                align-items:center;
                justify-content:center;
                font-size:40px;
                margin:auto;
            ">
                {int(stress_today)}
            </div>
            """, unsafe_allow_html=True)
