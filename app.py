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

# محاولة استيراد مكتبة البحث بأمان
try:
    from googlesearch import search
except ImportError:
    st.error("❌ مكتبة googlesearch ناقصة. تأكد من تحديث requirements.txt فـ main branch.")
    st.stop()

# أسرارك البرمجية
G_KEY = "AIzaSyAwfjDDb5Z6_Its2_VrkXKnl3xVcLJP83I"
G_USER = "zakariyaa.lamritiba00@gmail.com"
G_PASS = "fxetfhxnttiebrll"
A_CODE = "zakariya2026"

# واجهة بسيطة وقوية
st.set_page_config(page_title="Zakariya Hunter v8.1", layout="wide")

if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🛡️ نظام زكرياء v8.1")
    if st.text_input("رمز الأمان:", type="password") == A_CODE:
        st.session_state.auth = True
        st.rerun()
else:
    st.sidebar.title("⚙️ الإعدادات")
    city = st.sidebar.text_input("📍 المدينة (Bremen/Hamburg):", "Bremen")
    job = st.sidebar.text_input("🎯 المهنة (Koch):", "Koch")
    cv_file = st.sidebar.file_uploader("📄 ارفع CV ديالك (PDF):", type="pdf")

    if st.button("🚀 ابدأ العملية الآن"):
        genai.configure(api_key=G_KEY, transport='rest')
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        st.info(f"📡 جاري البحث عن فرص {job} في {city}...")
        
        try:
            # كلمات بحث دقيقة لضمان العثور على إيميلات
            query = f'"{job}" Ausbildung {city} "email" contact'
            links = [url for url in search(query, num_results=10, lang="de") if "google" not in url]
            
            if not links:
                st.warning("⚠️ لم يتم العثور على روابط. جرب مدينة أخرى أو مهنة أخرى.")
            else:
                sent_count = 0
                for link in links:
                    st.write(f"🛠️ فحص: {link}")
                    # هنا كيدار كود استخراج الإيميل والإرسال (نفس اللي فالنسخة السابقة)
                    # ... 
                st.success(f"🎯 المجموع النهائي: {sent_count} شركة.")
        except Exception as e:
            st.error(f"⚠️ حدث تنبيه من جوجل. انتظر 5 دقائق ثم حاول مجدداً.")
