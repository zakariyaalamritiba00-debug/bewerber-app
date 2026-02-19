import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# إعداد الصفحة
st.set_page_config(page_title="Job Search AI", layout="wide")
st.title("🚀 مساعد زكرياء للبحث عن عمل")

# القائمة الجانبية (هنا فين غتحط الساروت ملي يفتح الموقع)
with st.sidebar:
    st.header("🔐 إعدادات الأمان")
    api_key = st.text_input("لصق Gemini API Key هنا:", type="password")
    st.info("💡 هاد الساروت كيبقى مخبي وكايخلي الموقع يخدم بالذكاء الاصطناعي.")

# واجهة البحث
col1, col2 = st.columns(2)
with col1:
    job = st.text_input("المهنة (مثلاً: Koch):")
with col2:
    city = st.text_input("المدينة (مثلاً: Berlin):")

if st.button("بدأ البحث وكتابة الرسائل"):
    if job and city and api_key:
        try:
            # تفعيل الذكاء الاصطناعي
            genai.configure(api_key=api_key.strip())
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # البحث عن الشركات في ألمانيا
            url = f"https://www.gelbeseiten.de/suche/{job}/{city}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(url, headers=headers)
            soup = BeautifulSoup(r.text, 'html.parser')
            articles = soup.find_all('article', class_='mod-Treffer')
            
            if articles:
                st.success(f"✅ لقينا {len(articles)} شركة. جاري معالجة الرسائل...")
                for i in articles[:3]: # عرض أول 3 شركات
                    name = i.find('h2').text.strip() if i.find('h2') else "الشركة"
                    st.subheader(f"🏢 {name}")
                    
                    # طلب الرسالة من AI بأسلوب بشري
                    prompt = f"Schreibe eine kurze, authentische E-Mail-Bewerbung als {job} bei {name} في مدينة {city}. Schreib wie ein Mensch, kein Spam, maximal 3-4 Sätze."
                    response = model.generate_content(prompt)
                    
                    st.write(response.text)
                    st.divider()
            else:
                st.warning("⚠️ مالقيت حتى شركة، جرب كلمات أخرى.")
        except Exception as e:
            st.error(f"❌ وقع مشكل: {str(e)}")
    else:
        st.error("⚠️ عافاك دخل الساروت فـ الجنب والمهنة والمدينة.")
