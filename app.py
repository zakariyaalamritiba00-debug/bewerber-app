import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# إعداد واجهة الموقع
st.set_page_config(page_title="Job Assistant Pro", layout="wide")
st.title("🚀 مساعد زكرياء الذكي للبحث عن عمل")

# القائمة الجانبية لإدخال الساروت
with st.sidebar:
    st.header("🔑 إعدادات الذكاء الاصطناعي")
    user_api_key = st.text_input("لصق Gemini API Key هنا:", type="password")
    st.info("💡 هاد الساروت كيخلي الموقع يكتب رسائل احترافية.")

# خانات إدخال المعلومات
col1, col2 = st.columns(2)
with col1:
    job = st.text_input("المهنة (مثلاً: Koch):")
with col2:
    city = st.text_input("المدينة (مثلاً: Berlin):")

if st.button("بدأ البحث الذكي وكتابة الرسائل"):
    if job and city and user_api_key:
        try:
            # الربط مع أحدث موديل متاح (Flash 1.5)
            genai.configure(api_key=user_api_key.strip())
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # البحث في Gelbe Seiten
            url = f"https://www.gelbeseiten.de/suche/{job}/{city}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(url, headers=headers)
            soup = BeautifulSoup(r.text, 'html.parser')
            articles = soup.find_all('article', class_='mod-Treffer')
            
            if articles:
                st.success(f"✅ لقينا {len(articles)} شركة. جاري كتابة الرسائل...")
                
                # عرض أول 3 شركات لتجنب البطء
                for i in articles[:3]:
                    name = i.find('h2').text.strip() if i.find('h2') else "الشركة"
                    st.subheader(f"🏢 {name}")
                    
                    # الـ Prompt الذكي لكتابة رسالة "بشرية"
                    prompt = f"""
                    Schreibe eine kurze, authentische Bewerbungs-E-Mail auf Deutsch für die Stelle als {job} bei {name} in {city}.
                    WICHTIG:
                    - Schreib wie ein Mensch, nicht wie ein Computer.
                    - Keine Standard-Sätze wie 'Hiermit bewerbe ich mich'.
                    - Halte es kurz (B2 Niveau).
                    """
                    
                    response = model.generate_content(prompt)
                    st.info("✉️ رسالة المراسلة:")
                    st.write(response.text)
                    st.divider()
            else:
                st.warning("⚠️ مالقينا حتى شركة فـ هاد البحث، جرب كلمات أخرى.")
        except Exception as e:
            # كشف نوع الخطأ الحقيقي
            st.error(f"❌ مشكل تقني: {str(e)}")
    else:
        st.error("⚠️ عافاك دخل المهنة والمدينة ولصق الساروت فـ الجنب.")
