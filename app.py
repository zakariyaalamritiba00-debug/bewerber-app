import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# إعداد واجهة الموقع
st.set_page_config(page_title="Job Assistant Pro", layout="wide")
st.title("🚀 مساعد زكرياء الذكي")

# القائمة الجانبية
with st.sidebar:
    st.header("🔑 إعدادات الأمان")
    user_api_key = st.text_input("لصق Gemini API Key هنا:", type="password")
    st.info("💡 استعمل الساروت الجديد اللي صاوبتي.")

# خانات البحث
col1, col2 = st.columns(2)
with col1:
    job = st.text_input("المهنة (مثلاً: Koch):")
with col2:
    city = st.text_input("المدينة (مثلاً: Berlin):")

if st.button("بدأ البحث وكتابة الرسائل"):
    if job and city and user_api_key:
        try:
            # --- هادا هو السطر اللي غايحل مشكل 404 نهائياً ---
            genai.configure(api_key=user_api_key.strip(), transport='rest')
            
            # كنعيطو للموديل نيشأن بلا v1beta بلا والو
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # عملية البحث فـ Gelbe Seiten
            url = f"https://www.gelbeseiten.de/suche/{job}/{city}"
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(r.text, 'html.parser')
            articles = soup.find_all('article', class_='mod-Treffer')
            
            if articles:
                st.success(f"✅ لقينا {len(articles)} شركة. الذكاء الاصطناعي كايوجد الرسائل...")
                for i in articles[:3]:
                    name = i.find('h2').text.strip() if i.find('h2') else "الشركة"
                    st.subheader(f"🏢 {name}")
                    
                    # طلب الرسالة
                    prompt = f"Schreibe eine kurze Bewerbung als {job} bei {name}. Maximal 4 Sätze."
                    response = model.generate_content(prompt)
                    
                    st.info("✉️ الرسالة المقترحة:")
                    st.write(response.text)
                    st.divider()
            else:
                st.warning("⚠️ مالقيت والو فالبحث.")
        except Exception as e:
            # هاد المسج غايأكد لينا النجاح
            st.error(f"❌ مشكل تقني: {str(e)}")
    else:
        st.error("⚠️ عافاك دخل الساروت والمعلومات.")
