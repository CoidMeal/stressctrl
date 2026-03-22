import streamlit as st
import pandas as pd
import datetime
import os
import altair as alt

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

    def ask_block(title, questions):
        st.subheader(title)
        answers = []
        for q, reverse in questions:
            val = st.select_slider(q, options=scale, key=q)
            if reverse:
                val = -val
            answers.append(val)
        return sum(answers) / len(answers)

    # 10 вопросов на блок
    S_block = [
        ("Чувствую себя здоровым", False),
        ("Есть силы", False),
        ("Чувствую усталость", True),
        ("Я бодр", False),
        ("Чувствую слабость", True),
        ("Есть энергия", False),
        ("Чувствую себя разбитым", True),
        ("Физически хорошо себя чувствую", False),
        ("Есть напряжение в теле", True),
        ("Чувствую себя комфортно", False),
    ]

    A_block = [
        ("Я активен", False),
        ("Легко работать", False),
        ("Я вялый", True),
        ("Быстро включаюсь в дела", False),
        ("Хочу ничего не делать", True),
        ("Продуктивен", False),
        ("Тяжело начать", True),
        ("Много делаю", False),
        ("Нет сил двигаться", True),
        ("Полон энергии", False),
    ]

    M_block = [
        ("Я счастлив", False),
        ("Доволен собой", False),
        ("Мне грустно", True),
        ("Я спокоен", False),
        ("Чувствую тревогу", True),
        ("В хорошем настроении", False),
        ("Раздражён", True),
        ("Чувствую радость", False),
        ("Мне плохо", True),
        ("Чувствую гармонию", False),
    ]

    S = ask_block("Самочувствие", S_block)
    A = ask_block("Активность", A_block)
    M = ask_block("Настроение", M_block)

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

    if df.empty:
        st.warning("Нет данных")
    else:
        df["time"] = pd.to_datetime(df["time"])

        # ---------- ВЫБОР ПЕРИОДА ----------
        period = st.selectbox(
            "Период",
            ["Последние 3 дня", "Последние 7 дней", "Последние 30 дней"]
        )

        now = datetime.datetime.now()

        if period == "Последние 3 дня":
            df = df[df["time"] >= now - datetime.timedelta(days=3)]
        elif period == "Последние 7 дней":
            df = df[df["time"] >= now - datetime.timedelta(days=7)]
        else:
            df = df[df["time"] >= now - datetime.timedelta(days=30)]

        if len(df) < 2:
            st.info("Недостаточно данных")
        else:
            df_melt = df.melt(id_vars=["time"], value_vars=["S","A","M"],
                              var_name="Показатель", value_name="Значение")

            chart = alt.Chart(df_melt).mark_line(point=True).encode(
                x="time:T",
                y="Значение:Q",
                color="Показатель:N"
            ).properties(
                height=400
            )

            st.altair_chart(chart, use_container_width=True)    
