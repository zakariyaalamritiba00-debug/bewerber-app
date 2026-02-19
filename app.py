import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

st.set_page_config(page_title="Safe Job Assistant", layout="wide")
st.title("🚀 مساعد زكرياء الذكي (نسخة آمنة)")

# هادي هي الطريقة الصحيحة: الساروت كيدخل من واجهة الموقع
with st.sidebar:
    st.header("🔐 الأمان")
    user_api_key = st.text_input("لصق الساروت الجديد هنا:", type="password")
    st.info("💡 هاد الساروت غايبقى عندك فالمتصفح وما غايشوفوش GitHub.")

job = st.text_input("المهنة (مثلاً: Koch):")
city = st.text_input("المدينة (مثلاً: Berlin):")

if st.button("بدأ البحث"):
    if job and city and user_api_key:
        try:
            # تفعيل الساروت الجديد
            genai.configure(api_key=user_api_key.strip())
            # استعمل هاد الموديل نيشأن
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            url = f"https://www.gelbeseiten.de/suche/{job}/{city}"
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(r.text, 'html.parser')
            articles = soup.find_all('article', class_='mod-Treffer')
            
            if articles:
                st.success(f"✅ لقينا {len(articles)} شركة.")
                for i in articles[:3]:
                    name = i.find('h2').text.strip()
                    st.subheader(f"🏢 {name}")
                    response = model.generate_content(f"Schreibe eine kurze E-Mail für {job} bei {name}.")
                    st.write(response.text)
                    st.divider()
        except Exception as e:
            st.error(f"❌ وقع خطأ: {str(e)}")
    else:
        st.error("⚠️ عافاك دخل الساروت الجديد فـ الجنب والمهنة والمدينة.")
