import streamlit as st
import speech_recognition as sr
import pyttsx3
import threading

from database import init_db, verify_user, log_chat, get_chat_history, clear_chat_history, get_all_faqs, bot_response
from database import *

init_db()

st.set_page_config(page_title="College Chatbot")

# ---------------- SESSION ----------------
if "user" not in st.session_state:
    st.session_state.user = None

# ---------------- VOICE ENGINE (FIXED) ----------------
engine = pyttsx3.init()

def speak(text):
    def run():
        engine.say(text)
        engine.runAndWait()

    threading.Thread(target=run, daemon=True).start()

# ---------------- VOICE INPUT ----------------
def voice_input():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening...")
        audio = r.listen(source)

    try:
        return r.recognize_google(audio)
    except:
        return ""

# ---------------- LOGIN ----------------
def login():
    st.title("College Chatbot Login")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        user = verify_user(u,p)
        if user:
            st.session_state.user = {"id":user[0]}
            st.success("Login success")
            st.rerun()
        else:
            st.error("Invalid login")

# ---------------- CHAT ----------------
def chat():
    st.title("💬 College Chatbot")

    history = get_chat_history(st.session_state.user["id"])

    for msg,is_bot in history:
        if is_bot:
            st.markdown("🤖 " + msg)
        else:
            st.markdown("👤 " + msg)

    msg = st.text_input("Type message")

    c1,c2,c3 = st.columns(3)

    if c1.button("Send"):
        if msg:
            log_chat(st.session_state.user["id"],msg,0)
            res = bot_response(msg)
            log_chat(st.session_state.user["id"],res,1)
            speak(res)
            st.rerun()

    if c2.button("🎤 Speak"):
        msg = voice_input()
        if msg:
            log_chat(st.session_state.user["id"],msg,0)
            res = bot_response(msg)
            log_chat(st.session_state.user["id"],res,1)
            speak(res)
            st.rerun()

    if c3.button("Clear"):
        clear_chat_history(st.session_state.user["id"])
        st.rerun()

# ---------------- MAIN ----------------
if st.session_state.user is None:
    login()
else:
    chat()