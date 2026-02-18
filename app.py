import streamlit as st
import requests
from bs4 import BeautifulSoup

# إعداد واجهة الموقع
st.set_page_config(page_title="Bewerber Assistant", layout="wide")
st.title("🚀 مساعد البحث عن شركات في ألمانيا")

# خانات الإدخال
col1, col2 = st.columns(2)
with col1:
    job = st.text_input("المهنة (مثلاً: IT, Koch, Handwerk)")
with col2:
    city = st.text_input("المدينة (مثلاً: Berlin, München)")

# زر البحث
if st.button("بدأ البحث"):
    if job and city:
        url = f"https://www.gelbeseiten.de/suche/{job}/{city}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            r = requests.get(url, headers=headers)
            soup = BeautifulSoup(r.text, 'html.parser')
            articles = soup.find_all('article', class_='mod-Treffer')
            
            if articles:
                st.success(f"لقينا {len(articles)} شركة مستهدفة:")
                for i in articles:
                    name = i.find('h2').text.strip() if i.find('h2') else "اسم غير معروف"
                    st.info(f"🏢 {name}")
            else:
                st.warning("للأسف مالقينا والو، حاول تبدل كلمات البحث.")
        except:
            st.error("وقع مشكل تقني، عاود جرب من بعد.")
    else:
        st.error("عافاك دخل المهنة والمدينة أولاً.")
