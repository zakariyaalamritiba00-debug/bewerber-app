import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import smtplib
import re
from email.mime.text import MIMEText
import time
import random

# إعدادات الواجهة
st.set_page_config(page_title="Zakariya Job Bot v3", layout="wide", page_icon="👨‍🍳")

# جلب السوارت اللي عطيتي ليا (دابا حطيناهم فالموقع نيشان)
G_KEY = "AIzaSyAwfjDDb5Z6_Its2_VrkXKnl3xVcLJP83I"
G_USER = "zakariyaa.lamritiba00@gmail.com"
G_PASS = "fxetfhxnttiebrll"
A_CODE = "zakariya2026"

# دالة استخراج الإيميل من موقع الشركة
def get_email_from_site(url):
    try:
        r = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
        # تفادي إيميلات الصور أو الصيغ الغريبة
        valid_emails = [e for e in emails if not e.endswith(('.png', '.jpg', '.gif'))]
        return valid_emails[0] if valid_emails else None
    except:
        return None

# دالة إرسال الإيميل عبر SMTP
def send_email(to_email, body, company_name):
    try:
        msg = MIMEText(body)
        msg['Subject'] = f"Anfrage zur Ausbildung als Koch - {company_name}"
        msg['From'] = G_USER
        msg['To'] = to_email
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(G_USER, G_PASS)
            server.sendmail(G_USER, to_email, msg.as_string())
        return True
    except:
        return False

# حماية الموقع برمز الدخول
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔑 تسجيل الدخول")
    pwd = st.text_input("أدخل رمز الوصول:", type="password")
    if st.button("دخول"):
        if pwd == A_CODE:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("رمز خاطئ!")
else:
    st.title("🤖 روبوت القنص الذكي - مجال الطبخ 👨‍🍳")
    city = st.text_input("في أي مدينة ألمانية تريد البحث؟ (مثلاً: Hamburg)")

    if st.button("🚀 ابدأ البحث والمراسلة التلقائية"):
        if not city:
            st.warning("أدخل المدينة أولاً!")
        else:
            # تهيئة AI
            genai.configure(api_key=G_KEY, transport='rest')
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # فئات البحث
            categories = ["Restaurant", "Hotel", "Krankenhaus", "Seniorenheim"]
            sent_count = 0
            
            progress_bar = st.progress(0)
            
            for cat in categories:
                st.info(f"🔎 جاري البحث في فئة: {cat}...")
                search_url = f"https://www.gelbeseiten.de/suche/{cat}/{city}"
                res = requests.get(search_url, headers={'User-Agent': 'Mozilla/5.0'})
                soup = BeautifulSoup(res.text, 'html.parser')
                companies = soup.find_all('article', class_='mod-Treffer')

                for comp in companies[:20]: # نأخذ أول 20 من كل صنف
                    name = comp.find('h2').text.strip() if comp.find('h2') else "Unbekannt"
                    
                    # البحث عن الموقع الإلكتروني للشركة
                    link_tag = comp.find('a', class_='gs_url')
                    website = link_tag['href'] if link_tag else None
                    
                    email = get_email_from_site(website) if website else None
                    
                    if email:
                        # توليد رسالة B2 بشرية
                        prompt = f"Write a professional yet natural German email for an Ausbildung application as a cook. Company: {name} in {city}. Level B2. No robotic phrases. Max 5 sentences."
                        response = model.generate_content(prompt)
                        email_content = response.text
                        
                        # الإرسال الفعلي
                        if send_email(email, email_content, name):
                            st.success(f"✅ تم الإرسال بنجاح إلى: {name} ({email})")
                            sent_count += 1
                            # تأخير عشوائي لتفادي الـ Spam
                            time.sleep(random.randint(15, 30))
                        else:
                            st.error(f"❌ فشل الإرسال إلى {name}")
                    else:
                        st.text(f"ℹ️ {name}: لم يتم العثور على بريد إلكتروني.")
            
            st.balloons()
            st.success(f"🎯 المهمة اكتملت! تم مراسلة {sent_count} شركة.")
