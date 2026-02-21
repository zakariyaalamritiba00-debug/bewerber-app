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
from urllib.parse import urljoin

# --- إعدادات زكرياء الخاصة ---
G_KEY = "AIzaSyAwfjDDb5Z6_Its2_VrkXKnl3xVcLJP83I"
G_USER = "zakariyaa.lamritiba00@gmail.com"
G_PASS = "fxetfhxnttiebrll"
A_CODE = "zakariya2026"

# قائمة المتصفحات للتمويه العالي
AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0'
]

def pro_search(job, city):
    query = f'site:.de "Ausbildung" "{job}" "{city}" "E-Mail" -site:xing.com -site:linkedin.com'
    links = []
    try:
        with DDGS() as ddgs:
            # البحث في نطاق ألمانيا لضمان الدقة
            results = ddgs.text(query, region='de-de', safesearch='off', timelimit='m')
            links = [r['href'] for r in results if 'zhihu' not in r['href']]
    except Exception as e:
        st.error(f"📡 تنبيه المحرك: {e}")
    return list(set(links))[:20]

def deep_scan_email(url):
    emails = set()
    try:
        h = {'User-Agent': random.choice(AGENTS)}
        r = requests.get(url, timeout=12, headers=h)
        # مسح الصفحة الأساسية
        found = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
        for e in found:
            if not e.lower().endswith(('.png', '.jpg', '.gif', '.svg', 'wix.com')):
                emails.add(e)
        
        # البحث عن صفحة الاتصال إذا لم يجد شيئاً
        if not emails:
            soup = BeautifulSoup(r.text, 'html.parser')
            for a in soup.find_all('a', href=True):
                t = a.text.lower()
                hr = a['href'].lower()
                if any(x in t or x in hr for x in ['impressum', 'kontakt', 'legal']):
                    target = urljoin(url, a['href'])
                    res = requests.get(target, timeout=7, headers=h)
                    found_sub = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', res.text)
                    for e in found_sub:
                        if not e.lower().endswith(('.png', '.jpg')): emails.add(e)
    except: pass
    return list(emails)

# --- واجهة المنصة v50 ---
st.set_page_config(page_title="ZAKARIYA TITAN v50", page_icon="🎯", layout="wide")

if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔒 Titan Secure Login")
    if st.text_input("Master Password:", type="password") == A_CODE:
        st.session_state.auth = True
        st.rerun()
else:
    st.title("🤖 Zakariya Titan v50.0")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        job = st.text_input("🎯 المهنة (بالألمانية):", "Koch")
    with col2:
        city = st.text_input("📍 المدينة (بالألمانية):", "Berlin")
    with col3:
        cv = st.file_uploader("📄 ارفع CV ديالك:", type="pdf")

    st.sidebar.header("📊 إحصائيات الماكينة")
    mode = st.sidebar.select_slider("طور العمل:", options=["هادئ", "فعال", "هجومي"])

    if st.button("🚀 إطلاق رادار القنص"):
        genai.configure(api_key=G_KEY, transport='rest')
        ai = genai.GenerativeModel('gemini-1.5-flash')
        
        links = pro_search(job, city)
        if not links:
            st.warning("⚠️ لم يتم العثور على أهداف جديدة. جرب تغيير المدينة.")
        else:
            success = 0
            progress = st.progress(0)
            
            for i, link in enumerate(links):
                with st.expander(f"🔍 فحص: {link}", expanded=False):
                    emails = deep_scan_email(link)
                    if emails:
                        email_to = emails[0]
                        st.write(f"✅ تم رصد الهدف: {email_to}")
                        
                        # توليد رسالة احترافية
                        prompt = f"Write a professional, short German cover letter for Ausbildung as {job} in {city}. Use high-level B2 German. Sign as Zakariya."
                        content = ai.generate_content(prompt).text
                        
                        # إرسال الإيميل
                        msg = MIMEMultipart()
                        msg['Subject'] = f"Bewerbung um einen Ausbildungsplatz als {job}"
                        msg['From'] = G_USER
                        msg['To'] = email_to
                        msg.attach(MIMEText(content, 'plain'))
                        
                        if cv:
                            cv.seek(0)
                            part = MIMEApplication(cv.read(), Name="Lebenslauf_Zakariya.pdf")
                            part['Content-Disposition'] = 'attachment; filename="Lebenslauf_Zakariya.pdf"'
                            msg.attach(part)
                            cv.seek(0)
                        
                        try:
                            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
                                s.login(G_USER, G_PASS)
                                s.sendmail(G_USER, email_to, msg.as_string())
                            st.success("📧 تم الإرسال بنجاح!")
                            success += 1
                            # تأخير ذكي
                            wait = 100 if mode == "هادئ" else 60 if mode == "فعال" else 30
                            time.sleep(wait + random.randint(5, 15))
                        except: st.error("❌ فشل في SMTP")
                    else: st.write("⚠️ لم يتم العثور على بريد إلكتروني.")
                progress.progress((i + 1) / len(links))
            
            st.balloons()
            st.success(f"🎯 المجموع النهائي: قنصنا {success} شركة بنجاح!")
