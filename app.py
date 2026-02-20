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
from googlesearch import search
from urllib.parse import urljoin

# --- أسرار زكرياء ---
G_KEY = "AIzaSyAwfjDDb5Z6_Its2_VrkXKnl3xVcLJP83I"
G_USER = "zakariyaa.lamritiba00@gmail.com"
G_PASS = "fxetfhxnttiebrll"
A_CODE = "zakariya2026"

def deep_email_finder(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'}
        r = requests.get(url, timeout=10, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # البحث عن إيميلات في الصفحة الرئيسية
        content = r.text
        # إضافة صفحات Impressum و Kontakt
        for a in soup.find_all('a', href=True):
            h = a['href'].lower()
            if any(x in h for x in ['impressum', 'kontakt', 'legal', 'contact']):
                try:
                    target = urljoin(url, a['href'])
                    res = requests.get(target, timeout=5, headers=headers)
                    content += res.text
                except: continue
        
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', content)
        refined = [e for e in emails if not e.endswith(('.png', '.jpg', '.gif', '.svg', 'wixpress.com'))]
        return list(set(refined))
    except: return []

# --- الواجهة ---
st.set_page_config(page_title="Zakariya AI Hunter v8", layout="wide")

if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🛡️ نظام زكرياء v8.0")
    if st.text_input("رمز الأمان:", type="password") == A_CODE:
        st.session_state.auth = True
        st.rerun()
else:
    st.sidebar.title("⚙️ التحكم")
    city = st.sidebar.text_input("📍 المدينة:", "Hamburg")
    job = st.sidebar.text_input("🎯 المهنة:", "Koch")
    cv_file = st.sidebar.file_uploader("📄 ارفع CV (PDF):", type="pdf")

    if st.button("🚀 ابدأ الهجوم الشامل"):
        genai.configure(api_key=G_KEY, transport='rest')
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        st.info("📡 جاري البحث عن شركات حقيقية فـ جوجل...")
        
        # البحث بكلمات دقيقة باش نلقاو مواقع فيها إيميلات
        query = f'"{job}" Ausbildung {city} "email"'
        
        try:
            links = [url for url in search(query, num_results=10, lang="de") if "google" not in url]
        except:
            st.error("⚠️ جوجل داير بلوك. جرب مرة أخرى من بعد 5 دقايق.")
            st.stop()

        sent_count = 0
        for link in links:
            with st.status(f"🛠️ فحص: {link}", expanded=False):
                emails = deep_email_finder(link)
                if emails:
                    target = emails[0]
                    st.write(f"📧 لقيت إيميل: {target}")
                    
                    # إنشاء الرسالة
                    prompt = f"Write a professional B2 German email applying for an Ausbildung as {job} in {city}. Short and human. Sign as Zakariya."
                    response = model.generate_content(prompt)
                    
                    # إرسال
                    msg = MIMEMultipart()
                    msg['Subject'] = f"Bewerbung Ausbildung {job} - {city}"
                    msg['From'] = G_USER
                    msg['To'] = target
                    msg.attach(MIMEText(response.text, 'plain'))
                    
                    if cv_file:
                        part = MIMEApplication(cv_file.read(), Name=cv_file.name)
                        part['Content-Disposition'] = f'attachment; filename="{cv_file.name}"'
                        msg.attach(part)
                        cv_file.seek(0)

                    try:
                        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                            server.login(G_USER, G_PASS)
                            server.sendmail(G_USER, target, msg.as_string())
                        st.success(f"✅ تم الإرسال لـ {target}")
                        sent_count += 1
                        time.sleep(random.randint(30, 60))
                    except: st.error("❌ مشكل فـ Gmail")
                else:
                    st.write("لم نجد إيميل.")
        
        st.success(f"🎯 المجموع: {sent_count} شركة توصلت بطلبك!")
