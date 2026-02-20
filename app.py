import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

st.set_page_config(page_title="Job Search AI", layout="wide")
st.title("🚀 مساعد زكرياء للبحث عن عمل")

with st.sidebar:
    st.header("🔐 إعدادات الأمان")
    api_key = st.text_input("لصق Gemini API Key هنا:", type="password")

job = st.text_input("المهنة (مثلاً: Koch):")
city = st.text_input("المدينة (مثلاً: Berlin):")

if st.button("بدأ البحث وكتابة الرسائل"):
    if job and city and api_key:
        try:
            genai.configure(api_key=api_key.strip())
            
            # التعديل المهم هنا: استعملنا النسخة latest باش نتفاداو 404
            model = genai.GenerativeModel('gemini-1.5-flash-latest') 
            
            url = f"https://www.gelbeseiten.de/suche/{job}/{city}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(url, headers=headers)
            soup = BeautifulSoup(r.text, 'html.parser')
            articles = soup.find_all('article', class_='mod-Treffer')
            
            if articles:
                st.success(f"✅ لقينا {len(articles)} شركة.")
                for i in articles[:3]:
                    name = i.find('h2').text.strip() if i.find('h2') else "Firma"
                    st.subheader(f"🏢 {name}")
                    
                    prompt = f"Schreibe eine kurze Bewerbung als {job} bei {name}. Maximal 3 Sätze, menschlich."
                    response = model.generate_content(prompt)
                    
                    st.write(response.text)
                    st.divider()
            else:
                st.warning("⚠️ مالقيت والو فالبحث.")
        except Exception as e:
            # هاد المسج غايورينا دابا واش المشكل من الساروت ولا الموديل
            st.error(f"❌ وقع مشكل: {str(e)}")
    else:
        st.error("⚠️ دخل المعلومات كاملة.")
