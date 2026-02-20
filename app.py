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

# محاولة استيراد محرك البحث بأمان
try:
    from googlesearch import search
except ImportError:
    st.error("❌ مكتبة البحث ناقصة. تأكد من requirements.txt")
    st.stop()

# مفاتيح زكرياء
G_KEY = "AIzaSyAwfjDDb5Z6_Its2_VrkXKnl3xVcLJP83I"
G_USER = "zakariyaa.lamritiba00@gmail.com"
G_PASS = "fxetfhxnttiebrll"
A_CODE = "zakariya2026"

st.set_page_config(page_title="Zakariya Final Bot v9.6", layout="wide")

if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🛡️ رادار زكرياء v9.6")
    if st.text_input("قن الدخول:", type="password") == A_CODE:
        st.session_state.auth = True
        st.rerun()
else:
    st.sidebar.success("📡 السيرفر متصل بـ Main Branch")
    city = st.sidebar.text_input("📍 المدينة المستهدفة:", "Bremen")
    job = st.sidebar.text_input("🎯 المهنة المطلوبة:", "Koch")
    cv_file = st.sidebar.file_uploader("📄 ارفع CV ديالك (PDF):", type="pdf")

    if st.button("🚀 إطلاق رادار البحث والإرسال"):
        genai.configure(api_key=G_KEY, transport='rest')
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        st.info(f"📡 جاري البحث عن {job} في {city}...")
        
        try:
            # كلمات بحث تقلل من احتمال "البلوك"
            query = f'"{job}" Ausbildung {city} "email"'
            # زيادة sleep_interval باش جوجل ما يحبسناش
            links = list(search(query, num_results=12, lang="de", sleep_interval=15))
            
            if not links:
                st.warning("⚠️ جوجل متبلوكي حالياً. انتظر 20 دقيقة لتجنب الحظر.")
            else:
                for link in links:
                    if "google" in link or "facebook" in link: continue
                    with st.status(f"🌐 فحص الموقع: {link}"):
                        try:
                            headers = {'User-Agent': 'Mozilla/5.0'}
                            r = requests.get(link, timeout=10, headers=headers)
                            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
                            
                            if emails:
                                target = emails[0]
                                st.write(f"✅ لقينا إيميل: {target}")
                                
                                # كتابة الرسالة بالذكاء الاصطناعي
                                prompt = f"Write a short, professional B2 German application for Ausbildung as {job} in {city}. Sign as Zakariya."
                                res = model.generate_content(prompt)
                                
                                # إرسال الإيميل
                                msg = MIMEMultipart()
                                msg['Subject'] = f"Bewerbung Ausbildung {job} - {city}"
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
                                
                                st.success(f"📧 تمت المراسلة بنجاح لـ {target}")
                                # انتظار طويل بين كل إرسال باش جوجل وجيميل ما يشكوش
                                time.sleep(random.randint(60, 120))
                            else:
                                st.write("❌ مالقيناش إيميل مباشر.")
                        except: continue
                st.balloons()
        except Exception as e:
            st.error("⚠️ جوجل متبلوكي حالياً. ارجع من بعد 20 دقيقة.")
