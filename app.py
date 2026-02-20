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

# --- السوارت ديالك (اللي حطيتي قبيلة) ---
G_KEY = "AIzaSyAwfjDDb5Z6_Its2_VrkXKnl3xVcLJP83I"
G_USER = "zakariyaa.lamritiba00@gmail.com"
G_PASS = "fxetfhxnttiebrll"
A_CODE = "zakariya2026"

def find_emails_deeply(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        r = requests.get(url, timeout=12, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # صفحات مستهدفة
        targets = []
        for a in soup.find_all('a', href=True):
            h = a['href'].lower()
            if any(x in h for x in ['impressum', 'kontakt', 'karriere', 'jobs', 'contact']):
                full_url = h if h.startswith('http') else url.rstrip('/') + '/' + h.lstrip('/')
                targets.append(full_url)
        
        combined_text = r.text
        for t_url in list(set(targets))[:3]:
            try:
                rt = requests.get(t_url, timeout=7, headers=headers)
                combined_text += rt.text
            except: continue
            
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', combined_text)
        return list(set([e for e in emails if not e.endswith(('.png', '.jpg', '.gif', '.svg', 'wixpress.com'))]))
    except: return []

def send_complex_email(to_email, body, subject, cv_file=None):
    try:
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = G_USER
        msg['To'] = to_email
        msg.attach(MIMEText(body, 'plain'))
        
        if cv_file:
            part = MIMEApplication(cv_file.read(), Name=cv_file.name)
            part['Content-Disposition'] = f'attachment; filename="{cv_file.name}"'
            msg.attach(part)
            cv_file.seek(0) # إعادة المؤشر للبداية

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(G_USER, G_PASS)
            server.sendmail(G_USER, to_email, msg.as_string())
        return True
    except: return False

# --- واجهة المستخدم الاحترافية ---
st.set_page_config(page_title="Zakariya Job Platform v7", layout="wide")

if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🛡️ نظام زكرياء للتوظيف الذكي - الدخول")
    if st.text_input("رمز الأمان:", type="password") == A_CODE:
        st.session_state.auth = True
        st.rerun()
else:
    st.sidebar.title("👨‍🍳 لوحة التحكم")
    city = st.sidebar.text_input("📍 المدينة:", "Hamburg")
    job = st.sidebar.selectbox("🎯 المهنة:", ["Koch", "Küchenhilfe", "Beikoch", "Hotelfachmann"])
    cv_upload = st.sidebar.file_uploader("📄 ارفع الـ CV ديالك (PDF):", type="pdf")
    tone = st.sidebar.radio("🎭 نبرة الرسالة:", ["رسمية جداً", "ودية واحترافية"])

    st.title(f"🚀 رادار القنص: Ausbildung {job} في {city}")
    
    if st.button("🔥 إطلاق عملية القنص الشاملة"):
        genai.configure(api_key=G_KEY, transport='rest')
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        st.write("--- 📡 جاري البحث عن المواقع الرسمية عبر جوجل ---")
        query = f"Ausbildung {job} {city} contact email website"
        
        results = []
        try:
            for url in search(query, num_results=12, lang="de"):
                if any(x in url for x in ['google', 'youtube', 'facebook', 'linkedin', 'xing', 'instagram']): continue
                results.append(url)
        except:
            st.error("⚠️ جوجل حجب البحث المؤقت. جاري المحاولة مرة أخرى...")
            time.sleep(5)
            
        success_count = 0
        for site in results:
            with st.status(f"🛠️ فحص الموقع: {site}", expanded=False):
                emails = find_emails_deeply(site)
                if emails:
                    target = emails[0]
                    st.write(f"📧 تم العثور على: {target}")
                    
                    # إنشاء الرسالة
                    prompt = f"Write a professional B2 German application for an Ausbildung as {job}. Target city: {city}. Style: {tone}. Max 6 sentences. Include 'Mit freundlichen Grüßen, Zakariya'."
                    response = model.generate_content(prompt)
                    german_msg = response.text
                    
                    if send_complex_email(target, german_msg, f"Bewerbung Ausbildung {job} - {city}", cv_upload):
                        st.success(f"✅ تم الإرسال بنجاح إلى {target}")
                        success_count += 1
                        time.sleep(random.randint(30, 60)) # حماية من الحظر
                    else: st.error(f"❌ فشل إرسال الإيميل.")
                else: st.warning("لم نجد إيميل في هذا الموقع.")
        
        st.balloons()
        st.success(f"🎯 المجموع النهائي: تم مراسلة {success_count} شركة بنجاح!")

