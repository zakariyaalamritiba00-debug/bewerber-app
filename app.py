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
from duckduckgo_search import DDGS

# --- بيانات السيرفر ---
G_KEY = "AIzaSyAwfjDDb5Z6_Its2_VrkXKnl3xVcLJP83I"
G_USER = "zakariyaa.lamritiba00@gmail.com"
G_PASS = "fxetfhxnttiebrll"
A_CODE = "zakariya2026"

def get_links_pro(query):
    links = []
    # محاولة البحث في DuckDuckGo أولاً لأنه لا يحظر
    try:
        with DDGS() as ddgs:
            # زيادة دقة البحث
            results = ddgs.text(f"{query} Germany", region='de-de', safesearch='off')
            links = [r['href'] for r in results if 'google' not in r['href']][:15]
    except Exception as e:
        st.write(f"⚠️ DDG Delay: {e}")
        # إذا فشل، جرب جوجل كخطة بديلة
        try:
            links = list(search(query, num_results=10, lang="de"))
        except: pass
    return list(set(links))

def extract_email_smart(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        r = requests.get(url, timeout=8, headers=headers)
        # استخراج الإيميلات من النص الخام
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
        return list(set([e for e in emails if not e.lower().endswith(('.png', '.jpg', '.svg'))]))
    except: return []

st.set_page_config(page_title="Zakariya Job Hunter PRO", layout="wide")

if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🛡️ نظام زكرياء الاحترافي v10.1")
    if st.text_input("كود الدخول:", type="password") == A_CODE:
        st.session_state.auth = True
        st.rerun()
else:
    st.sidebar.title("🎮 لوحة التحكم")
    city = st.sidebar.text_input("📍 المدينة (بالألمانية):", "Berlin")
    job = st.sidebar.text_input("🎯 المهنة (بالألمانية):", "Koch")
    cv_file = st.sidebar.file_uploader("📄 ارفع CV ديالك:", type="pdf")
    
    if st.button("🔥 إطلاق السيسطيم الشامل"):
        genai.configure(api_key=G_KEY, transport='rest')
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # كلمات بحث ألمانية محضة لضمان النتائج
        search_query = f'Ausbildung {job} {city} "E-Mail"'
        st.info(f"📡 جاري القنص بكلمة: {search_query}")
        
        links = get_links_pro(search_query)
        
        if not links:
            st.error("❌ محركات البحث لم تعطي نتائج. جرب مدينة أخرى أو مهنة قريبة.")
        else:
            found_emails = 0
            for link in links:
                with st.status(f"🌐 فحص الموقع: {link}"):
                    emails = extract_email_smart(link)
                    if emails:
                        target = emails[0]
                        st.write(f"✅ لقينا: {target}")
                        
                        # إنشاء الرسالة بالذكاء الاصطناعي
                        prompt = f"Write a professional, very short German application for Ausbildung as {job} in {city}. Mention I am highly motivated. Sign as Zakariya."
                        res = model.generate_content(prompt)
                        
                        # إرسال الإيميل
                        msg = MIMEMultipart()
                        msg['Subject'] = f"Bewerbung um einen Ausbildungsplatz als {job}"
                        msg['From'] = G_USER
                        msg['To'] = target
                        msg.attach(MIMEText(res.text, 'plain'))
                        
                        if cv_file:
                            cv_file.seek(0)
                            part = MIMEApplication(cv_file.read(), Name=cv_file.name)
                            part['Content-Disposition'] = f'attachment; filename="Lebenslauf_Zakariya.pdf"'
                            msg.attach(part)
                            cv_file.seek(0)

                        try:
                            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                                server.login(G_USER, G_PASS)
                                server.sendmail(G_USER, target, msg.as_string())
                            st.success(f"📧 صيفطنا بنجاح لـ {target}")
                            found_emails += 1
                            time.sleep(random.randint(45, 90))
                        except: st.write("❌ مشكل في الإرسال.")
            
            st.balloons()
            st.success(f"🎯 المهمة انتهت! تم التواصل مع {found_emails} شركة.")
