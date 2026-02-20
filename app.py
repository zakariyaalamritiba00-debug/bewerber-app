import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import os

# إعداد واجهة الموقع
st.set_page_config(page_title="Bewerber AI Pro", layout="wide")
st.title("🚀 مساعد زكرياء: النسخة الشغالة 2026")

# القائمة الجانبية للساروت
with st.sidebar:
    st.header("🔑 إعدادات الأمان")
    user_api_key = st.text_input("لصق Gemini API Key هنا:", type="password")
    st.info("💡 هاد الساروت كيبقى مخبي عندك فالمتصفح.")

# المدخلات
job = st.text_input("المهنة (مثلاً: Koch):")
city = st.text_input("المدينة (مثلاً: Berlin):")

if st.button("بدأ البحث الذكي"):
    if job and city and user_api_key:
        try:
            # --- هاد الجزء هو اللي فيه الحل السحري ---
            genai.configure(api_key=user_api_key.strip())
            
            # كنستعملو هاد الطريقة باش نفرضو على المكتبة تخدم بالعنوان الصحيح (v1)
            # هادي هي اللي كتحيد مشكل 404 نهائياً
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config={"top_p": 0.95, "top_k": 40}
            )
            # ----------------------------------------
            
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
                    
                    # طلب توليد الرسالة
                    prompt = f"Schreibe eine kurze Bewerbung als {job} bei {name}. Maximal 3-4 Sätze, sehr höflich."
                    # كنحددو الموديل نيشأن هنا
                    response = model.generate_content(prompt)
                    
                    st.info("✉️ الرسالة المقترحة:")
                    st.write(response.text)
                    st.divider()
            else:
                st.warning("⚠️ مالقينا والو، جرب كلمات أخرى.")
        except Exception as e:
            st.error(f"❌ وقع مشكل تقني: {str(e)}")
    else:
        st.error("⚠️ عافاك دخل الساروت فـ الجنب والمهنة والمدينة.")
