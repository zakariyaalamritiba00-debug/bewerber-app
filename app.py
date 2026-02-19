import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

st.set_page_config(page_title="Job Assistant Pro", layout="wide")
st.title("🚀 مساعد زكرياء الذكي")

with st.sidebar:
    st.header("🔑 إعدادات AI")
    user_api_key = st.text_input("لصق Gemini API Key هنا:", type="password")

job = st.text_input("المهنة (مثلاً: Koch):")
city = st.text_input("المدينة (مثلاً: Berlin):")

if st.button("بدأ البحث"):
    if job and city and user_api_key:
        try:
            # إعداد Gemini
            genai.configure(api_key=user_api_key.strip()) # strip كتحيد الفراغات الزايدة
            model = genai.GenerativeModel('gemini-1.5-flash') # نسخة سريعة ومجانية
            
            url = f"https://www.gelbeseiten.de/suche/{job}/{city}"
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(r.text, 'html.parser')
            articles = soup.find_all('article', class_='mod-Treffer')
            
            if articles:
                st.success(f"✅ لقينا {len(articles)} شركة.")
                for i in articles[:3]:
                    name = i.find('h2').text.strip()
                    st.subheader(f"🏢 {name}")
                    
                    # طلب الرسالة
                    prompt = f"Schreibe eine kurze, authentische Bewerbung als {job} bei {name}."
                    response = model.generate_content(prompt)
                    st.info("✉️ الرسالة المقترحة:")
                    st.write(response.text)
                    st.divider()
            else:
                st.warning("⚠️ مالقيت حتى شركة، جرب مهنة أخرى.")
        except Exception as e:
            # هاد السطر غايطبع لينا الخطأ الحقيقي باش نحلوه
            st.error(f"❌ وقع خطأ: {str(e)}")
    else:
        st.error("⚠️ عافاك دخل المعلومات كاملة والساروت.")
