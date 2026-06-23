import streamlit as st
import json
import database as db
from openai import OpenAI

# Инициализация
db.init_db()

# --- КОНФИГУРАЦИЯ ИИ ---
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=GROQ_API_KEY)

# --- НАСТРОЙКИ СТРАНИЦЫ И CSS ---
st.set_page_config(page_title="AI Lifestyle Balancer", page_icon="⚖️", layout="wide")

# Кастомный CSS для центрирования и красоты
st.markdown("""
    <style>
    .main { text-align: center; }
    .stTextArea textarea { font-size: 1.1rem !important; }
    [data-testid="stMetricValue"] { font-size: 1.8rem !important; }
    .centered-header { text-align: center; margin-bottom: 2rem; }
    </style>
""", unsafe_allow_html=True)

# --- ЗАГОЛОВОК (ПО ЦЕНТРУ) ---
st.markdown("<div class='centered-header'><h1>⚖️ Lifestyle Balancer AI</h1><h3>Твой день под контролем искусственного интеллекта</h3></div>", unsafe_allow_html=True)

# --- БЛОК МЕТРИК (Чтобы не было пусто) ---
total, work, health = db.get_stats()
m_col1, m_col2, m_col3, m_col4 = st.columns(4)
m_col1.metric("Всего задач", total)
m_col2.metric("Работа/Учеба", work)
m_col3.metric("Здоровье/Отдых", health)
balance_score = "Идеально" if total > 0 and abs(work - health) <= 1 else "Требует внимания"
m_col4.metric("Статус баланса", balance_score)

st.divider()

# --- ВВОД (СВЕРХУ) ---
# Используем контейнер для центрирования поля ввода
container = st.container()
with container:
    col1, col2, col3 = st.columns([1, 2, 1]) # Боковые колонки пустые для центрирования
    with col2:
        st.markdown("##### 💬 Расскажи ИИ о своих планах:")
        user_prompt = st.text_area(
            "Что нужно сделать сегодня?", 
            height=100, 
            label_visibility="collapsed",
            placeholder="Напиши: сходить в зал, доделать отчет, купить продукты..."
        )
        submit_btn = st.button("🪄 Сбалансировать мой день", use_container_width=True, type="primary")

st.divider()

# --- ВЫВОД РЕЗУЛЬТАТОВ (СНИЗУ) ---
st.markdown("<h4 style='text-align: center;'>🗓️ Твое персональное расписание</h4>", unsafe_allow_html=True)

SYSTEM_PROMPT = """
Ты — ИИ-агент управления временем. Распредели задачи пользователя по времени, 
чередуя категории: "Работа/Учеба", "Быт/Рутина" и "Здоровье/Отдых".
Ответь СТРОГО JSON-массивом объектов с полями time_slot, category, task_text.
"""

if submit_btn and user_prompt:
    with st.spinner("🧠 Агент анализирует данные..."):
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                model="llama-3.1-8b-instant",
                temperature=0.2,
            )
            raw_json = chat_completion.choices[0].message.content
            schedule = json.loads(raw_json)
            db.save_schedule(schedule)
            st.rerun() # Перезагружаем страницу, чтобы обновить метрики и список
        except Exception as e:
            st.error(f"Ошибка ИИ: {e}")

# Вывод списка задач в виде красивых карточек
current_tasks = db.get_all_tasks()
if current_tasks:
    # Разделим на 3 колонки для красивой сетки
    t_col1, t_col2, t_col3 = st.columns(3)
    cols = [t_col1, t_col2, t_col3]
    
    for idx, item in enumerate(current_tasks):
        emoji = "💻" if "Работа" in item['category'] else "🔋" if "Здоровье" in item['category'] else "🧹"
        with cols[idx % 3]:
            st.info(f"**{item['time_slot']}**\n\n{emoji} **{item['category']}**\n\n{item['task_text']}")
else:
    st.markdown("<p style='text-align: center; color: gray;'>Здесь появится твой план на день. Введи задачи выше!</p>", unsafe_allow_html=True)