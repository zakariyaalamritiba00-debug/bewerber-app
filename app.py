import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# إعداد الصفحة
st.set_page_config(page_title="Job Search AI 2026", layout="wide")
st.title("🚀 مساعد زكرياء الذكي")

# القائمة الجانبية
with st.sidebar:
    st.header("🔑 إعدادات الأمان")
    # الخانة غتكون خاوية باش تدخل الساروت الجديد ديالك
    user_api_key = st.text_input("لصق Gemini API Key هنا:", type="password")
    st.info("💡 استعمل الساروت اللي صاوبتي اليوم.")

# واجهة البحث
col1, col2 = st.columns(2)
with col1:
    job = st.text_input("المهنة (مثلاً: Koch):")
with col2:
    city = st.text_input("المدينة (مثلاً: Berlin):")

if st.button("بدأ البحث وكتابة الرسائل"):
    if job and city and user_api_key:
        try:
            # الحل السحري لمشكل 404
            genai.configure(api_key=user_api_key.strip(), transport='rest')
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # البحث
            url = f"https://www.gelbeseiten.de/suche/{job}/{city}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(url, headers=headers)
            soup = BeautifulSoup(r.text, 'html.parser')
            articles = soup.find_all('article', class_='mod-Treffer')
            
            if articles:
                st.success(f"✅ لقينا {len(articles)} شركة. الذكاء الاصطناعي كايوجد الرسائل...")
                for i in articles[:3]:
                    name = i.find('h2').text.strip() if i.find('h2') else "الشركة"
                    st.subheader(f"🏢 {name}")
                    
                    # طلب الرسالة
                    prompt = f"Schreibe eine kurze, authentische Bewerbung als {job} bei {name}. Schreib wie ein Mensch, maximal 4 Sätze."
                    response = model.generate_content(prompt)
                    
                    st.info("✉️ الرسالة المقترحة:")
                    st.write(response.text)
                    st.divider()
            else:
                st.warning("⚠️ مالقينا والو، جرب كلمات أخرى.")
        except Exception as e:
            st.error(f"❌ مشكل تقني: {str(e)}")
    else:
        st.error("⚠️ عافاك دخل الساروت والمعلومات.")
