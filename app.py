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

# --- بيانات الولوج ---
G_KEY = "AIzaSyAwfjDDb5Z6_Its2_VrkXKnl3xVcLJP83I"
G_USER = "zakariyaa.lamritiba00@gmail.com"
G_PASS = "fxetfhxnttiebrll"
A_CODE = "zakariya2026"

# --- دوال البحث الذكية ---
def get_links(query):
    links = []
    # المحاولة الأولى: جوجل
    try:
        links = list(search(query, num_results=10, lang="de", sleep_interval=5))
    except:
        # المحاولة الثانية: DuckDuckGo (الهروب من الحظر)
        try:
            with DDGS() as ddgs:
                results = ddgs.text(query, region='wt-wt', safesearch='off', timelimit='y')
                links = [r['href'] for r in results][:10]
        except: pass
    return [l for l in links if "google" not in l and "facebook" not in l]

def extract_email_pro(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'}
        r = requests.get(url, timeout=10, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # البحث في الصفحة الرئيسية والصفحات القانونية
        content = r.text
        for a in soup.find_all('a', href=True):
            if any(x in a['href'].lower() for x in ['impressum', 'kontakt', 'contact']):
                try:
                    target = a['href'] if a['href'].startswith('http') else url.rstrip('/') + '/' + a['href'].lstrip('/')
                    res = requests.get(target, timeout=5, headers=headers)
                    content += res.text
                except: continue
        
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', content)
        refined = [e for e in emails if not e.endswith(('.png', '.jpg', '.svg', '.gif'))]
        return list(set(refined))
    except: return []

# --- الواجهة الاحترافية ---
st.set_page_config(page_title="Zakariya Job Master v10", layout="wide")

if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🛡️ منصة زكرياء للتوظيف v10")
    if st.text_input("كود السيرفر:", type="password") == A_CODE:
        st.session_state.auth = True
        st.rerun()
else:
    st.sidebar.title("👨‍🍳 لوحة التحكم")
    city = st.sidebar.text_input("📍 المدينة المستهدفة:", "Bremen")
    job = st.sidebar.text_input("🎯 المهنة المطلوبة:", "Koch")
    cv_file = st.sidebar.file_uploader("📄 ارفع CV (PDF):", type="pdf")
    delay = st.sidebar.slider("⏱️ الانتظار بين الإرسال (ثانية):", 30, 120, 60)

    st.header(f"🚀 قناص الفرص: {job} في {city}")
    
    if st.button("🔥 إطلاق السيسطيم"):
        genai.configure(api_key=G_KEY, transport='rest')
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        st.info("📡 جاري البحث في عدة محركات (Google + DuckDuckGo)...")
        query = f'"{job}" Ausbildung {city} email contact'
        links = get_links(query)
        
        if not links:
            st.error("❌ لم يتم العثور على نتائج. جرب كلمات بحث أخرى.")
        else:
            success_count = 0
            for link in links:
                with st.status(f"🌐 فحص: {link}", expanded=False):
                    emails = extract_email_pro(link)
                    if emails:
                        target = emails[0]
                        st.write(f"✅ تم العثور على: {target}")
                        
                        # إنشاء الرسالة
                        prompt = f"Write a professional B2 German application for Ausbildung as {job} in {city}. Short and human-like. Max 5 sentences. Sign as Zakariya."
                        res = model.generate_content(prompt)
                        
                        # إرسال
                        msg = MIMEMultipart()
                        msg['Subject'] = f"Bewerbung um einen Ausbildungsplatz als {job} - {city}"
                        msg['From'] = G_USER
                        msg['To'] = target
                        msg.attach(MIMEText(res.text, 'plain'))
                        
                        if cv_file:
                            cv_file.seek(0)
                            part = MIMEApplication(cv_file.read(), Name=cv_file.name)
                            part['Content-Disposition'] = f'attachment; filename="{cv_file.name}"'
                            msg.attach(part)
                            cv_file.seek(0)

                        try:
                            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                                server.login(G_USER, G_PASS)
                                server.sendmail(G_USER, target, msg.as_string())
                            st.success(f"📧 تمت المراسلة بنجاح: {target}")
                            success_count += 1
                            time.sleep(delay + random.randint(1, 15))
                        except: st.error("❌ خطأ في الإرسال.")
                    else: st.warning("لم نجد إيميل في هذا الموقع.")
            
            st.balloons()
            st.success(f"🎯 المهمة اكتملت! تم التواصل مع {success_count} شركة.")
