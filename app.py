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

# محاولة استيراد محرك البحث
try:
    from googlesearch import search
except ImportError:
    st.error("❌ المكتبات ناقصة. تأكد من تحديث requirements.txt في فرع main.")
    st.stop()

# بيانات زكرياء
G_KEY = "AIzaSyAwfjDDb5Z6_Its2_VrkXKnl3xVcLJP83I"
G_USER = "zakariyaa.lamritiba00@gmail.com"
G_PASS = "fxetfhxnttiebrll"
A_CODE = "zakariya2026"

st.set_page_config(page_title="Zakariya Final Bot v9.5", layout="wide")

if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    if st.text_input("قن السيرفر:", type="password") == A_CODE:
        st.session_state.auth = True
        st.rerun()
else:
    st.sidebar.success("✅ متصل بالـ Main Branch")
    city = st.sidebar.text_input("📍 المدينة:", "Bremen")
    job = st.sidebar.text_input("🎯 المهنة:", "Koch")
    cv_file = st.sidebar.file_uploader("📄 ارفع CV (PDF):", type="pdf")

    if st.button("🚀 إطلاق رادار البحث"):
        genai.configure(api_key=G_KEY, transport='rest')
        model = genai.GenerativeModel('gemini-1.5-flash')
        st.info(f"🔎 جاري البحث عن شركات {job} في {city}...")
        
        try:
            # استخدام كلمات بحث دقيقة لتقليل البلوك
            query = f'"{job}" Ausbildung {city} email'
            links = list(search(query, num_results=10, lang="de", sleep_interval=10))
            
            if not links:
                st.warning("⚠️ جوجل متبلوكي حالياً. تسنى 15 دقيقة وجرب مدينة أخرى.")
            else:
                for link in links:
                    if "google" in link: continue
                    with st.status(f"🌐 فحص الموقع: {link}"):
                        try:
                            r = requests.get(link, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
                            if emails:
                                target = emails[0]
                                st.write(f"✅ لقينا إيميل: {target}")
                                
                                # إنشاء الرسالة
                                prompt = f"Write a professional B2 German application for Ausbildung as {job} in {city}. Sign as Zakariya."
                                res = model.generate_content(prompt)
                                
                                # إرسال SMTP
                                msg = MIMEMultipart()
                                msg['Subject'] = f"Bewerbung Ausbildung {job}"
                                msg['From'] = G_USER
                                msg['To'] = target
                                msg.attach(MIMEText(res.text, 'plain'))
                                
                                if cv_file:
                                    cv_file.seek(0)
                                    part = MIMEApplication(cv_file.read(), Name=cv_file.name)
                                    part['Content-Disposition'] = f'attachment; filename="{cv_file.name}"'
                                    msg.attach(part)
                                    cv_file.seek(0)

                                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                                    server.login(G_USER, G_PASS)
                                    server.sendmail(G_USER, target, msg.as_string())
                                st.success(f"📧 تم الإرسال بنجاح لـ {target}")
                                time.sleep(random.randint(60, 90)) # وقت طويل لتفادي الحظر
                        except: continue
        except Exception as e:
            st.error("⚠️ حدث خطأ في محرك البحث. ارجع بعد قليل.")
