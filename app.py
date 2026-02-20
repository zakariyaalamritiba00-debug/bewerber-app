import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
import time
import random

# إعداد الواجهة الاحترافية
st.set_page_config(page_title="Chef Ausbildung Bot", layout="wide", page_icon="👨‍🍳")
st.title("🤖 روبوت زكرياء: التقديم الأوتوماتيكي للـ Ausbildung")

# القائمة الجانبية (هنا غاتحط السوارت ديالك)
with st.sidebar:
    st.header("🔑 إعدادات التشغيل")
    gemini_key = st.text_input("Gemini API Key:", type="password")
    my_email = st.text_input("إيميلك (Gmail):")
    app_pass = st.text_input("كود الـ 16 حرف (App Password):", type="password")
    st.divider()
    st.info("💡 هاد المعلومات كيبقاو عندك نتا بوحدك.")

# خانة المدينة
city = st.text_input("أدخل المدينة الألمانية (مثلاً: Hamburg):")

if st.button("🚀 ابدأ قصف الشركات بالرسائل"):
    if gemini_key and my_email and app_pass and city:
        try:
            # حل مشكلة 404 نهائياً
            genai.configure(api_key=gemini_key.strip(), transport='rest')
            model = genai.GenerativeModel('gemini-1.5-flash')

            # البحث عن المطاعم والفنادق والمستشفيات
            targets = ["Restaurant", "Hotel", "Krankenhaus"]
            for target in targets:
                st.subheader(f"🔎 كنشوف الشركات فـ فئة: {target}")
                url = f"https://www.gelbeseiten.de/suche/{target}/{city}"
                r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
                soup = BeautifulSoup(r.text, 'html.parser')
                companies = soup.find_all('article', class_='mod-Treffer')

                for comp in companies[:5]: # نجربو بـ 5 من كل نوع فالبداية
                    name = comp.find('h2').text.strip() if comp.find('h2') else "Firma"
                    
                    # توليد رسالة B2 بشرية
                    prompt = f"Write a 4-sentence email for a cooking apprenticeship (Ausbildung) inquiry at {name} in {city}. Level: German B2. Friendly and human tone."
                    response = model.generate_content(prompt)
                    email_body = response.text

                    # إرسال الإيميل (SMTP)
                    # ملاحظة: هاد الجزء كيحتاج إيميل الشركة، حالياً غانطبعو الرسالة
                    # مستقبلاً نزيدو مستخرج الإيميلات
                    with st.expander(f"✉️ رسالة جاهزة لـ {name}"):
                        st.write(email_body)
                        st.success(f"✅ تم تجهيز الإرسال عبر {my_email}")
            
            st.balloons()
            st.success("🎯 المهمة تمت بنجاح!")

        except Exception as e:
            st.error(f"❌ وقع مشكل: {str(e)}")
    else:
        st.warning("⚠️ عافاك دخل كاع السوارت فـ الجنب.")
