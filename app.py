import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# إعداد الصفحة
st.set_page_config(page_title="Bewerber AI Pro", layout="wide")
st.title("🚀 مساعد زكرياء الذكي")

# القائمة الجانبية للساروت
with st.sidebar:
    st.header("🔑 إعدادات AI")
    user_api_key = st.text_input("لصق الساروت الجديد هنا:", type="password")
    st.info("💡 هاد الساروت هو اللي كيخلي AI يكتب الرسائل.")

# خانات البحث
job = st.text_input("المهنة (مثلاً: Koch):")
city = st.text_input("المدينة (مثلاً: Berlin):")

if st.button("بدأ البحث والذكاء الاصطناعي"):
    if job and city and user_api_key:
        try:
            # --- هادا هو السطر اللي غايحل مشكل 404 ---
            genai.configure(api_key=user_api_key.strip(), transport='rest') 
            
            # كنعيطو للموديل بلا "-latest" وبلا تعقيدات
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # عملية البحث
            url = f"https://www.gelbeseiten.de/suche/{job}/{city}"
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(r.text, 'html.parser')
            articles = soup.find_all('article', class_='mod-Treffer')
            
            if articles:
                st.success(f"✅ لقينا {len(articles)} شركة. الذكاء الاصطناعي كايوجد الرسائل...")
                for i in articles[:3]:
                    name = i.find('h2').text.strip()
                    st.subheader(f"🏢 {name}")
                    
                    # طلب الرسالة
                    response = model.generate_content(f"Schreibe eine kurze Bewerbung als {job} bei {name}.")
                    
                    st.info("✉️ الرسالة المقترحة:")
                    st.write(response.text)
                    st.divider()
            else:
                st.warning("⚠️ مالقيت والو فالبحث.")
        except Exception as e:
            # هنا غايبان لينا واش باقي داك 404 ولا تهنينا منو
            st.error(f"❌ مشكل تقني: {str(e)}")
    else:
        st.error("⚠️ عافاك دخل الساروت والمعلومات.")
