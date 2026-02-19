import streamlit as st
import requests
from bs4 import BeautifulSoup

# كنحاولوا نثبتوا Gemini، وإلا ما كاينش ما نوقفوش الموقع
try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

st.set_page_config(page_title="Bewerber Assistant Pro", layout="wide")
st.title("🚀 مساعد زكرياء الذكي")

with st.sidebar:
    st.header("🔑 إعدادات AI")
    user_api_key = st.text_input("لصق Gemini API Key (AIza...) هنا:", type="password")

col1, col2 = st.columns(2)
with col1:
    job = st.text_input("المهنة (مثلاً: Koch)")
with col2:
    city = st.text_input("المدينة (مثلاً: Berlin)")

if st.button("بدأ البحث الذكي"):
    if job and city:
        url = f"https://www.gelbeseiten.de/suche/{job}/{city}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        articles = soup.find_all('article', class_='mod-Treffer')
        
        if articles:
            st.success(f"✅ لقينا {len(articles)} شركة.")
            for i in articles[:5]:
                name = i.find('h2').text.strip() if i.find('h2') else "الشركة"
                st.subheader(f"🏢 {name}")
                
                if HAS_GENAI and user_api_key:
                    genai.configure(api_key=user_api_key)
                    model = genai.GenerativeModel('gemini-pro')
                    prompt = f"Schreibe eine persönliche E-Mail für {job} bei {name}. Schreib wie ein Mensch, kein Spam."
                    response = model.generate_content(prompt)
                    st.code(response.text)
                else:
                    st.warning("⚠️ دخل الساروت (API Key) فـ الجنب باش نكتب ليك الرسالة.")
                st.divider()
        else:
            st.warning("مالقيت والو.")
    else:
        st.error("دخل المهنة والمدينة.")
