import streamlit as st
import pandas as pd
import datetime
import altair as alt
from supabase import create_client

# ---------- SUPABASE ----------
url = "https://PROJECT_ID.supabase.com"
key = "sb_publishable_eVZeidzDpvZk2vLhmwZgBg_4I-x9j5K"
supabase = create_client(url, key)

st.set_page_config(page_title="Стресс", layout="wide")

st.title("Контроль стресса")

user = st.text_input("Введите имя", placeholder="Например: Иван")

if not user:
    st.stop()

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

    q6 = st.radio("Настроение", [0,1,2])
    q7 = st.radio("Аппетит", [0,1,2])
    q8 = st.radio("Мотивация", [0,1,2])
    q9 = st.radio("Конфликт с близкими", [0,1,2])

    # реверс
    q2 = 11 - q2
    q4 = 11 - q4
    q5 = 11 - q5
    q6 = 2 - q6
    q7 = 2 - q7
    q8 = 2 - q8

    base = (q1 + q2 + q3 + q4 + q5) / 50 * 100
    modifier = (q6 + q7 + q8 + q9) / 4

    stress = base * modifier / 2
    stress = min(max(stress, 0), 100)

    st.subheader(f"Текущий стресс: {int(stress)}")

    if st.button("💾 Сохранить"):
        supabase.table("stress").insert({
            "user": user,
            "time": str(datetime.datetime.now()),
            "stress": float(stress)
        }).execute()

        st.success("Сохранено")

# =====================================================
# ================= ГРАФИК =============================
# =====================================================
with tab2:
    st.header("График по дням")

    response = supabase.table("stress").select("*").eq("user", user).execute()
    df = pd.DataFrame(response.data)

    if df.empty:
        st.warning("Нет данных")
    else:
        df["time"] = pd.to_datetime(df["time"])
        df["date"] = df["time"].dt.date

        df_day = df.groupby("date")["stress"].mean().reset_index()
        df_day["date_str"] = df_day["date"].astype(str)

        period = st.selectbox("Период", ["3 дня", "7 дней", "30 дней"])

        today = datetime.date.today()

        if period == "3 дня":
            df_day = df_day[df_day["date"] >= today - datetime.timedelta(days=3)]
        elif period == "7 дней":
            df_day = df_day[df_day["date"] >= today - datetime.timedelta(days=7)]
        else:
            df_day = df_day[df_day["date"] >= today - datetime.timedelta(days=30)]

        chart = alt.Chart(df_day).mark_line(point=True).encode(
            x=alt.X("date_str:N", title="День"),
            y=alt.Y("stress:Q", scale=alt.Scale(domain=[0,100])),
            tooltip=["date_str", "stress"]
        )

        st.altair_chart(chart, use_container_width=True)

# =====================================================
# ================= СЕГОДНЯ ============================
# =====================================================
with tab3:
    st.header("Сегодня")

    response = supabase.table("stress").select("*").eq("user", user).execute()
    df = pd.DataFrame(response.data)

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

            if stress_today >= 70:
                color = "red"
            elif stress_today >= 50:
                color = "orange"
            else:
                color = "green"

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
