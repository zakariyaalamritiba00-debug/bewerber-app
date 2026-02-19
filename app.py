import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# إعدادات الصفحة
st.set_page_config(page_title="Bewerber Assistant Pro", layout="wide")
st.title("🚀 مساعد زكرياء للبحث عن عمل (نسخة الذكاء الاصطناعي)")

# القائمة الجانبية للساروت
with st.sidebar:
    st.header("🔑 إعدادات AI")
    user_api_key = st.text_input("لصق Gemini API Key (AIza...) هنا:", type="password")
    st.info("هاد الساروت كيجعل الرسائل تبان كأنها مكتوبة من إنسان.")

# مدخلات البحث
col1, col2 = st.columns(2)
with col1:
    job = st.text_input("المهنة (مثلاً: Koch)")
with col2:
    city = st.text_input("المدينة (مثلاً: Berlin)")

if st.button("بدأ البحث الذكي"):
    if job and city and user_api_key:
        try:
            # إعداد Gemini
            genai.configure(api_key=user_api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            # البحث عن الشركات
            url = f"https://www.gelbeseiten.de/suche/{job}/{city}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(url, headers=headers)
            soup = BeautifulSoup(r.text, 'html.parser')
            articles = soup.find_all('article', class_='mod-Treffer')
            
            if articles:
                st.success(f"✅ لقينا {len(articles)} شركة. الذكاء الاصطناعي كيوجد الرسائل...")
                for i in articles[:5]: # عرض أول 5 شركات
                    name = i.find('h2').text.strip() if i.find('h2') else "الشركة"
                    st.subheader(f"🏢 {name}")
                    
                    # الأمر اللي كيخلي اللغة بشرية وضد الـ Spam
                    prompt = f"""
                    Schreibe eine kurze, authentische Bewerbungs-E-Mail auf Deutsch für die Stelle als {job} bei der Firma {name} in {city}.
                    WICHTIG:
                    - Schreib wie ein echter Mensch (junger Bewerber), nicht wie eine KI.
                    - Keine Standard-Phrasen wie 'Hiermit bewerbe ich mich'.
                    - Halte es kurz, motiviert und professionell (B2 Niveau).
                    - Vermeide Spam-Strukturen.
                    """
                    
                    response = model.generate_content(prompt)
                    st.code(response.text, language="text")
                    st.divider()
            else:
                st.warning("⚠️ مالقينا والو، جرب كلمات بحث أبسط.")
        except Exception as e:
            st.error(f"❌ تأكد من الساروت (API Key): {e}")
    else:
        st.error("⚠️ عافاك دخل المهنة، المدينة، ولصق الساروت فـ الجنب.")
