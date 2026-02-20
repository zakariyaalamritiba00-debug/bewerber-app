import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# إعداد الصفحة
st.set_page_config(page_title="Bewerber AI Pro", layout="wide")
st.title("🚀 مساعد زكرياء الذكي")

# القائمة الجانبية للساروت
with st.sidebar:
    st.header("🔑 إعدادات الأمان")
    user_api_key = st.text_input("لصق Gemini API Key هنا:", type="password")
    st.info("💡 استعمل الساروت اللي صاوبتي اليوم (الجديد).")

# المدخلات
col1, col2 = st.columns(2)
with col1:
    job = st.text_input("المهنة (مثلاً: Koch):")
with col2:
    city = st.text_input("المدينة (مثلاً: Berlin):")

if st.button("بدأ البحث وكتابة الرسائل"):
    if job and city and user_api_key:
        try:
            # --- هادا هو السطر السحري اللي غايحيد 404 ---
            # كنفرضوا على المكتبة تستعمل البروتوكول المستقر (rest)
            genai.configure(api_key=user_api_key.strip(), transport='rest')
            
            # استعمال الموديل نيشأن
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # البحث في Gelbe Seiten
            url = f"https://www.gelbeseiten.de/suche/{job}/{city}"
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(r.text, 'html.parser')
            articles = soup.find_all('article', class_='mod-Treffer')
            
            if articles:
                st.success(f"✅ لقينا {len(articles)} شركة. الذكاء الاصطناعي خدام...")
                for i in articles[:3]:
                    name = i.find('h2').text.strip() if i.find('h2') else "الشركة"
                    st.subheader(f"🏢 {name}")
                    
                    # طلب الرسالة
                    response = model.generate_content(f"Schreibe eine kurze Bewerbung als {job} bei {name}. Maximal 4 Sätze.")
                    
                    st.info("✉️ الرسالة المقترحة:")
                    st.write(response.text)
                    st.divider()
            else:
                st.warning("⚠️ مالقيت والو فالبحث.")
        except Exception as e:
            st.error(f"❌ مشكل تقني: {str(e)}")
    else:
        st.error("⚠️ دخل المعلومات والساروت.")
