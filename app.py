import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# إعداد واجهة الموقع
st.set_page_config(page_title="Bewerber Assistant Pro", layout="wide")
st.title("🚀 مساعد زكرياء: النسخة الاحترافية")

# القائمة الجانبية
with st.sidebar:
    st.header("🔑 إعدادات AI")
    # حطيت ليك الساروت ديالك هنا نيشأن باش الموقع يخدم ديريكت
    user_api_key = st.text_input("Gemini API Key:", value="AIzaSyDuIL209rtc5hg9OtGKKKWzg4V1EANVUqI", type="password")

# خانات البحث
col1, col2 = st.columns(2)
with col1:
    job = st.text_input("المهنة (مثلاً: Koch):")
with col2:
    city = st.text_input("المدينة (مثلاً: Berlin):")

if st.button("بدأ البحث الذكي وكتابة الرسائل"):
    if job and city and user_api_key:
        try:
            # الربط الصحيح والمباشر
            genai.configure(api_key=user_api_key.strip())
            
            # استعملنا هاد الطريقة باش نتفاداو كاع مشاكل النسخ (v1beta, etc)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # عملية البحث فـ Gelbe Seiten
            url = f"https://www.gelbeseiten.de/suche/{job}/{city}"
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(r.text, 'html.parser')
            articles = soup.find_all('article', class_='mod-Treffer')
            
            if articles:
                st.success(f"✅ لقينا {len(articles)} شركة. الذكاء الاصطناعي كايوجد الرسائل...")
                for i in articles[:3]: # نختاروا أول 3 شركات
                    name = i.find('h2').text.strip() if i.find('h2') else "Firma"
                    st.subheader(f"🏢 {name}")
                    
                    # طلب الرسالة بأسلوب بشري
                    prompt = f"Schreibe eine kurze, authentische Bewerbung als {job} bei {name}. Schreib wie ein Mensch, kein Spam."
                    
                    # توليد النص
                    response = model.generate_content(prompt)
                    
                    st.info("✉️ الرسالة المقترحة:")
                    st.write(response.text)
                    st.divider()
            else:
                st.warning("⚠️ مالقيت والو فالبحث، جرب كلمات أخرى.")
        except Exception as e:
            # هنا غايعطينا السبب الحقيقي إلا بقى شي مشكل (مثلاً الساروت محتاج تفعيل)
            st.error(f"❌ مشكل تقني: {str(e)}")
    else:
        st.error("⚠️ عافاك دخل المهنة والمدينة.")
