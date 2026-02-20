import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import smtplib
import re
from email.mime.text import MIMEText
import time
import random
from urllib.parse import urljoin
import pandas as pd

# --- معلومات الوصول الثابتة ---
G_KEY = "AIzaSyAwfjDDb5Z6_Its2_VrkXKnl3xVcLJP83I"
G_USER = "zakariyaa.lamritiba00@gmail.com"
G_PASS = "fxetfhxnttiebrll"
A_CODE = "zakariya2026"

# --- دوال الذكاء الاصطناعي والبحث ---
def get_pro_emails(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        r = requests.get(url, timeout=8, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # جمع روابط صفحات التواصل
        links = [url]
        for a in soup.find_all('a', href=True):
            h = a['href'].lower()
            if any(x in h for x in ['impressum', 'kontakt', 'about', 'contact']):
                links.append(urljoin(url, a['href']))
        
        all_emails = []
        for link in list(set(links))[:3]:
            try:
                res = requests.get(link, timeout=5, headers=headers)
                found = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', res.text)
                all_emails.extend(found)
            except: continue
            
        # تصفية الإيميلات المهمة فقط
        refined = [e for e in all_emails if not e.endswith(('.png', '.jpg', '.gif', 'wix', 'example.com'))]
        return list(set(refined)) if refined else []
    except:
        return []

def send_final_email(to_email, body, company, subject_type):
    try:
        subject = f"Bewerbung um einen Ausbildungsplatz als Koch - {company}" if subject_type == "Formal" else f"Anfrage Ausbildung (Koch) - {company}"
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = G_USER
        msg['To'] = to_email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(G_USER, G_PASS)
            server.sendmail(G_USER, to_email, msg.as_string())
        return True
    except: return False

# --- واجهة المستخدم (Streamlit UI) ---
st.set_page_config(page_title="Zakariya AI Hunter v5", layout="wide")

if "auth" not in st.session_state: st.session_state.auth = False
if "history" not in st.session_state: st.session_state.history = []

if not st.session_state.auth:
    st.title("🛡️ بوابة الدخول الآمنة")
    pwd = st.text_input("أدخل رمز الوصول:", type="password")
    if st.button("دخول"):
        if pwd == A_CODE:
            st.session_state.auth = True
            st.rerun()
        else: st.error("الرمز خاطئ")
else:
    st.title("👨‍🍳 رادار زكرياء الخارق لفرص الـ Ausbildung")
    
    with st.sidebar:
        st.header("⚙️ لوحة التحكم")
        city = st.text_input("📍 المدينة المستهدفة:", "Hamburg")
        category = st.selectbox("🏢 النوع:", ["Restaurant", "Hotel", "Seniorenheim", "Krankenhaus", "Catering"])
        tone = st.radio("✉️ أسلوب الرسالة:", ["رسمي (Formal)", "بشري ودود (Friendly)"])
        limit = st.slider("🎯 عدد الشركات:", 5, 50, 15)
        
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("🚀 إطلاق عملية البحث والإرسال"):
            genai.configure(api_key=G_KEY, transport='rest')
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            st.write(f"--- 📡 جاري مسح مدينة {city} ---")
            search_url = f"https://www.gelbeseiten.de/suche/{category}/{city}"
            res = requests.get(search_url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(res.text, 'html.parser')
            items = soup.find_all('article', class_='mod-Treffer')

            for item in items[:limit]:
                name = item.find('h2').text.strip()
                link = item.find('a', class_='gs_url')['href'] if item.find('a', class_='gs_url') else None
                
                with st.expander(f"🏢 {name}", expanded=True):
                    if not link:
                        st.write("❌ لا يوجد موقع إلكتروني.")
                        continue
                    
                    st.write(f"🌐 فحص الموقع: {link}")
                    emails = get_pro_emails(link)
                    
                    if emails:
                        target_email = emails[0]
                        st.write(f"📧 تم إيجاد إيميل: {target_email}")
                        
                        # توليد الرسالة بالذكاء الاصطناعي
                        style_prompt = "formal and professional" if "Formal" in tone else "natural, warm and human-like"
                        prompt = f"Write a short B2 German application email for a cook apprenticeship. Target: {name}. Style: {style_prompt}. Max 5 sentences."
                        
                        response = model.generate_content(prompt)
                        email_body = response.text
                        
                        if send_final_email(target_email, email_body, name, tone):
                            st.success(f"✅ تم الإرسال بنجاح!")
                            st.session_state.history.append({"الشركة": name, "الإيميل": target_email, "الحالة": "تم الإرسال"})
                            time.sleep(random.randint(20, 40)) # وقفة أمان
                        else: st.error("❌ فشل في الإرسال.")
                    else: st.warning("⚠️ لم نجد إيميل بعد الفحص العميق.")
            st.balloons()

    with col2:
        st.header("📊 سجل اليوم")
        if st.session_state.history:
            df = pd.DataFrame(st.session_state.history)
            st.table(df)
            # زر تحميل السجل
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 تحميل السجل (Excel)", csv, "my_applications.csv", "text/csv")
        else:
            st.write("السجل فارغ حالياً.")
