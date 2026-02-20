import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# === إعدادات الموقع ===
st.set_page_config(page_title="Bewerber AI Pro", layout="wide")

# === كلمة السر الافتراضية ===
# تقدر تبدلها بكلمة سر صعيبة، أو تقراها من ملف آخر مستقبلا
ACCESS_CODE = "zakariya" 

# === دالة صفحة الوصول ===
def access_page():
    st.title("🔐 صفحة الوصول")
    st.write("أدخل رمز الوصول الخاص بك للمتابعة.")
    
    # حقل إدخال رمز الوصول
    input_code = st.text_input("رمز الوصول:", type="password")
    
    if st.button("الوصول"):
        if input_code == ACCESS_CODE:
            st.session_state["logged_in"] = True # نسجل أن المستخدم دخل
            st.rerun() # نعاود تحميل الصفحة باش يبان التطبيق الرئيسي
        else:
            st.error("رمز الوصول غير صحيح. حاول مرة أخرى.")

# === دالة التطبيق الرئيسي (هادشي هو الكود اللي كان عندك قبل) ===
def main_app():
    st.title("🚀 مساعد زكرياء الذكي")

    with st.sidebar:
        st.header("🔑 إعدادات الأمان")
        user_api_key = st.text_input("لصق Gemini API Key هنا:", type="password")
        st.info("💡 استعمل الساروت الجديد (الآمن).")

    job = st.text_input("المهنة (مثلاً: Koch):")
    city = st.text_input("المدينة (مثلاً: Berlin):")

    if st.button("بدأ البحث وكتابة الرسائل"):
        if job and city and user_api_key:
            try:
                genai.configure(api_key=user_api_key.strip(), transport='rest')
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                url = f"https://www.gelbeseiten.de/suche/{job}/{city}"
                r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
                soup = BeautifulSoup(r.text, 'html.parser')
                articles = soup.find_all('article', class_='mod-Treffer')
                
                if articles:
                    st.success(f"✅ لقينا {len(articles)} شركة. الذكاء الاصطناعي خدام...")
                    for i in articles[:3]:
                        name = i.find('h2').text.strip() if i.find('h2') else "الشركة"
                        st.subheader(f"🏢 {name}")
                        
                        prompt = f"Schreibe eine kurze Bewerbung als {job} bei {name}. Maximal 4 Sätze."
                        response = model.generate_content(prompt)
                        
                        st.info("✉️ الرسالة المقترحة:")
                        st.write(response.text)
                        st.divider()
                else:
                    st.warning("⚠️ مالقيت والو فالبحث.")
            except Exception as e:
                st.error(f"❌ مشكل تقني: {str(e)}")
        else:
            st.error("⚠️ دخل الساروت والمعلومات.")

# === منطق إظهار الصفحة ===
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if st.session_state["logged_in"]:
    main_app() # إلا دخل، كيبان التطبيق الرئيسي
else:
    access_page() # إلا لا، كتبان صفحة الوصول
