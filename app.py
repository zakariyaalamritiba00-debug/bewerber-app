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

# محاولة استيراد محرك البحث بذكاء
try:
    from googlesearch import search
except ImportError:
    st.error("⚠️ المكتبات مازال ما تثبتوش فـ main branch. عاود خطوات GitHub.")
    st.stop()

# السوارت ديال زكرياء
G_KEY = "AIzaSyAwfjDDb5Z6_Its2_VrkXKnl3xVcLJP83I"
G_USER = "zakariyaa.lamritiba00@gmail.com"
G_PASS = "fxetfhxnttiebrll"
A_CODE = "zakariya2026"

def get_emails_smart(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, timeout=10, headers=headers)
        content = r.text
        # كاشف الإيميلات
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', content)
        return list(set([e for e in emails if not e.endswith(('.png', '.jpg', '.svg'))]))
    except: return []

st.set_page_config(page_title="Zakariya AI Job Hunter v8.5", layout="wide")

if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    if st.text_input("رمز الأمان:", type="password") == A_CODE:
        st.session_state.auth = True
        st.rerun()
else:
    st.sidebar.title("⚙️ الإعدادات")
    city = st.sidebar.text_input("📍 المدينة (مثلاً: Hamburg):", "Bremen")
    job = st.sidebar.text_input("🎯 المهنة:", "Koch")
    cv_file = st.sidebar.file_uploader("📄 ارفع CV (PDF):", type="pdf")

    if st.button("🚀 إطلاق هجوم الإيميلات"):
        genai.configure(api_key=G_KEY, transport='rest')
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        st.info(f"🔎 جاري التنقيب عن شركات {job} في {city}...")
        
        # البحث عن الشركات اللي عندها إيميلات واضحة
        query = f'"{job}" Ausbildung {city} "email" contact'
        
        try:
            links = list(search(query, num_results=12, lang="de"))
            if not links:
                st.warning("⚠️ جوجل متبلوكي حالياً. تسنى 10 دقايق وعاود.")
            else:
                sent_count = 0
                for link in links:
                    if "google" in link: continue
                    with st.status(f"🌐 فحص: {link}"):
                        emails = get_emails_smart(link)
                        if emails:
                            target = emails[0]
                            st.write(f"✅ تم إيجاد إيميل: {target}")
                            
                            # إنشاء الرسالة بالذكاء الاصطناعي
                            prompt = f"Write a professional B2 German application for Ausbildung as {job} in {city}. Sign as Zakariya."
                            res = model.generate_content(prompt)
                            
                            # إرسال الإيميل
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
                            st.success(f"📧 صيفطنا لـ {target}")
                            sent_count += 1
                            time.sleep(random.randint(30, 60))
                        else: st.write("❌ مالقيتش إيميل.")
                st.balloons()
                st.success(f"🎯 المجموع: {sent_count} شركة توصلت بطلبك!")
        except Exception as e:
            st.error("⚠️ جوجل دار 'بلوك' مؤقت. جرب من بعد شوية.")
