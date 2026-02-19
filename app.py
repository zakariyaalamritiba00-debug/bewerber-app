import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# إعداد الصفحة
st.set_page_config(page_title="Job Assistant Pro", layout="wide")
st.title("🚀 مساعد زكرياء الذكي")

# القائمة الجانبية للساروت
with st.sidebar:
    st.header("🔑 إعدادات AI")
    user_api_key = st.text_input("لصق Gemini API Key هنا:", type="password")

# المدخلات
job = st.text_input("المهنة (مثلاً: Koch):")
city = st.text_input("المدينة (مثلاً: Berlin):")

if st.button("بدأ البحث"):
    if job and city and user_api_key:
        try:
            # الربط مع أحدث نسخة مستقرة
            genai.configure(api_key=user_api_key.strip())
            # جرب هاد السمية بالضبط هي اللي خدامة دابا
            model = genai.GenerativeModel('gemini-1.5-flash-latest') 
            
            url = f"https://www.gelbeseiten.de/suche/{job}/{city}"
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(r.text, 'html.parser')
            articles = soup.find_all('article', class_='mod-Treffer')
            
            if articles:
                st.success(f"✅ لقينا {len(articles)} شركة.")
                for i in articles[:3]:
                    name = i.find('h2').text.strip() if i.find('h2') else "Firma"
                    st.subheader(f"🏢 {name}")
                    
                    # طلب الرسالة
                    prompt = f"Schreibe eine kurze, authentische Bewerbung als {job} bei {name}. Schreib wie ein Mensch, kein Spam."
                    response = model.generate_content(prompt)
                    
                    st.info("✉️ الرسالة المقترحة:")
                    st.write(response.text)
                    st.divider()
            else:
                st.warning("⚠️ مالقيت والو فـ البحث.")
        except Exception as e:
            # هادا غايخرج ليك مسج فيه الحل نيشأن إلا بقى مشكل
            st.error(f"❌ مشكل تقني: {str(e)}")
    else:
        st.error("⚠️ عافاك دخل المهنة، المدينة، ولصق الساروت فـ الجنب.")
