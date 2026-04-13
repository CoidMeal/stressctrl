import streamlit as st
import pandas as pd
import datetime
import altair as alt
from supabase import create_client
# ---------- SUPABASE ----------
url = "https://wusyaloxkcaqojloosum.supabase.co"
key = "sb_publishable_eVZeidzDpvZk2vLhmwZgBg_4I-x9j5K"
supabase = create_client(url, key)

st.set_page_config(page_title="stressctrl", layout="wide")
# ---------- ВХОД ----------
if "user" not in st.session_state:
    st.title("Контроль стресса")

    name_input = st.text_input("", placeholder="Например: Игорь")

    if st.button("🚀 Начать", use_container_width=True):
        if name_input:
            st.session_state.user = name_input
            st.rerun()
        else:
            st.warning("Введите имя")

    st.stop()

user = st.session_state.user

if st.button("Сменить пользователя"):
    del st.session_state.user
    st.rerun()

# ---------- ВКЛАДКИ ----------
tab1, tab2, tab3 = st.tabs(["📋 Тесты", "📊 График", "🎯 Сегодня"])

# =====================================================
# ================= ТЕСТЫ ==============================
# =====================================================
with tab1:
    sub1, sub2 = st.tabs(["📅 Ежедневный тест", "🧠 Еженедельный САН"])

    # -------------------------------------------------
    # DAILY (ТВОЙ СТАРЫЙ)
    # -------------------------------------------------
    with sub1:
        st.header("Ежедневный тест")

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

        st.subheader(f"Стресс: {int(stress)}")

        if st.button("💾 Сохранить ежедневный", use_container_width=True):
            supabase.table("stress").insert({
                "user": user,
                "time": str(datetime.datetime.now()),
                "stress": float(stress),
                "type": "daily"
            }).execute()

            st.success("Сохранено")

    # -------------------------------------------------
    # SAN (30 ВОПРОСОВ)
    # -------------------------------------------------
    with sub2:
        st.header("Еженедельный тест САН")

        scale = [-3, -2, -1, 0, 1, 2, 3]

        def ask(q):
            return st.select_slider(q, options=scale, value=0)

        st.subheader("Самочувствие")
        S_list = [
            ask("Чувствую себя сильным"),
            ask("Чувствую усталость"),
            ask("Физически хорошо"),
            ask("Есть слабость"),
            ask("Чувствую бодрость"),
            ask("Есть напряжение"),
            ask("Хорошее самочувствие"),
            ask("Разбитость"),
            ask("Чувствую себя здоровым"),
            ask("Есть дискомфорт")
        ]

        st.subheader("Активность")
        A_list = [
            ask("Я активен"),
            ask("Мне сложно начать"),
            ask("Легко работать"),
            ask("Я вялый"),
            ask("Продуктивен"),
            ask("Нет сил"),
            ask("Быстро действую"),
            ask("Пассивен"),
            ask("Полон энергии"),
            ask("Не хочу ничего делать")
        ]

        st.subheader("Настроение")
        M_list = [
            ask("Я счастлив"),
            ask("Мне грустно"),
            ask("Я спокоен"),
            ask("Чувствую тревогу"),
            ask("Хорошее настроение"),
            ask("Раздражён"),
            ask("Чувствую радость"),
            ask("Мне плохо"),
            ask("Есть гармония"),
            ask("Негативное состояние")
        ]

        def normalize(x):
            return (sum(x)/len(x) + 3) / 6 * 100

        S = normalize(S_list)
        A = normalize(A_list)
        M = normalize(M_list)

        stress = 100 - (S + A + M) / 3

        st.subheader(f"Стресс: {int(stress)}")

        if st.button("💾 Сохранить САН", use_container_width=True):
            supabase.table("stress").insert({
                "user": user,
                "time": str(datetime.datetime.now()),
                "stress": float(stress),
                "type": "san"
            }).execute()

            st.success("Сохранено")

# =====================================================
# ================= ГРАФИК =============================
# =====================================================
with tab2:
    st.header("График")

    response = supabase.table("stress").select("*").eq("user", user).execute()
    df = pd.DataFrame(response.data)

    if df.empty:
        st.warning("Нет данных")
    else:
        df["time"] = pd.to_datetime(df["time"])
        df["date"] = df["time"].dt.date

        df_day = df.groupby("date")["stress"].mean().reset_index()
        df_day["date_str"] = df_day["date"].astype(str)

        chart = alt.Chart(df_day).mark_line(point=True).encode(
            x=alt.X("date_str:N", title="День"),
            y=alt.Y("stress:Q", scale=alt.Scale(domain=[0,100]))
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


