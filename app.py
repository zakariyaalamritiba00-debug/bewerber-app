import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# إعداد واجهة الموقع
st.set_page_config(page_title="Bewerber Assistant Pro", layout="wide")
st.title("🚀 مساعد زكرياء: النسخة الشغالة")

# القائمة الجانبية للساروت
with st.sidebar:
    st.header("🔑 إعدادات AI")
    user_api_key = st.text_input("لصق Gemini API Key هنا:", value="AIzaSyDuIL209rtc5hg9OtGKKKWzg4V1EANVUqI", type="password")
    st.info("💡 الساروت محطوط دابا، غير عمر المدن وبدا.")

# خانات البحث
col1, col2 = st.columns(2)
with col1:
    job = st.text_input("المهنة (مثلاً: Koch):")
with col2:
    city = st.text_input("المدينة (مثلاً: Berlin):")

if st.button("بدأ البحث الذكي"):
    if job and city and user_api_key:
        try:
            # الربط الصحيح اللي كيحيد خطأ 404
            genai.configure(api_key=user_api_key.strip())
            
            # كنستعملو هاد السمية بالضبط حيت هي اللي كتمشي مع السوارت الجداد
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # البحث عن الشركات
            url = f"https://www.gelbeseiten.de/suche/{job}/{city}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(url, headers=headers)
            soup = BeautifulSoup(r.text, 'html.parser')
            articles = soup.find_all('article', class_='mod-Treffer')
            
            if articles:
                st.success(f"✅ لقينا {len(articles)} شركة. الذكاء الاصطناعي خدام...")
                for i in articles[:3]:
                    name = i.find('h2').text.strip() if i.find('h2') else "الشركة"
                    st.subheader(f"🏢 {name}")
                    
                    # الأمر السحري للرسالة
                    prompt = f"Schreibe eine kurze, authentische Bewerbung als {job} bei {name}. Schreib wie ein Mensch, kein Spam."
                    response = model.generate_content(prompt)
                    
                    st.info("✉️ الرسالة المقترحة:")
                    st.write(response.text)
                    st.divider()
            else:
                st.warning("⚠️ مالقينا والو، جرب كلمات أخرى.")
        except Exception as e:
            # كشف الخطأ بوضوح
            st.error(f"❌ وقع مشكل: {str(e)}")
    else:
        st.error("⚠️ عافاك دخل المهنة والمدينة.")
