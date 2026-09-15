import streamlit as st

def render_guide():
    st.markdown("## 📖 AEGIS AI - User Operating Manual")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 👑 Admin Ke Liye (Master Control)
        1. **Live Users Tab:** Yahan aapko saare users, unka live GPS location, aur unka **SAFE / SOS** status dikhega.
        2. **Emergency Alert:** Agar koi user SOS button dabayega, toh aapko red color ka **CRITICAL ALERT** warning screen par aayega.
        3. **New User Add Karein:** Naye guard/operator ke liye niche form bharke unka username register karein.
        """)
        
    with col2:
        st.markdown("""
        ### 👤 Field User / Operator Ke Liye
        1. **My Live GPS Location:** Map tab me jayein aur **"GET MY REAL-TIME GPS LOCATION"** button par click karein. Browser aapki exact location trace kar lega.
        2. **Emergency SOS Button:** Kisi bhi khatre me **"🚨 SEND SOS EMERGENCY"** dabaayein, Admin ko turant signal pahunch jayega.
        """)