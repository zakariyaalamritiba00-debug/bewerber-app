import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import time
import random

# محاولة استيراد مكتبة البحث بذكاء
try:
    from googlesearch import search
except ImportError:
    st.error("❌ السيرفر مازال ما ثبتش المكتبات. تسنى دقيقة وحدث الصفحة.")
    st.stop()

# السوارت ديال زكرياء
G_KEY = "AIzaSyAwfjDDb5Z6_Its2_VrkXKnl3xVcLJP83I"
G_USER = "zakariyaa.lamritiba00@gmail.com"
G_PASS = "fxetfhxnttiebrll"
A_CODE = "zakariya2026"

def find_emails(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, timeout=10, headers=headers)
        # البحث عن إيميلات فـ الصفحة الرئيسية وفي صفحات قانونية
        content = r.text
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', content)
        refined = [e for e in emails if not e.endswith(('.png', '.jpg', '.gif', '.svg'))]
        return list(set(refined))
    except: return []

st.set_page_config(page_title="Zakariya AI Job Bot v8.2", layout="wide")

if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🛡️ بوابة الدخول")
    if st.text_input("رمز الأمان:", type="password") == A_CODE:
        st.session_state.auth = True
        st.rerun()
else:
    st.sidebar.title("⚙️ التحكم")
    city = st.sidebar.text_input("📍 المدينة (مثلاً Hamburg):", "Bremen")
    job = st.sidebar.text_input("🎯 المهنة:", "Koch")
    cv_file = st.sidebar.file_uploader("📄 ارفع CV ديالك (PDF):", type="pdf")

    if st.button("🚀 ابدأ قصف الشركات"):
        genai.configure(api_key=G_KEY, transport='rest')
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        st.info(f"🔎 جاري البحث عن {job} في {city}...")
        
        try:
            # كنقلبو فـ جوجل على الشركات اللي حاطة إيميلات
            query = f'"{job}" Ausbildung {city} "email"'
            # كنطلبو 10 نتائج
            links = list(search(query, num_results=10, lang="de"))
            
            if not links:
                st.warning("لم أجد روابط حالياً. جرب مدينة أخرى.")
            else:
                for link in links:
                    if "google" in link or "facebook" in link: continue
                    with st.status(f"🌐 فحص: {link}"):
                        emails = find_emails(link)
                        if emails:
                            target = emails[0]
                            st.write(f"✅ تم إيجاد إيميل: {target}")
                            
                            # إنشاء الرسالة
                            prompt = f"Write a professional B2 German email for an Ausbildung as {job} in {city}. Short and human. Sign as Zakariya."
                            res = model.generate_content(prompt)
                            
                            # إرسال الإيميل (SMTP)
                            msg = MIMEMultipart()
                            msg['Subject'] = f"Bewerbung Ausbildung {job} - {city}"
                            msg['From'] = G_USER
                            msg['To'] = target
                            msg.attach(MIMEText(res.text, 'plain'))
                            
                            if cv_file:
                                part = MIMEApplication(cv_file.read(), Name=cv_file.name)
                                part['Content-Disposition'] = f'attachment; filename="{cv_file.name}"'
                                msg.attach(part)
                                cv_file.seek(0)

                            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                                server.login(G_USER, G_PASS)
                                server.sendmail(G_USER, target, msg.as_string())
                            st.success(f"📧 صيفطنا بنجاح لـ {target}")
                            time.sleep(random.randint(30, 60))
                        else:
                            st.write("❌ مالقيتش إيميل فهاد الموقع.")
        except Exception as e:
            st.error("⚠️ تنبيه: جوجل دار 'بلوك' مؤقت. جرب مرة أخرى بعد 10 دقائق.")
