import streamlit as st
import requests
from bs4 import BeautifulSoup

# محاولة تحميل مكتبة الذكاء الاصطناعي
try:
    import google.generativeai as genai
    HAS_AI = True
except ImportError:
    HAS_AI = False

st.set_page_config(page_title="Job Assistant Pro", layout="wide")
st.title("🚀 مساعد زكرياء الذكي للبحث عن عمل")

# القائمة الجانبية للساروت
with st.sidebar:
    st.header("🔑 إعدادات AI")
    user_api_key = st.text_input("لصق Gemini API Key هنا:", type="password")
    st.info("هاد الساروت هو اللي كيخلي AI يكتب ليك الرسائل بأسلوب بشري.")

# خانات الإدخال
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
            st.success(f"✅ لقينا {len(articles)} شركة مستهدفة.")
            for i in articles[:5]: # عرض أول 5 شركات
                name = i.find('h2').text.strip() if i.find('h2') else "Firma"
                st.subheader(f"🏢 {name}")
                
                # إذا كان الساروت موجود، يكتب الرسالة
                if HAS_AI and user_api_key:
                    genai.configure(api_key=user_api_key)
                    model = genai.GenerativeModel('gemini-pro')
                    prompt = f"Schreibe eine kurze, persönliche E-Mail für die Stelle als {job} bei {name}. Schreib wie ein Mensch, kein Spam."
                    try:
                        response = model.generate_content(prompt)
                        st.code(response.text, language="text")
                    except:
                        st.error("مشكل فـ الساروت، تأكد منه.")
                else:
                    st.warning("⚠️ دخل API Key فـ الجنب باش نكتب ليك الرسالة.")
                st.divider()
        else:
            st.warning("مالقينا والو، جرب كلمات أبسط.")
    else:
        st.error("عافاك دخل المهنة والمدينة.")
