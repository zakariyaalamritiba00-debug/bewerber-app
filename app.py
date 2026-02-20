import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import smtplib
import re
from email.mime.text import MIMEText
import time
import random
from googlesearch import search

# --- المعلومات الأساسية ---
G_KEY = "AIzaSyAwfjDDb5Z6_Its2_VrkXKnl3xVcLJP83I"
G_USER = "zakariyaa.lamritiba00@gmail.com"
G_PASS = "fxetfhxnttiebrll"
A_CODE = "zakariya2026"

def extract_email_from_url(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, timeout=10, headers=headers)
        # البحث في الصفحة الرئيسية والروابط القانونية
        content = r.text
        soup = BeautifulSoup(content, 'html.parser')
        
        # محاولة البحث في صفحات Kontakt أو Impressum
        for link in soup.find_all('a', href=True):
            href = link['href'].lower()
            if 'impressum' in href or 'kontakt' in href:
                contact_url = href if href.startswith('http') else url.rstrip('/') + '/' + href.lstrip('/')
                try:
                    r_contact = requests.get(contact_url, timeout=5, headers=headers)
                    content += r_contact.text
                except: continue
        
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', content)
        valid = [e for e in emails if not e.endswith(('.png', '.jpg', '.gif', '.svg'))]
        return list(set(valid))[0] if valid else None
    except: return None

# واجهة المستخدم
st.set_page_config(page_title="Zakariya AI Ultimate", layout="wide")

if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🛡️ بوابة الدخول")
    if st.text_input("الرمز:", type="password") == A_CODE:
        st.session_state.auth = True
        st.rerun()
else:
    st.title("👨‍🍳 رادار زكرياء الخارق v6.0")
    city = st.text_input("المدينة المستهدفة (مثلاً: Hamburg):")
    category = st.selectbox("الفئة:", ["Restaurant", "Hotel", "Seniorenheim", "Krankenhaus"])

    if st.button("🚀 إطلاق الهجوم الذكي"):
        genai.configure(api_key=G_KEY, transport='rest')
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # البحث عن الشركات في جوجل بدل Gelbe Seiten للحصول على نتائج أدق
        query = f"{category} in {city} Deutschland website"
        st.write(f"🔍 جاري التنقيب عن أفضل {category} في {city}...")
        
        found_count = 0
        # نستخدم Google Search للحصول على مواقع حقيقية
        for site_url in search(query, num_results=15, lang="de"):
            if "google" in site_url or "yelp" in site_url or "tripadvisor" in site_url:
                continue
            
            with st.status(f"🌐 فحص الموقع: {site_url}", expanded=False):
                email = extract_email_from_url(site_url)
                if email:
                    prompt = f"Write a professional B2 German email applying for a cook apprenticeship at this company. City: {city}. Short, human, and convincing. Max 5 sentences."
                    response = model.generate_content(prompt)
                    email_body = response.text
                    
                    # إرسال الإيميل
                    msg = MIMEText(email_body)
                    msg['Subject'] = "Anfrage Ausbildung als Koch"
                    msg['From'] = G_USER
                    msg['To'] = email
                    
                    try:
                        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                            server.login(G_USER, G_PASS)
                            server.sendmail(G_USER, email, msg.as_string())
                        st.success(f"✅ تم الإرسال بنجاح إلى: {email}")
                        found_count += 1
                        time.sleep(random.randint(20, 40))
                    except: st.error("❌ فشل في الإرسال")
                else:
                    st.write("لم نجد إيميل مباشر في هذا الموقع.")
        
        st.balloons()
        st.success(f"🎯 المهمة انتهت! تم التواصل مع {found_count} شركة.")
