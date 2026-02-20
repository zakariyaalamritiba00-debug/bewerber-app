import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import smtplib
import re
from email.mime.text import MIMEText
import time
import random

# جلب السوارت
G_KEY = "AIzaSyAwfjDDb5Z6_Its2_VrkXKnl3xVcLJP83I"
G_USER = "zakariyaa.lamritiba00@gmail.com"
G_PASS = "fxetfhxnttiebrll"
A_CODE = "zakariya2026"

# دالة مطورة لاستخراج الإيميلات
def get_email_pro(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        r = requests.get(url, timeout=10, headers=headers)
        content = r.text
        
        # البحث عن روابط Impressum أو Kontakt
        soup = BeautifulSoup(content, 'html.parser')
        for link in soup.find_all('a', href=True):
            href = link['href'].lower()
            if 'impressum' in href or 'kontakt' in href:
                target_url = href if href.startswith('http') else url.rstrip('/') + '/' + href.lstrip('/')
                try:
                    res = requests.get(target_url, timeout=5, headers=headers)
                    content += res.text
                except: continue
        
        # استخراج الإيميلات وتصفيتها
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', content)
        valid = [e for e in emails if not e.endswith(('.png', '.jpg', '.gif', '.svg', 'wixpress.com'))]
        return list(set(valid))[0] if valid else None
    except:
        return None

def send_email(to_email, body, company_name):
    try:
        msg = MIMEText(body)
        msg['Subject'] = f"Bewerbung um einen Ausbildungsplatz als Koch - {company_name}"
        msg['From'] = G_USER
        msg['To'] = to_email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(G_USER, G_PASS)
            server.sendmail(G_USER, to_email, msg.as_string())
        return True
    except:
        return False

# واجهة الموقع
st.set_page_config(page_title="Zakariya Job Hunter", layout="wide")

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 تسجيل الدخول")
    pwd = st.text_input("رمز الدخول:", type="password")
    if st.button("دخول"):
        if pwd == A_CODE:
            st.session_state.auth = True
            st.rerun()
        else: st.error("رمز خاطئ")
else:
    st.title("👨‍🍳 رادار زكرياء للبحث عن Ausbildung")
    city = st.text_input("المدينة الألمانية (مثلاً: Hamburg أو Berlin):")
    
    if st.button("🚀 ابدأ قصف الشركات"):
        if city:
            genai.configure(api_key=G_KEY, transport='rest')
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # فئات البحث
            cats = ["Restaurant", "Hotel", "Krankenhaus", "Seniorenheim"]
            sent_count = 0
            
            for cat in cats:
                st.subheader(f"📍 فئة: {cat}")
                search_url = f"https://www.gelbeseiten.de/suche/{cat}/{city}"
                res = requests.get(search_url, headers={'User-Agent': 'Mozilla/5.0'})
                soup = BeautifulSoup(res.text, 'html.parser')
                companies = soup.find_all('article', class_='mod-Treffer')

                for comp in companies[:10]:
                    name = comp.find('h2').text.strip()
                    link_tag = comp.find('a', class_='gs_url')
                    website = link_tag['href'] if link_tag else None
                    
                    email = get_email_pro(website) if website else None
                    
                    if email:
                        prompt = f"Write a professional B2 German email applying for a cooking apprenticeship at {name} in {city}. Short and natural. Max 5 sentences."
                        response = model.generate_content(prompt)
                        body = response.text
                        
                        if send_email(email, body, name):
                            st.success(f"✅ تم الإرسال لـ {name} ({email})")
                            with st.expander("شاهد الرسالة المرسلة"):
                                st.write(body)
                            sent_count += 1
                            time.sleep(random.randint(15, 30))
                        else: st.error(f"❌ فشل الإرسال لـ {name}")
                    else:
                        st.write(f"⚪ {name}: مالقيتش الإيميل.")
            st.balloons()
            st.success(f"🎯 المجموع: صيفطنا لـ {sent_count} شركة!")
