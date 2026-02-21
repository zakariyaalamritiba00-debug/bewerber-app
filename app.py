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
from duckduckgo_search import DDGS

# --- أسرار زكرياء ---
G_KEY = "AIzaSyAwfjDDb5Z6_Its2_VrkXKnl3xVcLJP83I"
G_USER = "zakariyaa.lamritiba00@gmail.com"
G_PASS = "fxetfhxnttiebrll"
A_CODE = "zakariya2026"

def get_real_german_firms(job, city):
    # تنظيف الكلمات: كتحيد أي حاجة زايدة باش البحث يكون دقيق
    clean_job = job.replace("Ausbildung", "").strip()
    clean_city = city.replace("2026", "").strip()
    
    # جملة بحث "قناصة" للمواقع الألمانية فقط
    query = f'site:.de "Ausbildung" "{clean_job}" "{clean_city}" "E-Mail"'
    links = []
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, region='de-de', safesearch='off')
            for r in results:
                url = r['href']
                # تصفية المواقع الشينوية والمواقع العامة
                if '.de' in url and not any(x in url for x in ['zhihu', 'amazon', 'facebook', 'ebay', 'instagram']):
                    links.append(url)
    except: pass
    return list(set(links))[:12]

def extract_emails(url):
    try:
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        r = requests.get(url, timeout=10, headers=header)
        # البحث عن الإيميلات فـ النص
        found = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
        return list(set([e for e in found if not e.lower().endswith(('.png', '.jpg', '.svg'))]))
    except: return []

st.set_page_config(page_title="Zakariya Oracle v100", layout="wide")

if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 نظام قنص الشركات v100")
    if st.text_input("كود السيرفر:", type="password") == A_CODE:
        st.session_state.auth = True
        st.rerun()
else:
    st.title("🎯 رادار زكرياء للتوظيف")
    col1, col2 = st.columns(2)
    with col1:
        job_input = st.text_input("🎯 المهنة (ألمانية):", "Koch")
        city_input = st.text_input("📍 المدينة (ألمانية):", "Berlin")
    with col2:
        cv = st.file_uploader("📄 ارفع الـ CV ديالك:", type="pdf")

    if st.button("🚀 إطلاق الهجوم الذكي"):
        genai.configure(api_key=G_KEY, transport='rest')
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        st.info(f"📡 جاري مسح الشركات الحقيقية في {city_input}...")
        links = get_real_german_firms(job_input, city_input)
        
        if not links:
            st.error("❌ مالقيناش شركات دابا. جرب مدينة كبر (مثلاً: München).")
        else:
            found_count = 0
            for link in links:
                with st.status(f"🌐 فحص: {link}"):
                    emails = extract_emails(link)
                    if emails:
                        target = emails[0]
                        st.write(f"✅ تم رصد: {target}")
                        
                        prompt = f"Write a professional short German email for Ausbildung as {job_input} in {city_input}. Sign as Zakariya."
                        res = model.generate_content(prompt).text
                        
                        msg = MIMEMultipart()
                        msg['Subject'] = f"Bewerbung: Ausbildung als {job_input}"
                        msg['From'] = G_USER
                        msg['To'] = target
                        msg.attach(MIMEText(res, 'plain'))
                        
                        if cv:
                            cv.seek(0)
                            part = MIMEApplication(cv.read(), Name="Lebenslauf_Zakariya.pdf")
                            part['Content-Disposition'] = 'attachment; filename="Lebenslauf_Zakariya.pdf"'
                            msg.attach(part)
                        
                        try:
                            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
                                s.login(G_USER, G_PASS)
                                s.sendmail(G_USER, target, msg.as_string())
                            st.success(f"📧 صيفطنا لـ {target}")
                            found_count += 1
                            time.sleep(random.randint(30, 60))
                        except: st.write("❌ عكيس فـ SMTP")
            st.balloons()
            st.success(f"🎯 المهمة اكتملت! صيفطنا لـ {found_count} شركة.")
