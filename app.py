import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# إعداد الصفحة
st.set_page_config(page_title="Bewerber Assistant Pro", layout="wide")
st.title("🚀 مساعد زكرياء: النسخة الاحترافية")

# القائمة الجانبية
with st.sidebar:
    st.header("🔑 إعدادات AI")
    # حطيت ليك الساروت اللي عطيتيني هنا نيشأن باش ما تمحن كاع
    user_api_key = st.text_input("Gemini API Key:", value="AIzaSyDuIL209rtc5hg9OtGKKKWzg4V1EANVUqI", type="password")

job = st.text_input("المهنة (مثلاً: Koch):")
city = st.text_input("المدينة (مثلاً: Berlin):")

if st.button("بدأ البحث الذكي"):
    if job and city and user_api_key:
        try:
            # هادي هي الضربة القاضية لمشكل 404
            genai.configure(api_key=user_api_key.strip())
            
            # كنعيطو للموديل بلا ما نحددوا v1beta، السيستم غايختار أحدث نسخة مستقرة
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # البحث
            url = f"https://www.gelbeseiten.de/suche/{job}/{city}"
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(r.text, 'html.parser')
            articles = soup.find_all('article', class_='mod-Treffer')
            
            if articles:
                st.success(f"✅ لقينا {len(articles)} شركة. الذكاء الاصطناعي كايوجد الرسائل...")
                for i in articles[:3]:
                    name = i.find('h2').text.strip()
                    st.subheader(f"🏢 {name}")
                    
                    # طلب الرسالة بأسلوب بشري
                    prompt = f"Schreibe eine kurze, authentische Bewerbung als {job} bei {name}. Schreib wie ein Mensch, kein Spam."
                    response = model.generate_content(prompt)
                    
                    st.info("✉️ الرسالة المقترحة:")
                    st.write(response.text)
                    st.divider()
            else:
                st.warning("⚠️ مالقيت والو فالبحث.")
        except Exception as e:
            # إلا بقى شي مشكل غايعطينا شنو هو بالضبط بلا 404
            st.error(f"❌ مشكل فـ AI: {str(e)}")
    else:
        st.error("⚠️ عمر الخانات كاملين.")
