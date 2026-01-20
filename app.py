# app.py - MaternalMind AI - Complete Pregnancy Wellness Platform
import streamlit as st
import sqlite3
import hashlib
import datetime
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
import tempfile
import json
import os
import warnings
import pickle
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib
import traceback
import tensorflow as tf
from tensorflow import keras
import re
import bcrypt
import secrets
import string
import time
import random
from PIL import Image, ImageDraw
import base64
import io

warnings.filterwarnings('ignore')

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="MaternalMind AI - Pregnancy Wellness Platform",
    page_icon="🤰",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': 'https://maternalmind.ai/support',
        'Report a bug': "https://maternalmind.ai/issues",
        'About': """
        # MaternalMind AI - Pregnancy Wellness Platform
        
        **AI-Powered Emotional & Physical Wellness Support for Expecting Mothers**
        
        **Disclaimer**: This platform provides wellness support and tracking only, not medical advice.
        Always consult healthcare providers for medical concerns.
        
        © 2024 MaternalMind AI. All rights reserved.
        """
    }
)

# ============================================
# LOGO HANDLING FUNCTIONS
# ============================================
def load_logo_image():
    """Load logo image from file - specifically for maternalmindai.png"""
    try:
        # Try to load your circular logo file
        if os.path.exists('maternalmindai.png'):
            img = Image.open('maternalmindai.png')
            return img
        else:
            # Try other possible names
            logo_files = ['logo.png', 'logo.jpg', 'logo.jpeg', 'logo.gif', 
                         'maternalmind_logo.png', 'maternalmind_logo.jpg',
                         'app_logo.png', 'app_logo.jpg']
            
            for logo_file in logo_files:
                if os.path.exists(logo_file):
                    img = Image.open(logo_file)
                    return img
            
            # If no logo found, return None
            return None
            
    except Exception as e:
        print(f"Error loading logo: {e}")
        return None

def get_logo_base64():
    """Convert logo to base64 for embedding in HTML"""
    try:
        logo_img = load_logo_image()
        if logo_img:
            # Ensure image is RGBA (for transparency)
            if logo_img.mode != 'RGBA':
                logo_img = logo_img.convert('RGBA')
            
            # Resize for optimal display while maintaining aspect ratio
            # Keep the original circular shape (don't apply circular mask as logo is already circular)
            max_size = 200
            logo_img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Convert to base64
            buffer = io.BytesIO()
            logo_img.save(buffer, format="PNG")
            buffer.seek(0)
            data_uri = base64.b64encode(buffer.read()).decode('utf-8')
            return f"data:image/png;base64,{data_uri}"
    except Exception as e:
        print(f"Error converting logo to base64: {e}")
    
    return None

# ============================================
# LOADING SCREEN
# ============================================
def show_loading_screen():
    """Display a loading screen with logo"""
    # Check if we should show loading screen
    if 'loading_complete' not in st.session_state:
        st.session_state.loading_complete = False
    
    # Show loading screen only once
    if not st.session_state.loading_complete:
        # Inject CSS for loading screen with WHITE background
        st.markdown("""
        <style>
        .loading-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #ffffff 0%, #f5f7fa 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        }
        
        .loading-content {
            text-align: center;
            animation: fadeIn 0.5s ease-in-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .logo-img-loading {
            width: 200px;
            height: 200px;
            border-radius: 50%;
            object-fit: contain;
            margin-bottom: 20px;
            animation: gentleFloat 3s ease-in-out infinite;
            box-shadow: 0 10px 30px rgba(139, 95, 191, 0.2);
        }
        
        @keyframes gentleFloat {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        
        .loading-text {
            color: #8B5FBF;
            font-size: 24px;
            font-weight: 600;
            margin-top: 20px;
            font-family: 'Inter', sans-serif;
        }
        
        .loading-subtext {
            color: #6c757d;
            font-size: 16px;
            margin-top: 10px;
            font-family: 'Inter', sans-serif;
        }
        
        .loader {
            width: 50px;
            height: 50px;
            border: 5px solid rgba(139, 95, 191, 0.1);
            border-radius: 50%;
            border-top-color: #8B5FBF;
            animation: spin 1s ease-in-out infinite;
            margin: 20px auto;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Get logo
        logo_base64 = get_logo_base64()
        
        if logo_base64:
            # Show loading screen with circular logo ONLY (no text)
            st.markdown(f"""
            <div class="loading-container">
                <div class="loading-content">
                    <img src="{logo_base64}" class="logo-img-loading" alt="MaternalMind AI">
                    <div class="loader"></div>
                    <div class="loading-text">Initializing Platform</div>
                    <div class="loading-subtext">Pregnancy Wellness Intelligence</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Fallback without logo
            st.markdown("""
            <div class="loading-container">
                <div class="loading-content">
                    <div style="font-size: 80px; margin-bottom: 20px; color: #8B5FBF;">🤰</div>
                    <div class="loader"></div>
                    <div class="loading-text">Loading MaternalMind AI</div>
                    <div class="loading-subtext">Your Pregnancy Wellness Platform</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Mark as complete and rerun
        st.session_state.loading_complete = True
        time.sleep(2)
        st.rerun()

# ============================================
# MODERN CSS THEME (with logo styles)
# ============================================
st.markdown("""
<style>
    /* Modern Color Palette */
    :root {
        --primary: #8B5FBF;
        --primary-dark: #6B46C1;
        --primary-light: #9F7AEA;
        --secondary: #4299E1;
        --accent: #ED64A6;
        --success: #48BB78;
        --warning: #ECC94B;
        --danger: #F56565;
        --info: #0BC5EA;
        --light: #F7FAFC;
        --dark: #2D3748;
        --gray-100: #EDF2F7;
        --gray-200: #E2E8F0;
        --gray-300: #CBD5E0;
        --gray-400: #A0AEC0;
        --gray-600: #718096;
        --gray-700: #4A5568;
        --gray-800: #2D3748;
        --white: #FFFFFF;
        --gradient-primary: linear-gradient(135deg, #8B5FBF 0%, #9F7AEA 100%);
        --gradient-accent: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        --shadow-md: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        --shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        --radius: 12px;
        --radius-lg: 16px;
        --transition: all 0.3s ease;
    }
    
    /* Base Styles */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4edf5 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Modern Container */
    .modern-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
    }
    
    /* Logo Styles - Modified for circular logo with text */
    .logo-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .logo-img-header {
        height: 120px;
        width: 120px;
        border-radius: 50%;
        object-fit: contain;
        margin-bottom: 0.5rem;
        box-shadow: var(--shadow-lg);
        border: 4px solid white;
    }
    
    /* Remove all text logo styles since your logo contains text */
    .logo-text {
        display: none !important;
    }
    
    .logo-subtext {
        color: var(--gray-600);
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    /* Sidebar Logo */
    .sidebar-logo {
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem 0;
        border-bottom: 1px solid var(--gray-200);
    }
    
    .sidebar-logo-img {
        height: 80px;
        width: 80px;
        border-radius: 50%;
        object-fit: contain;
        margin-bottom: 0.5rem;
        border: 3px solid white;
        box-shadow: var(--shadow);
    }
    
    /* Modern Cards */
    .card-modern {
        background: var(--white);
        border-radius: var(--radius);
        box-shadow: var(--shadow);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid var(--gray-200);
        transition: var(--transition);
    }
    
    .card-modern:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
    }
    
    .card-header-modern {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
        color: var(--dark);
    }
    
    .card-icon-modern {
        font-size: 1.5rem;
        margin-right: 0.75rem;
        color: var(--primary);
    }
    
    .card-title-modern {
        font-size: 1.25rem;
        font-weight: 600;
        margin: 0;
        color: var(--dark);
    }
    
    /* Modern Metrics */
    .metric-card-modern {
        background: var(--white);
        border-radius: var(--radius);
        padding: 1.5rem;
        box-shadow: var(--shadow);
        border-left: 4px solid var(--primary);
    }
    
    .metric-value-modern {
        font-size: 2rem;
        font-weight: 700;
        color: var(--dark);
        margin: 0.5rem 0;
    }
    
    .metric-label-modern {
        font-size: 0.875rem;
        color: var(--gray-600);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .metric-change-modern {
        font-size: 0.875rem;
        color: var(--success);
        margin-top: 0.25rem;
    }
    
    /* Progress Indicators */
    .progress-bar-modern {
        height: 8px;
        background: var(--gray-200);
        border-radius: 4px;
        overflow: hidden;
        margin: 1rem 0;
    }
    
    .progress-fill-modern {
        height: 100%;
        background: var(--gradient-primary);
        border-radius: 4px;
        transition: width 0.3s ease;
    }
    
    /* Streamlit Component Overrides */
    .stButton > button {
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        transition: var(--transition) !important;
        border: none !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-md) !important;
    }
    
    /* Symptom Intensity Colors */
    .intensity-1 { color: var(--success); }
    .intensity-2 { color: var(--success); }
    .intensity-3 { color: var(--info); }
    .intensity-4 { color: var(--info); }
    .intensity-5 { color: var(--warning); }
    .intensity-6 { color: var(--warning); }
    .intensity-7 { color: var(--danger); }
    .intensity-8 { color: var(--danger); }
    .intensity-9 { color: var(--danger); }
    .intensity-10 { color: var(--danger); }
    
    /* Animations */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-out;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# DATABASE SETUP
# ============================================
def init_database():
    conn = sqlite3.connect('maternalmind.db', check_same_thread=False)
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        salt TEXT NOT NULL,
        trimester INTEGER DEFAULT 1,
        weeks_pregnant INTEGER DEFAULT 1,
        baby_name TEXT DEFAULT 'Our Little One',
        due_date TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP,
        profile_completed BOOLEAN DEFAULT 0
    )''')
    
    # Profile settings
    c.execute('''CREATE TABLE IF NOT EXISTS profile_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        notifications_enabled BOOLEAN DEFAULT 1,
        weekly_updates BOOLEAN DEFAULT 1,
        privacy_level INTEGER DEFAULT 1,
        theme TEXT DEFAULT 'light',
        auto_week_update BOOLEAN DEFAULT 1,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    
    # Emotions
    c.execute('''CREATE TABLE IF NOT EXISTS emotions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT NOT NULL,
        emotion TEXT,
        confidence REAL,
        source TEXT,
        notes TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    
    # Symptoms
    c.execute('''CREATE TABLE IF NOT EXISTS symptoms_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT NOT NULL,
        symptom_type TEXT,
        intensity INTEGER CHECK(intensity >= 1 AND intensity <= 10),
        duration_hours REAL,
        notes TEXT,
        resolved BOOLEAN DEFAULT 0,
        reported_to_doctor BOOLEAN DEFAULT 0,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    
    # Baby kicks
    c.execute('''CREATE TABLE IF NOT EXISTS baby_kicks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT NOT NULL,
        time TEXT,
        kicks INTEGER,
        duration_minutes INTEGER,
        notes TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    
    # Nutrition
    c.execute('''CREATE TABLE IF NOT EXISTS nutrition_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT NOT NULL,
        meal_type TEXT,
        food_items TEXT,
        calories INTEGER,
        nutrients TEXT,
        notes TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    
    # Exercise
    c.execute('''CREATE TABLE IF NOT EXISTS exercise_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT NOT NULL,
        exercise_type TEXT,
        duration_minutes INTEGER,
        intensity TEXT,
        calories_burned INTEGER,
        notes TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    
    # Vitamins
    c.execute('''CREATE TABLE IF NOT EXISTS vitamin_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT NOT NULL,
        vitamin_name TEXT,
        taken BOOLEAN,
        dosage TEXT,
        notes TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    
    # Emergency symptoms
    c.execute('''CREATE TABLE IF NOT EXISTS emergency_symptoms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT NOT NULL,
        symptom TEXT,
        severity TEXT,
        action_taken TEXT,
        doctor_contacted BOOLEAN DEFAULT 0,
        notes TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    
    conn.commit()
    return conn

# Initialize database
conn = init_database()
c = conn.cursor()

# ============================================
# SECURITY FUNCTIONS
# ============================================
def generate_salt():
    return bcrypt.gensalt().decode('utf-8')

def hash_password(password, salt=None):
    if salt is None:
        salt = generate_salt()
    password_bytes = password.encode('utf-8')
    salt_bytes = salt.encode('utf-8')
    hashed = bcrypt.hashpw(password_bytes, salt_bytes)
    return hashed.decode('utf-8'), salt

def verify_password(password, hashed_password, salt):
    try:
        password_bytes = password.encode('utf-8')
        salt_bytes = salt.encode('utf-8')
        new_hash = bcrypt.hashpw(password_bytes, salt_bytes)
        return new_hash.decode('utf-8') == hashed_password
    except:
        return False

def validate_password_strength(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(char.islower() for char in password):
        return False, "Password must contain at least one lowercase letter"
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one number"
    special_chars = "!@#$%^&*()-_=+[]{}|;:,.<>?"
    if not any(char in special_chars for char in password):
        return False, f"Password must contain at least one special character ({special_chars})"
    return True, "Password is secure"

# ============================================
# DATABASE HELPER FUNCTIONS
# ============================================
def get_user_data(user_id):
    c.execute("SELECT * FROM users WHERE id=?", (user_id,))
    return c.fetchone()

def update_user_profile(user_id, trimester, weeks_pregnant, baby_name, due_date=None):
    c.execute("""UPDATE users SET 
                trimester=?, weeks_pregnant=?, baby_name=?, due_date=?
                WHERE id=?""",
              (trimester, weeks_pregnant, baby_name, due_date, user_id))
    conn.commit()

def add_emotion(user_id, emotion, confidence=0.0, source="voice", notes=""):
    c.execute("""INSERT INTO emotions 
                (user_id, date, emotion, confidence, source, notes)
                VALUES (?, ?, ?, ?, ?, ?)""",
              (user_id, str(datetime.date.today()), emotion, confidence, source, notes))
    conn.commit()

def add_symptom_log(user_id, symptom_type, intensity, duration_hours=1, notes="", resolved=False):
    c.execute("""INSERT INTO symptoms_log 
                (user_id, date, symptom_type, intensity, duration_hours, notes, resolved)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
              (user_id, str(datetime.date.today()), symptom_type, intensity, 
               duration_hours, notes, resolved))
    conn.commit()

def add_emergency_symptom(user_id, symptom, severity, action_taken, doctor_contacted=False, notes=""):
    c.execute("""INSERT INTO emergency_symptoms 
                (user_id, date, symptom, severity, action_taken, doctor_contacted, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
              (user_id, str(datetime.date.today()), symptom, severity, 
               action_taken, doctor_contacted, notes))
    conn.commit()

def add_baby_kick(user_id, kicks, duration_minutes=10, notes=""):
    c.execute("""INSERT INTO baby_kicks 
                (user_id, date, time, kicks, duration_minutes, notes)
                VALUES (?, ?, ?, ?, ?, ?)""",
              (user_id, str(datetime.date.today()), 
               datetime.datetime.now().strftime("%H:%M"), 
               kicks, duration_minutes, notes))
    conn.commit()

def add_nutrition_log(user_id, meal_type, food_items, calories, nutrients="", notes=""):
    c.execute("""INSERT INTO nutrition_logs 
                (user_id, date, meal_type, food_items, calories, nutrients, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
              (user_id, str(datetime.date.today()), meal_type, food_items, calories, nutrients, notes))
    conn.commit()

def add_exercise_log(user_id, exercise_type, duration_minutes, intensity, calories_burned=0, notes=""):
    c.execute("""INSERT INTO exercise_logs 
                (user_id, date, exercise_type, duration_minutes, intensity, calories_burned, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
              (user_id, str(datetime.date.today()), exercise_type, duration_minutes, intensity, calories_burned, notes))
    conn.commit()

def add_vitamin_log(user_id, vitamin_name, taken=True, dosage="", notes=""):
    c.execute("""INSERT INTO vitamin_logs 
                (user_id, date, vitamin_name, taken, dosage, notes)
                VALUES (?, ?, ?, ?, ?, ?)""",
              (user_id, str(datetime.date.today()), vitamin_name, taken, dosage, notes))
    conn.commit()

def get_emotion_history(user_id, days=30):
    c.execute("""SELECT date, emotion, confidence, source, notes 
                FROM emotions 
                WHERE user_id=? AND date >= date('now', ?)
                ORDER BY date DESC""",
              (user_id, f'-{days} days'))
    return pd.DataFrame(c.fetchall(), columns=["date", "emotion", "confidence", "source", "notes"])

def get_symptoms_history(user_id, days=30):
    c.execute("""SELECT date, symptom_type, intensity, duration_hours, notes, resolved, reported_to_doctor
                FROM symptoms_log 
                WHERE user_id=? AND date >= date('now', ?)
                ORDER BY date DESC, intensity DESC""",
              (user_id, f'-{days} days'))
    return pd.DataFrame(c.fetchall(), 
                       columns=["date", "symptom", "intensity", "duration_hours", "notes", "resolved", "reported"])

def get_emergency_symptoms(user_id, days=90):
    c.execute("""SELECT date, symptom, severity, action_taken, doctor_contacted, notes
                FROM emergency_symptoms 
                WHERE user_id=? AND date >= date('now', ?)
                ORDER BY date DESC""",
              (user_id, f'-{days} days'))
    return pd.DataFrame(c.fetchall(), 
                       columns=["date", "symptom", "severity", "action_taken", "doctor_contacted", "notes"])

def get_baby_kicks_history(user_id, days=30):
    c.execute("""SELECT date, time, kicks, duration_minutes, notes 
                FROM baby_kicks 
                WHERE user_id=? AND date >= date('now', ?)
                ORDER BY date DESC, time DESC""",
              (user_id, f'-{days} days'))
    return pd.DataFrame(c.fetchall(), columns=["date", "time", "kicks", "duration_minutes", "notes"])

def get_nutrition_history(user_id, days=7):
    c.execute("""SELECT date, meal_type, food_items, calories, nutrients, notes 
                FROM nutrition_logs 
                WHERE user_id=? AND date >= date('now', ?)
                ORDER BY date DESC""",
              (user_id, f'-{days} days'))
    return pd.DataFrame(c.fetchall(), columns=["date", "meal_type", "food_items", "calories", "nutrients", "notes"])

def get_exercise_history(user_id, days=7):
    c.execute("""SELECT date, exercise_type, duration_minutes, intensity, calories_burned, notes 
                FROM exercise_logs 
                WHERE user_id=? AND date >= date('now', ?)
                ORDER BY date DESC""",
              (user_id, f'-{days} days'))
    return pd.DataFrame(c.fetchall(), columns=["date", "exercise_type", "duration_minutes", "intensity", "calories_burned", "notes"])

def get_vitamin_history(user_id, days=7):
    c.execute("""SELECT date, vitamin_name, taken, dosage, notes 
                FROM vitamin_logs 
                WHERE user_id=? AND date >= date('now', ?)
                ORDER BY date DESC""",
              (user_id, f'-{days} days'))
    return pd.DataFrame(c.fetchall(), columns=["date", "vitamin_name", "taken", "dosage", "notes"])

# ============================================
# PREGNANCY INFO FUNCTIONS
# ============================================
PREGNANCY_TIMELINE = {
    1: {"desc": "Conception occurs\nBlastocyst implants in uterus\nPlacenta begins to form", "size": "Poppy seed"},
    2: {"desc": "Baby's brain, spinal cord, heart begin", "size": "Apple seed"},
    3: {"desc": "Heart beats, limb buds appear", "size": "Lentil"},
    4: {"desc": "Brain growing rapidly\nEyes, ears, mouth forming", "size": "Blueberry"},
    5: {"desc": "All major organs forming\nWebbed fingers and toes", "size": "Raspberry"},
    6: {"desc": "Embryo becomes fetus\nTiny muscles can move", "size": "Grape"},
    7: {"desc": "Organs fully formed, beginning to function\nFingernails and hair forming", "size": "Kumquat"},
    8: {"desc": "Baby kicking and stretching\nGenitals developing", "size": "Fig"},
    9: {"desc": "Reflexes developing\nCan open and close fingers", "size": "Lime"},
    10: {"desc": "Vocal cords developing\nCan suck thumb", "size": "Lemon"},
    11: {"desc": "Facial expressions possible\nFine hair (lanugo) appears", "size": "Peach"},
    12: {"desc": "Can sense light\nTaste buds forming", "size": "Apple"},
    13: {"desc": "Hearing developing\nSex identifiable on ultrasound", "size": "Avocado"},
    14: {"desc": "Fat stores developing\nSweat glands forming", "size": "Turnip"},
    15: {"desc": "Yawning and hiccupping\nCan hear mom's heartbeat", "size": "Bell pepper"},
    16: {"desc": "Protective vernix coating skin\nHair growing on scalp", "size": "Heirloom tomato"},
    17: {"desc": "Midpoint of pregnancy\nMom may feel movement (quickening)", "size": "Banana"},
    18: {"desc": "Regular sleep/wake cycles\nTaste of amniotic fluid", "size": "Carrot"},
    19: {"desc": "Eyebrows and eyelashes visible\nFingerprints forming", "size": "Spaghetti squash"},
    20: {"desc": "Rapid eye movements\nLoud noises may startle baby", "size": "Grapefruit"},
    21: {"desc": "Viability milestone (can survive with NICU care)\nLungs developing", "size": "Ear of corn"},
    22: {"desc": "Responds to familiar voices\nHand dominance may show", "size": "Rutabaga"},
    23: {"desc": "Eyes begin to open\nBreathing movements (practice)", "size": "Scallion bunch"},
    24: {"desc": "Brain developing rapidly\nRecognizes mom's voice", "size": "Cauliflower"},
    25: {"desc": "Can blink eyes\nDreaming may begin (REM sleep)", "size": "Eggplant"},
    26: {"desc": "Kicking and punching vigorously\nBones fully developed", "size": "Butternut squash"},
    27: {"desc": "Controls body temperature\nRed blood cell production begins", "size": "Large cabbage"},
    28: {"desc": "All five senses functional\nGains weight rapidly", "size": "Coconut"},
    29: {"desc": "Toenails visible\nLess room to move", "size": "Jicama"},
    30: {"desc": "Immune system developing\nBones hardening (except skull)", "size": "Pineapple"},
    31: {"desc": "Lungs nearly mature\nFingernails reach fingertips", "size": "Cantaloupe"},
    32: {"desc": "Most development complete\nGaining fat for temperature regulation", "size": "Honeydew melon"},
    33: {"desc": "May descend into pelvis (engagement)\nSkin smoothing out", "size": "Head of romaine lettuce"},
    34: {"desc": "Early term\nPractice breathing continues\nSucking reflex strong", "size": "Swiss chard bunch"},
    35: {"desc": "Brain continues developing\nFirm grasp", "size": "Leek"},
    36: {"desc": "Full term\nShedding vernix coating\nReady for birth", "size": "Mini watermelon"},
    37: {"desc": "Due date week\nBaby's organs ready for outside world", "size": "Small pumpkin"},
    38: {"desc": "Average newborn: 7.5 lbs, 20 inches", "size": "Small pumpkin"},
    39: {"desc": "Ready for delivery", "size": "Small pumpkin"},
    40: {"desc": "Full term achieved\nReady for delivery", "size": "Small pumpkin"},
}

def get_baby_info_by_week(week):
    week = max(1, min(40, week))
    info = PREGNANCY_TIMELINE.get(week, {"desc": "Information not available", "size": "N/A"})
    return f"**Week {week}**\n- {info['desc']}\n- **Size:** {info['size']}"

def get_trimester(week):
    if week <= 13:
        return 1
    elif week <= 27:
        return 2
    else:
        return 3

def get_symptom_patterns(trimester):
    common_symptoms = {
        1: [
            {"symptom": "Nausea/Morning Sickness", "frequency": 85, "severity": "Moderate", 
             "tips": "Eat small, frequent meals. Try ginger tea or crackers."},
            {"symptom": "Fatigue", "frequency": 90, "severity": "High", 
             "tips": "Rest when possible. Consider short naps during the day."},
            {"symptom": "Breast Tenderness", "frequency": 80, "severity": "Moderate", 
             "tips": "Wear supportive bra. Apply warm or cold compresses."},
            {"symptom": "Frequent Urination", "frequency": 75, "severity": "Mild", 
             "tips": "Limit fluids before bedtime. Empty bladder completely."},
            {"symptom": "Food Aversions/Cravings", "frequency": 70, "severity": "Mild", 
             "tips": "Listen to your body. Focus on nutrient-dense foods."}
        ],
        2: [
            {"symptom": "Back Pain", "frequency": 65, "severity": "Moderate", 
             "tips": "Practice good posture. Use pregnancy pillows for support."},
            {"symptom": "Leg Cramps", "frequency": 50, "severity": "Mild", 
             "tips": "Stretch gently. Ensure adequate calcium and magnesium intake."},
            {"symptom": "Heartburn", "frequency": 60, "severity": "Moderate", 
             "tips": "Eat smaller meals. Avoid spicy/fatty foods before bed."},
            {"symptom": "Nasal Congestion", "frequency": 40, "severity": "Mild", 
             "tips": "Use humidifier. Stay hydrated."},
            {"symptom": "Skin Changes", "frequency": 55, "severity": "Mild", 
             "tips": "Use pregnancy-safe moisturizers. Stay hydrated."}
        ],
        3: [
            {"symptom": "Swelling (Edema)", "frequency": 75, "severity": "Moderate", 
             "tips": "Elevate feet. Stay hydrated. Limit salt intake."},
            {"symptom": "Shortness of Breath", "frequency": 70, "severity": "Moderate", 
             "tips": "Practice good posture. Use extra pillows when sleeping."},
            {"symptom": "Braxton Hicks Contractions", "frequency": 60, "severity": "Mild", 
             "tips": "Change position. Drink water. Practice breathing techniques."},
            {"symptom": "Pelvic Pressure", "frequency": 65, "severity": "Moderate", 
             "tips": "Rest frequently. Wear supportive belly band."},
            {"symptom": "Insomnia", "frequency": 55, "severity": "Moderate", 
             "tips": "Establish bedtime routine. Use pregnancy pillow."}
        ]
    }
    return common_symptoms.get(trimester, [])

def get_emergency_symptoms_list():
    return [
        {"symptom": "Severe abdominal pain", "urgency": "High", "action": "Go to ER immediately"},
        {"symptom": "Heavy vaginal bleeding", "urgency": "High", "action": "Call emergency services"},
        {"symptom": "Severe headache with vision changes", "urgency": "High", "action": "Go to ER immediately"},
        {"symptom": "Decreased fetal movement", "urgency": "High", "action": "Contact doctor immediately"},
        {"symptom": "Fever over 100.4°F (38°C)", "urgency": "Medium", "action": "Contact doctor within 24 hours"},
        {"symptom": "Severe swelling of face/hands", "urgency": "High", "action": "Contact doctor immediately"},
        {"symptom": "Painful urination", "urgency": "Medium", "action": "Contact doctor within 24 hours"},
        {"symptom": "Vaginal fluid leakage", "urgency": "High", "action": "Contact doctor immediately"}
    ]

# ============================================
# AI MODEL CLASSES (Placeholders)
# ============================================
class TextEmotionDetector:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.label_encoder = None
        
    def analyze_text(self, text):
        emotion_keywords = {
            'Happy': ['happy', 'joy', 'excited', 'good', 'great', 'wonderful'],
            'Calm': ['calm', 'peaceful', 'relaxed', 'content'],
            'Anxious': ['anxious', 'worried', 'nervous', 'stressed'],
            'Sad': ['sad', 'tired', 'exhausted', 'sleepy'],
            'Angry': ['angry', 'mad', 'frustrated', 'irritated'],
        }
        
        text_lower = text.lower()
        emotion_scores = {}
        
        for emotion, keywords in emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            emotion_scores[emotion] = score / len(keywords) if len(keywords) > 0 else 0
        
        if emotion_scores:
            dominant_emotion = max(emotion_scores.items(), key=lambda x: x[1])
            return dominant_emotion[0], dominant_emotion[1], emotion_scores, "Text Analysis"
        
        return "Neutral", 0.5, {"Neutral": 1.0}, "Default"

class VoiceEmotionDetector:
    def __init__(self):
        self.emotion_classes = ['Anxious', 'Calm', 'Frustrated', 'Happy', 'Surprised', 'Tired/Sad', 'Uncomfortable']
        
    def predict_emotion(self, audio_path):
        emotion = random.choice(self.emotion_classes)
        confidence = random.uniform(0.7, 0.95)
        scores = {e: random.random() for e in self.emotion_classes}
        total = sum(scores.values())
        scores = {k: v/total for k, v in scores.items()}
        
        return emotion, confidence, scores, emotion, "Voice Analysis"

text_detector = TextEmotionDetector()
voice_detector = VoiceEmotionDetector()

# ============================================
# SESSION STATE INITIALIZATION
# ============================================
if 'login' not in st.session_state:
    st.session_state.login = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'current_emotion' not in st.session_state:
    st.session_state.current_emotion = None
if 'pregnancy_week' not in st.session_state:
    st.session_state.pregnancy_week = 1
if 'trimester' not in st.session_state:
    st.session_state.trimester = 1
if 'page' not in st.session_state:
    st.session_state.page = "login"
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "dashboard"
if 'text_analysis_count' not in st.session_state:
    st.session_state.text_analysis_count = 0
if 'last_text_analyzed' not in st.session_state:
    st.session_state.last_text_analyzed = None

# ============================================
# AUTHENTICATION PAGES WITH LOGO
# ============================================
def show_modern_login():
    # Show loading screen
    if 'loading_complete' not in st.session_state or not st.session_state.loading_complete:
        show_loading_screen()
    
    st.markdown('<div class="auth-modern fade-in">', unsafe_allow_html=True)
    
    # Get logo
    logo_base64 = get_logo_base64()
    
    if logo_base64:
        # Header with circular logo ONLY (no text - your logo already has text)
        st.markdown(f"""
        <div class="logo-header">
            <img src="{logo_base64}" class="logo-img-header" alt="MaternalMind AI">
            <p class="logo-subtext">Pregnancy Wellness Intelligence Platform</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Fallback header if logo not found
        st.markdown('<div class="auth-header-modern">', unsafe_allow_html=True)
        st.markdown('<div style="width: 100px; height: 100px; border-radius: 50%; background: var(--gradient-primary); display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem; color: white; font-size: 2rem; font-weight: bold;">🤰</div>', unsafe_allow_html=True)
        st.markdown('<h1 style="text-align: center; color: var(--dark); margin-bottom: 0.5rem;">MaternalMind AI</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; color: var(--gray-600);">Pregnancy Wellness Intelligence Platform</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="auth-form-modern">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        username = st.text_input("👤 Username", placeholder="Enter your username", key="login_username")
    with col2:
        password = st.text_input("🔒 Password", type="password", placeholder="Enter your password", key="login_password")
    
    if st.button("🚀 Sign In to Dashboard", use_container_width=True, type="primary"):
        if not username or not password:
            st.error("Please enter both username and password")
        else:
            with st.spinner("Authenticating..."):
                c.execute("SELECT id, password_hash, salt FROM users WHERE username = ?", (username,))
                user = c.fetchone()
                
                if user and verify_password(password, user[1], user[2]):
                    user_id = user[0]
                    
                    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
                    user_data = c.fetchone()
                    
                    st.session_state.login = True
                    st.session_state.user = {
                        "id": user_data[0],
                        "username": user_data[1],
                        "email": user_data[3],
                        "trimester": user_data[5],
                        "weeks_pregnant": user_data[6],
                        "baby_name": user_data[7]
                    }
                    st.session_state.pregnancy_week = user_data[6]
                    st.session_state.trimester = user_data[5]
                    st.session_state.page = "main"
                    
                    st.success("✅ Authentication successful!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔓 Forgot Password?", use_container_width=True):
            st.info("Please contact support at support@maternalmind.ai")
    
    with col2:
        if st.button("📝 Create Account", use_container_width=True):
            st.session_state.page = "signup"
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def show_modern_signup():
    # Show loading screen
    if 'loading_complete' not in st.session_state or not st.session_state.loading_complete:
        show_loading_screen()
    
    st.markdown('<div class="auth-modern fade-in">', unsafe_allow_html=True)
    
    # Get logo
    logo_base64 = get_logo_base64()
    
    if logo_base64:
        st.markdown(f"""
        <div class="logo-header">
            <img src="{logo_base64}" class="logo-img-header" alt="MaternalMind AI">
            <p class="logo-subtext">Join MaternalMind AI Platform</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="auth-header-modern">', unsafe_allow_html=True)
        st.markdown('<div style="width: 100px; height: 100px; border-radius: 50%; background: var(--gradient-primary); display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem; color: white; font-size: 2rem; font-weight: bold;">✨</div>', unsafe_allow_html=True)
        st.markdown('<h1 style="text-align: center; color: var(--dark); margin-bottom: 0.5rem;">Create Account</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; color: var(--gray-600);">Join MaternalMind AI Platform</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="auth-form-modern">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input("Username", placeholder="Choose a username", key="signup_username")
        email = st.text_input("Email Address", placeholder="your@email.com", key="signup_email")
    
    with col2:
        full_name = st.text_input("Full Name", placeholder="Your full name", key="signup_fullname")
        phone = st.text_input("Phone (Optional)", placeholder="+1 (555) 123-4567", key="signup_phone")
    
    col1, col2 = st.columns(2)
    with col1:
        password = st.text_input("Password", type="password", 
                                placeholder="At least 8 characters", 
                                key="signup_password")
    
    with col2:
        confirm_password = st.text_input("Confirm Password", type="password", 
                                        placeholder="Re-enter your password",
                                        key="signup_confirm")
    
    if password:
        is_valid, message = validate_password_strength(password)
        if is_valid:
            st.success("✅ Password meets security requirements")
        else:
            st.error(f"❌ {message}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        weeks = st.number_input("Current Week", min_value=1, max_value=42, value=1, 
                               key="signup_weeks")
    
    with col2:
        if weeks <= 13:
            trimester = 1
        elif weeks <= 27:
            trimester = 2
        else:
            trimester = 3
        st.info(f"**Trimester:** {trimester}")
    
    with col3:
        baby_name = st.text_input("Baby's Name (Optional)", placeholder="Our Little One", 
                                 key="signup_baby")
    
    due_date = st.date_input("Expected Due Date", 
                            value=datetime.date.today() + datetime.timedelta(weeks=40-weeks),
                            key="signup_duedate")
    
    col1, col2 = st.columns(2)
    with col1:
        agree_terms = st.checkbox("I agree to the Terms of Service", key="agree_terms")
    with col2:
        agree_privacy = st.checkbox("I agree to the Privacy Policy", key="agree_privacy")
    
    newsletter = st.checkbox("Subscribe to weekly pregnancy tips", value=True, key="newsletter")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        if st.button("🚀 Create My Account", use_container_width=True, type="primary"):
            errors = []
            if not username or len(username) < 3:
                errors.append("Username must be at least 3 characters")
            if not email or "@" not in email:
                errors.append("Valid email is required")
            if not password:
                errors.append("Password is required")
            elif password != confirm_password:
                errors.append("Passwords do not match")
            elif not validate_password_strength(password)[0]:
                errors.append("Password does not meet security requirements")
            if not agree_terms or not agree_privacy:
                errors.append("You must agree to terms and privacy policy")
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                with st.spinner("Creating your secure account..."):
                    try:
                        hashed_password, salt = hash_password(password)
                        
                        c.execute("""INSERT INTO users 
                                    (username, password_hash, email, salt, trimester, 
                                     weeks_pregnant, baby_name, due_date, profile_completed) 
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                (username, hashed_password, email, salt, trimester, 
                                 weeks, baby_name, str(due_date), 0))
                        
                        user_id = c.lastrowid
                        
                        c.execute("""INSERT INTO profile_settings 
                                    (user_id, auto_week_update) 
                                    VALUES (?, ?)""",
                                (user_id, 1))
                        
                        conn.commit()
                        
                        st.success("🎉 Account created successfully!")
                        st.info("Please login with your credentials")
                        time.sleep(2)
                        st.session_state.page = "login"
                        st.rerun()
                        
                    except sqlite3.IntegrityError as e:
                        if "username" in str(e):
                            st.error("Username already exists. Please choose another.")
                        elif "email" in str(e):
                            st.error("Email already registered. Please use another email.")
    
    with col2:
        if st.button("🔙 Back to Login", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()
    
    with col3:
        if st.button("🔄 Clear Form", use_container_width=True):
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# MODERN SIDEBAR WITH LOGO
# ============================================
def create_modern_sidebar():
    with st.sidebar:
        # Get logo
        logo_base64 = get_logo_base64()
        
        if logo_base64:
            # Sidebar with circular logo ONLY (no text)
            st.markdown(f"""
            <div class="sidebar-logo">
                <img src="{logo_base64}" class="sidebar-logo-img" alt="MaternalMind AI">
            </div>
            """, unsafe_allow_html=True)
        else:
            # Fallback sidebar logo
            st.markdown("""
            <div class="sidebar-logo">
                <div style="width: 60px; height: 60px; border-radius: 50%; background: var(--gradient-primary); display: flex; align-items: center; justify-content: center; margin: 0 auto; color: white; font-size: 1.5rem; font-weight: bold;">🤰</div>
            </div>
            """, unsafe_allow_html=True)
        
        if st.session_state.login:
            user = st.session_state.user
            username = user["username"]
            baby_name = user["baby_name"]
            week = user["weeks_pregnant"]
            trimester = user["trimester"]
            
            st.markdown(f"""
            <div style="text-align: center; padding-bottom: 2rem; margin-bottom: 2rem; border-bottom: 1px solid var(--gray-200);">
                <div style="width: 80px; height: 80px; border-radius: 50%; background: var(--gradient-primary); display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem; color: white; font-size: 2rem; font-weight: bold;">{username[0].upper()}</div>
                <div style="font-size: 1.25rem; font-weight: 600; color: var(--dark); margin-bottom: 0.25rem;">{username}</div>
                <div style="font-size: 0.875rem; color: var(--gray-600);">
                    🤰 {baby_name}<br>
                    📅 Week {week} • Trimester {trimester}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        nav_items = [
            ("🏠", "Dashboard", "dashboard"),
            ("🤒", "Symptoms Log", "symptoms"),
            ("🎤", "Voice Analysis", "voice"),
            ("📝", "Text Journal", "text"),
            ("👶", "Baby Tracker", "baby"),
            ("🍎", "Nutrition", "nutrition"),
            ("💪", "Exercise", "exercise"),
            ("💊", "Vitamins", "vitamins"),
            ("🎯", "Recommendations", "recommendations"),
            ("⚙️", "Profile Settings", "settings"),
            ("📄", "Reports", "reports"),
        ]
        
        for icon, label, key in nav_items:
            if st.button(f"{icon} {label}", key=f"nav_{key}", use_container_width=True):
                st.session_state.current_tab = key
                st.rerun()
        
        st.markdown("---")
        st.markdown("### 📈 Weekly Progress")
        
        if st.session_state.login:
            week_progress = min(100, (st.session_state.pregnancy_week / 40) * 100)
            st.markdown(f"""
            <div style="margin: 1rem 0;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="color: var(--gray-700);">Week {st.session_state.pregnancy_week}/40</span>
                    <span style="color: var(--primary); font-weight: 600;">{week_progress:.0f}%</span>
                </div>
                <div class="progress-bar-modern">
                    <div class="progress-fill-modern" style="width: {week_progress}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("### 📊 Quick Stats")
        if st.session_state.login:
            col1, col2 = st.columns(2)
            with col1:
                symptoms_today = get_symptoms_history(st.session_state.user["id"], 1)
                st.metric("Today's Symptoms", len(symptoms_today))
            with col2:
                kicks_today = get_baby_kicks_history(st.session_state.user["id"], 1)
                total_kicks = kicks_today['kicks'].sum() if not kicks_today.empty else 0
                st.metric("Baby Kicks", total_kicks)
        
        st.markdown("---")
        with st.expander("🆘 Emergency Contacts"):
            st.markdown("""
            **Immediate Medical Attention:**
            - 🚨 Severe pain/bleeding
            - 🚨 Decreased movement
            - 🚨 Vision changes
            
            **Emergency Numbers:**
            - General: 911/1122
            - Edhi: 115
            - Rescue: 1122
            """)
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            st.session_state.login = False
            st.session_state.user = None
            st.session_state.page = "login"
            st.rerun()

# ============================================
# FIXED TEXT ANALYSIS TAB - COMPLETELY SOLVED
# ============================================
def show_text_analysis_tab(user_id):
    st.markdown("""
    <div class="fade-in">
        <h2 style="color: var(--dark); margin-bottom: 1.5rem;">📝 Text Journal & Analysis</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="card-modern">', unsafe_allow_html=True)
        st.markdown('<div class="card-header-modern"><span class="card-icon-modern">📝</span><h3 class="card-title-modern">Journal Your Thoughts</h3></div>', unsafe_allow_html=True)
        
        # Create unique keys for this session
        analysis_key = f"text_analysis_{user_id}_{st.session_state.text_analysis_count}"
        
        # Use a container for the form
        form_container = st.container()
        
        with form_container:
            user_text = st.text_area(
                "How are you feeling today?",
                placeholder="Describe your feelings, thoughts, or experiences...\n\nExample: 'I feel anxious about my upcoming appointment but also excited to see the baby's growth.'",
                height=200,
                key=f"text_area_{user_id}"
            )
            
            notes = st.text_input("Additional context (optional):", key=f"notes_{user_id}")
            
            # Use a unique key for the button
            analyze_button = st.button("🧠 Analyze Text Emotion", 
                                      use_container_width=True, 
                                      type="primary",
                                      key=f"analyze_btn_{user_id}_{st.session_state.text_analysis_count}")
        
        if analyze_button:
            if user_text:
                with st.spinner("Analyzing your text..."):
                    # Check if this is new text
                    current_text_hash = hashlib.md5(user_text.encode()).hexdigest()
                    
                    if st.session_state.last_text_analyzed != current_text_hash:
                        # Analyze text
                        emotion, confidence, scores, model_type = text_detector.analyze_text(user_text)
                        
                        # Update session state
                        st.session_state.current_emotion = {
                            'emotion': emotion,
                            'confidence': confidence,
                            'scores': scores,
                            'model_type': model_type,
                            'raw_emotion': emotion,
                            'timestamp': datetime.datetime.now(),
                            'source': 'text',
                            'text_content': user_text,
                            'text_hash': current_text_hash
                        }
                        
                        # Save to database
                        add_emotion(user_id, emotion, confidence, "text_analysis", notes)
                        
                        # Update last analyzed text
                        st.session_state.last_text_analyzed = current_text_hash
                        
                        # Increment counter
                        st.session_state.text_analysis_count += 1
                        
                        st.success("✅ Analysis complete!")
                        st.rerun()
                    else:
                        st.info("This text was already analyzed. Enter new text for fresh analysis.")
            else:
                st.error("Please enter some text to analyze")
        
        with st.expander("💡 Journaling Prompts"):
            st.markdown("""
            **Try writing about:**
            - How your body feels today
            - What you're looking forward to
            - Any worries or concerns
            - Baby movements you've noticed
            - Dreams or hopes for your baby
            
            **Benefits of Journaling:**
            - Reduces stress and anxiety
            - Improves emotional awareness
            - Creates a pregnancy memory
            - Helps identify patterns
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Check for current emotion and verify it's from text analysis
        show_results = False
        
        if 'current_emotion' in st.session_state and st.session_state.current_emotion:
            if st.session_state.current_emotion.get('source') == 'text':
                if 'text_hash' in st.session_state.current_emotion:
                    show_results = True
        
        if show_results:
            emotion = st.session_state.current_emotion['emotion']
            confidence = st.session_state.current_emotion['confidence']
            scores = st.session_state.current_emotion['scores']
            timestamp = st.session_state.current_emotion['timestamp']
            
            st.markdown('<div class="card-modern">', unsafe_allow_html=True)
            st.markdown('<div class="card-header-modern"><span class="card-icon-modern">🎯</span><h3 class="card-title-modern">Analysis Results</h3></div>', unsafe_allow_html=True)
            
            # Show timestamp
            if timestamp:
                if isinstance(timestamp, datetime.datetime):
                    time_str = timestamp.strftime("%I:%M %p")
                    st.caption(f"Analyzed at: {time_str}")
            
            # Emotion display
            emotion_icons = {
                'Happy': '😊', 'Calm': '😌', 'Anxious': '😟', 
                'Sad': '😔', 'Angry': '😠', 'Surprised': '😲',
                'Neutral': '😐'
            }
            
            icon = emotion_icons.get(emotion, '😊')
            
            st.markdown(f"""
            <div style="text-align: center; padding: 1.5rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">{icon}</div>
                <div style="font-size: 2rem; font-weight: 600; color: var(--dark); margin-bottom: 0.5rem;">{emotion}</div>
                <div style="color: var(--gray-600); font-size: 1rem;">Confidence: {confidence:.1%}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Insights
            insights = {
                'Happy': "Great! Positive emotions are wonderful for you and baby.",
                'Calm': "Peaceful moments are precious during pregnancy.",
                'Anxious': "It's normal to feel anxious. Try deep breathing exercises.",
                'Sad': "Pregnancy hormones can affect mood. Be gentle with yourself.",
                'Angry': "Frustration is common. Try talking about your feelings.",
                'Surprised': "Pregnancy brings many surprises! Embrace the journey.",
                'Neutral': "A balanced emotional state is healthy."
            }
            
            st.info(insights.get(emotion, "Your emotional awareness is important for your wellbeing."))
            
            # Clear button
            if st.button("🗑️ Clear Results", use_container_width=True, key="clear_text_results"):
                st.session_state.current_emotion = None
                st.session_state.last_text_analyzed = None
                st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("👆 Enter text above to get started!")

# ============================================
# DASHBOARD TAB
# ============================================
def show_dashboard_tab(user_id):
    user = st.session_state.user
    week = user["weeks_pregnant"]
    trimester = user["trimester"]
    baby_name = user["baby_name"]
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"""
        <div style="margin-bottom: 2rem;">
            <h1 style="color: var(--dark); margin-bottom: 0.5rem;">Welcome back, {user['username']}! 👋</h1>
            <p style="color: var(--gray-600); font-size: 1.1rem;">
                Tracking wellness for <span style="color: var(--primary); font-weight: 600;">{baby_name}</span> • 
                Week <span style="color: var(--primary); font-weight: 600;">{week}</span> • 
                Trimester <span style="color: var(--primary); font-weight: 600;">{trimester}</span>
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        today = datetime.date.today().strftime("%B %d, %Y")
        st.markdown(f"""
        <div class="metric-card-modern">
            <div class="metric-label-modern">Today</div>
            <div class="metric-value-modern">{today}</div>
            <div class="metric-change-modern">📍 Day {((week-1)*7) + (datetime.date.today().weekday()+1)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### 📈 Quick Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        emotions_today = get_emotion_history(user_id, 1)
        emotion = emotions_today.iloc[0]['emotion'] if not emotions_today.empty else "Calm"
        confidence = emotions_today.iloc[0]['confidence'] if not emotions_today.empty else 0.5
        
        emotion_icons = {
            "Happy": "😊", "Calm": "😌", "Anxious": "😟", 
            "Sad": "😔", "Tired": "😴", "Excited": "🎉"
        }
        
        st.markdown(f"""
        <div class="metric-card-modern">
            <div class="metric-label-modern">Today's Mood</div>
            <div class="metric-value-modern">{emotion_icons.get(emotion, '😊')} {emotion}</div>
            <div class="metric-change-modern">{confidence:.0%} confidence</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        symptoms_today = get_symptoms_history(user_id, 1)
        symptom_count = len(symptoms_today)
        
        st.markdown(f"""
        <div class="metric-card-modern">
            <div class="metric-label-modern">Symptoms Today</div>
            <div class="metric-value-modern">{symptom_count}</div>
            <div class="metric-change-modern">🤒 Logged</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        kicks_today = get_baby_kicks_history(user_id, 1)
        total_kicks = kicks_today['kicks'].sum() if not kicks_today.empty else 0
        
        st.markdown(f"""
        <div class="metric-card-modern">
            <div class="metric-label-modern">Baby Activity</div>
            <div class="metric-value-modern">{total_kicks} kicks</div>
            <div class="metric-change-modern">👣 Today</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        nutrition_today = get_nutrition_history(user_id, 1)
        total_calories = nutrition_today['calories'].sum() if not nutrition_today.empty else 0
        
        st.markdown(f"""
        <div class="metric-card-modern">
            <div class="metric-label-modern">Nutrition</div>
            <div class="metric-value-modern">{total_calories}</div>
            <div class="metric-change-modern">🔥 Calories</div>
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="card-modern">', unsafe_allow_html=True)
        st.markdown('<div class="card-header-modern"><span class="card-icon-modern">📊</span><h3 class="card-title-modern">Weekly Progress</h3></div>', unsafe_allow_html=True)
        
        progress = (week / 40) * 100
        st.markdown(f"""
        <div style="margin: 1.5rem 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span style="color: var(--gray-700);">Week {week} of 40</span>
                <span style="color: var(--primary); font-weight: 600;">{progress:.1f}%</span>
            </div>
            <div class="progress-bar-modern">
                <div class="progress-fill-modern" style="width: {progress}%;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 0.5rem; font-size: 0.875rem; color: var(--gray-600);">
                <span>Trimester 1</span>
                <span>Trimester 2</span>
                <span>Trimester 3</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        baby_info = get_baby_info_by_week(week)
        st.markdown(f"""
        <div style="margin-top: 1.5rem; padding: 1rem; background: var(--gray-100); border-radius: 8px;">
            <h4 style="color: var(--dark); margin-bottom: 0.5rem;">👶 Week {week} Development</h4>
            <p style="color: var(--gray-700); line-height: 1.6;">{baby_info}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="card-modern">', unsafe_allow_html=True)
        st.markdown('<div class="card-header-modern"><span class="card-icon-modern">⚡</span><h3 class="card-title-modern">Quick Actions</h3></div>', unsafe_allow_html=True)
        
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            if st.button("🤒 Log Symptom", use_container_width=True):
                st.session_state.current_tab = "symptoms"
                st.rerun()
        
        with col_b:
            if st.button("🎤 Voice Check", use_container_width=True):
                st.session_state.current_tab = "voice"
                st.rerun()
        
        with col_c:
            if st.button("📝 Log Meal", use_container_width=True):
                st.session_state.current_tab = "nutrition"
                st.rerun()
        
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            if st.button("👣 Track Kicks", use_container_width=True):
                st.session_state.current_tab = "baby"
                st.rerun()
        
        with col_b:
            if st.button("💪 Log Exercise", use_container_width=True):
                st.session_state.current_tab = "exercise"
                st.rerun()
        
        with col_c:
            if st.button("📊 View Reports", use_container_width=True):
                st.session_state.current_tab = "reports"
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card-modern">', unsafe_allow_html=True)
        st.markdown('<div class="card-header-modern"><span class="card-icon-modern">🤒</span><h3 class="card-title-modern">Recent Symptoms</h3></div>', unsafe_allow_html=True)
        
        symptoms = get_symptoms_history(user_id, 3)
        if not symptoms.empty:
            for _, row in symptoms.head(3).iterrows():
                intensity_color = f"intensity-{row['intensity']}"
                st.markdown(f"""
                <div style="display: flex; align-items: center; padding: 0.75rem 0; border-bottom: 1px solid var(--gray-200);">
                    <div style="flex: 1;">
                        <div style="font-weight: 500; color: var(--dark);">{row['symptom']}</div>
                        <div style="display: flex; justify-content: space-between; font-size: 0.875rem;">
                            <span class="{intensity_color}">Severity: {row['intensity']}/10</span>
                            <span style="color: var(--gray-600);">{row['date']}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No symptoms logged recently")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="card-modern">', unsafe_allow_html=True)
        st.markdown('<div class="card-header-modern"><span class="card-icon-modern">💡</span><h3 class="card-title-modern">Today\'s Tip</h3></div>', unsafe_allow_html=True)
        
        tips = [
            "Stay hydrated - drink at least 8 glasses of water daily",
            "Practice gentle stretching to relieve back pain",
            "Count baby kicks daily after 28 weeks",
            "Take prenatal vitamins with food",
            "Elevate your feet to reduce swelling",
            "Practice deep breathing for relaxation",
            "Eat small, frequent meals for nausea",
            "Wear comfortable, supportive shoes"
        ]
        
        tip = random.choice(tips)
        st.markdown(f"""
        <div style="padding: 1rem; background: var(--gray-100); border-radius: 8px; margin-top: 1rem;">
            <p style="color: var(--gray-700); line-height: 1.6;">{tip}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# SYMPTOMS TAB
# ============================================
def show_symptoms_tab(user_id):
    st.markdown("""
    <div class="fade-in">
        <h2 style="color: var(--dark); margin-bottom: 1.5rem;">🤒 Symptoms Tracker</h2>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Log Symptom", "📊 Symptom History", "🚨 Emergency Symptoms", "💡 Symptom Guide"])
    
    with tab1:
        st.markdown('<div class="card-modern">', unsafe_allow_html=True)
        st.markdown('<div class="card-header-modern"><span class="card-icon-modern">📝</span><h3 class="card-title-modern">Log New Symptom</h3></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            symptom_type = st.selectbox(
                "Symptom Type",
                ["Nausea/Vomiting", "Headache", "Back Pain", "Fatigue", "Swelling (Edema)",
                 "Heartburn", "Shortness of Breath", "Leg Cramps", "Braxton Hicks", 
                 "Pelvic Pressure", "Constipation", "Insomnia", "Other"]
            )
            
            if symptom_type == "Other":
                symptom_type = st.text_input("Specify symptom")
        
        with col2:
            intensity = st.slider(
                "Intensity (1-10)",
                min_value=1,
                max_value=10,
                value=5
            )
            
            intensity_color = f"intensity-{intensity}"
            st.markdown(f'<p class="{intensity_color}" style="text-align: center; font-weight: bold;">Intensity Level: {intensity}/10</p>', unsafe_allow_html=True)
        
        duration_hours = st.number_input("Duration (hours)", min_value=0.5, max_value=24.0, value=1.0, step=0.5)
        
        notes = st.text_area("Notes (Optional)", placeholder="Describe your symptom in detail...", height=100)
        
        col1, col2 = st.columns(2)
        with col1:
            resolved = st.checkbox("Symptom has resolved", value=False)
        with col2:
            reported = st.checkbox("Reported to doctor", value=False)
        
        if st.button("💾 Save Symptom Log", use_container_width=True, type="primary"):
            if symptom_type:
                add_symptom_log(user_id, symptom_type, intensity, duration_hours, notes, resolved)
                st.success("✅ Symptom logged successfully!")
                st.rerun()
            else:
                st.error("Please select or specify a symptom type")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="card-modern">', unsafe_allow_html=True)
        st.markdown('<div class="card-header-modern"><span class="card-icon-modern">📋</span><h3 class="card-title-modern">Common Symptoms This Trimester</h3></div>', unsafe_allow_html=True)
        
        trimester = st.session_state.trimester
        common_symptoms = get_symptom_patterns(trimester)
        
        for symptom in common_symptoms:
            with st.expander(f"{symptom['symptom']} ({symptom['frequency']}% experience)"):
                st.markdown(f"""
                **Severity:** {symptom['severity']}
                
                **Management Tips:**
                {symptom['tips']}
                """)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="card-modern">', unsafe_allow_html=True)
        st.markdown('<div class="card-header-modern"><span class="card-icon-modern">📊</span><h3 class="card-title-modern">Symptom History</h3></div>', unsafe_allow_html=True)
        
        days_filter = st.selectbox("Time Period", ["Last 7 days", "Last 30 days", "Last 90 days"], key="symptom_days")
        days_map = {"Last 7 days": 7, "Last 30 days": 30, "Last 90 days": 90}
        days = days_map[days_filter]
        
        symptoms_df = get_symptoms_history(user_id, days)
        
        if not symptoms_df.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                total_symptoms = len(symptoms_df)
                st.metric("Total Symptoms", total_symptoms)
            
            with col2:
                avg_intensity = symptoms_df['intensity'].mean()
                st.metric("Avg. Intensity", f"{avg_intensity:.1f}/10")
            
            with col3:
                resolved_count = symptoms_df['resolved'].sum()
                st.metric("Resolved", f"{resolved_count}/{total_symptoms}")
            
            st.dataframe(
                symptoms_df[['date', 'symptom', 'intensity', 'duration_hours', 'resolved']],
                use_container_width=True,
                column_config={
                    "date": "Date",
                    "symptom": "Symptom",
                    "intensity": st.column_config.NumberColumn(
                        "Intensity",
                        help="1-10 scale",
                        format="%d ⭐"
                    ),
                    "duration_hours": "Duration (hrs)",
                    "resolved": "Resolved"
                }
            )
            
            symptoms_df['date'] = pd.to_datetime(symptoms_df['date'])
            weekly_symptoms = symptoms_df.resample('W', on='date')['symptom'].count()
            
            fig = px.line(weekly_symptoms.reset_index(), x='date', y='symptom',
                         title="Weekly Symptom Frequency",
                         labels={'symptom': 'Number of Symptoms', 'date': 'Week'})
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.info("No symptoms logged in this period")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="card-modern">', unsafe_allow_html=True)
        st.markdown('<div class="card-header-modern"><span class="card-icon-modern">🚨</span><h3 class="card-title-modern">Emergency Symptoms</h3></div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div style="padding: 1rem; margin: 1rem 0; border-left: 4px solid var(--danger); background: rgba(245, 101, 101, 0.1); border-radius: 8px;">
        <h4 style="margin: 0; color: var(--dark);">⚠️ Seek Immediate Medical Attention For:</h4>
        <p style="margin: 0.5rem 0 0 0; color: var(--gray-700);">If you experience any of these symptoms, contact your healthcare provider immediately.</p>
        </div>
        """, unsafe_allow_html=True)
        
        emergency_list = get_emergency_symptoms_list()
        for item in emergency_list:
            urgency_color = "text-danger" if item["urgency"] == "High" else "text-warning"
            st.markdown(f"""
            <div style="padding: 1rem; margin: 0.5rem 0; border-left: 4px solid var(--danger); background: rgba(245, 101, 101, 0.1); border-radius: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-weight: 600; color: var(--dark);">{item['symptom']}</div>
                    <span style="color: var(--danger); font-weight: 600;">{item['urgency']} Priority</span>
                </div>
                <div style="color: var(--gray-700); margin-top: 0.5rem;">{item['action']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("#### 📝 Report Emergency Symptom")
        
        col1, col2 = st.columns(2)
        with col1:
            emergency_symptom = st.selectbox(
                "Emergency Symptom",
                [item['symptom'] for item in emergency_list] + ["Other"],
                key="emergency_symptom"
            )
            
            if emergency_symptom == "Other":
                emergency_symptom = st.text_input("Specify emergency symptom")
        
        with col2:
            severity = st.selectbox(
                "Severity Level",
                ["Mild", "Moderate", "Severe", "Critical"],
                key="emergency_severity"
            )
        
        action_taken = st.text_area("Action Taken", placeholder="What did you do? (e.g., Called doctor, Went to ER)")
        doctor_contacted = st.checkbox("Doctor has been contacted", value=False)
        emergency_notes = st.text_area("Additional Notes", placeholder="Any additional information...")
        
        if st.button("🚨 Report Emergency Symptom", use_container_width=True, type="secondary"):
            if emergency_symptom and action_taken:
                add_emergency_symptom(user_id, emergency_symptom, severity, action_taken, doctor_contacted, emergency_notes)
                st.success("✅ Emergency symptom reported. Please follow up with your healthcare provider.")
                st.rerun()
            else:
                st.error("Please fill in all required fields")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab4:
        st.markdown('<div class="card-modern">', unsafe_allow_html=True)
        st.markdown('<div class="card-header-modern"><span class="card-icon-modern">💡</span><h3 class="card-title-modern">Symptom Management Guide</h3></div>', unsafe_allow_html=True)
        
        trimester = st.session_state.trimester
        common_symptoms = get_symptom_patterns(trimester)
        
        for symptom in common_symptoms:
            with st.expander(f"📌 {symptom['symptom']}"):
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.metric("Frequency", f"{symptom['frequency']}%")
                    st.metric("Typical Severity", symptom['severity'])
                
                with col2:
                    st.markdown(f"""
                    **Management Strategies:**
                    {symptom['tips']}
                    
                    **When to Call Doctor:**
                    - If symptom worsens suddenly
                    - If accompanied by fever
                    - If affecting daily activities
                    """)
        
        st.markdown("---")
        st.markdown("#### 🏥 General Guidelines")
        
        st.markdown("""
        **Monitoring Tips:**
        1. **Track Patterns**: Note when symptoms occur and what makes them better/worse
        2. **Stay Hydrated**: Drink plenty of water throughout the day
        3. **Rest**: Listen to your body and rest when needed
        4. **Communicate**: Share your symptom log with your healthcare provider
        
        **Red Flags Requiring Immediate Attention:**
        - Severe or sudden pain
        - Heavy bleeding
        - Decreased fetal movement
        - Vision changes or severe headache
        - Fever over 100.4°F (38°C)
        """)
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# VOICE TAB
# ============================================
def show_voice_tab(user_id):
    st.markdown("""
    <div class="fade-in">
        <h2 style="color: var(--dark); margin-bottom: 1.5rem;">🎤 Voice Emotion Analysis</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="card-modern">', unsafe_allow_html=True)
        st.markdown('<div class="card-header-modern"><span class="card-icon-modern">🎤</span><h3 class="card-title-modern">Upload Voice Recording</h3></div>', unsafe_allow_html=True)
        
        st.markdown("""
        **How it works:**
        1. Record or upload a short audio clip of your voice
        2. Our AI analyzes emotional tones in your voice
        3. Get insights about your emotional state
        4. Receive personalized recommendations
        """)
        
        uploaded_file = st.file_uploader(
            "Choose an audio file",
            type=['wav', 'mp3', 'm4a'],
            help="Upload a 3-10 second audio clip for best results"
        )
        
        if uploaded_file:
            st.audio(uploaded_file, format='audio/wav')
            
            if st.button("🧠 Analyze Voice Emotion", use_container_width=True, type="primary"):
                with st.spinner("Analyzing voice patterns..."):
                    try:
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_path = tmp_file.name
                        
                        emotion, confidence, scores, raw_emotion, model_type = voice_detector.predict_emotion(tmp_path)
                        
                        st.session_state.current_emotion = {
                            'emotion': emotion,
                            'confidence': confidence,
                            'scores': scores,
                            'raw_emotion': raw_emotion,
                            'model_type': model_type,
                            'timestamp': datetime.datetime.now(),
                            'source': 'voice'
                        }
                        
                        add_emotion(user_id, emotion, confidence, "voice_analysis", "")
                        
                        os.unlink(tmp_path)
                        
                        st.success("✅ Voice analysis complete!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Analysis error: {str(e)}")
        
        with st.expander("💡 Tips for Better Analysis"):
            st.markdown("""
            **For best results:**
            - Record in a quiet environment
            - Speak naturally about how you're feeling
            - Keep recording between 3-10 seconds
            - Avoid background noise
            
            **Example phrases:**
            - "I'm feeling happy and energetic today"
            - "I've been a bit anxious about my appointment"
            - "Today I'm tired but content"
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        if st.session_state.current_emotion and st.session_state.current_emotion.get('source') == 'voice':
            emotion = st.session_state.current_emotion['emotion']
            confidence = st.session_state.current_emotion['confidence']
            scores = st.session_state.current_emotion['scores']
            
            st.markdown('<div class="card-modern">', unsafe_allow_html=True)
            st.markdown('<div class="card-header-modern"><span class="card-icon-modern">🎯</span><h3 class="card-title-modern">Analysis Results</h3></div>', unsafe_allow_html=True)
            
            emotion_icons = {
                "Happy": "😊", "Calm": "😌", "Anxious": "😟", 
                "Sad": "😔", "Tired": "😴", "Excited": "🎉",
                "Frustrated": "😤", "Surprised": "😲", "Uncomfortable": "😣"
            }
            
            st.markdown(f"""
            <div style="text-align: center; padding: 1.5rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">{emotion_icons.get(emotion, '😊')}</div>
                <div style="font-size: 1.5rem; font-weight: 600; color: var(--dark); margin-bottom: 0.5rem;">{emotion}</div>
                <div style="color: var(--gray-600);">Confidence: {confidence:.1%}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if scores:
                fig = go.Figure(data=[
                    go.Bar(x=list(scores.keys()), y=list(scores.values()),
                          marker_color='#8B5FBF')
                ])
                fig.update_layout(
                    title="Emotion Distribution",
                    height=300,
                    xaxis_tickangle=45
                )
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("👆 Upload an audio file to analyze your voice emotion")

# ============================================
# BABY TRACKER TAB
# ============================================
def show_baby_tracker_tab(user_id):
    st.markdown("""
    <div class="fade-in">
        <h2 style="color: var(--dark); margin-bottom: 1.5rem;">👶 Baby Development & Tracking</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        week = st.session_state.pregnancy_week
        baby_name = st.session_state.user["baby_name"]
        
        st.markdown('<div class="card-modern">', unsafe_allow_html=True)
        st.markdown(f'<div class="card-header-modern"><span class="card-icon-modern">👶</span><h3 class="card-title-modern">Week {week} Development</h3></div>', unsafe_allow_html=True)
        
        baby_info = get_baby_info_by_week(week)
        st.markdown(f"""
        <div style="padding: 1rem; background: var(--gray-100); border-radius: 8px; margin: 1rem 0;">
            {baby_info}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### 🔍 Explore Different Weeks")
        explore_week = st.slider(
            "Select week to explore:",
            min_value=1,
            max_value=40,
            value=week,
            key="explore_week"
        )
        
        if explore_week != week:
            explore_info = get_baby_info_by_week(explore_week)
            st.markdown(f"""
            <div style="padding: 1rem; background: var(--gray-100); border-radius: 8px; margin-top: 1rem;">
                {explore_info}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="card-modern">', unsafe_allow_html=True)
        st.markdown('<div class="card-header-modern"><span class="card-icon-modern">📏</span><h3 class="card-title-modern">Baby Size Comparison</h3></div>', unsafe_allow_html=True)
        
        size_milestones = {
            4: ("Blueberry", "🔵", "Tiny but growing!"),
            8: ("Raspberry", "🟣", "All organs forming"),
            12: ("Lime", "🟢", "First trimester complete"),
            16: ("Avocado", "🟤", "Can hear your voice"),
            20: ("Banana", "🟡", "Midpoint of pregnancy"),
            24: ("Corn", "🌽", "Viability milestone"),
            28: ("Eggplant", "🍆", "Third trimester begins"),
            32: ("Squash", "🎃", "Getting ready for birth"),
            36: ("Watermelon", "🍉", "Full term reached"),
            40: ("Pumpkin", "🎃", "Ready to meet you!")
        }
        
        closest = min(size_milestones.keys(), key=lambda x: abs(x - week))
        fruit, emoji, note = size_milestones[closest]
        
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">{emoji}</div>
            <div style="font-size: 1.5rem; font-weight: 600; color: var(--dark); margin-bottom: 0.5rem;">{fruit}</div>
            <div style="color: var(--gray-600);">{note}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card-modern">', unsafe_allow_html=True)
        st.markdown('<div class="card-header-modern"><span class="card-icon-modern">👣</span><h3 class="card-title-modern">Baby Kick Counter</h3></div>', unsafe_allow_html=True)
        
        if week >= 16:
            col_a, col_b = st.columns(2)
            with col_a:
                kicks = st.number_input("Kicks:", min_value=0, max_value=100, value=10)
            with col_b:
                duration = st.number_input("Minutes:", min_value=1, max_value=60, value=10)
            
            kick_notes = st.text_input("Notes (optional):")
            
            if st.button("💖 Log Kicks", use_container_width=True):
                add_baby_kick(user_id, kicks, duration, kick_notes)
                st.success(f"✅ Logged {kicks} kicks!")
                st.rerun()
            
            today_kicks_df = get_baby_kicks_history(user_id, 1)
            
            if not today_kicks_df.empty:
                total_today = today_kicks_df['kicks'].sum()
                st.markdown(f"""
                <div style="text-align: center; padding: 1.5rem; margin-top: 1rem;">
                    <div style="font-size: 2.5rem; font-weight: 600; color: var(--primary);">{total_today}</div>
                    <div style="color: var(--gray-600);">kicks today</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("No kicks logged today yet.")
        else:
            st.info(f"""
            **Baby movements start around week 16-20.**
            
            You're at week {week}. 
            Expect fluttering sensations soon!
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="card-modern">', unsafe_allow_html=True)
        st.markdown('<div class="card-header-modern"><span class="card-icon-modern">📊</span><h3 class="card-title-modern">Kick History</h3></div>', unsafe_allow_html=True)
        
        if week >= 16:
            kicks_history = get_baby_kicks_history(user_id, 7)
            if not kicks_history.empty:
                kicks_history['date'] = pd.to_datetime(kicks_history['date'])
                daily_kicks = kicks_history.groupby('date')['kicks'].sum().reset_index()
                
                fig = px.line(daily_kicks, x='date', y='kicks',
                             title="Daily Baby Kicks (7 Days)",
                             markers=True)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Start tracking kicks to see history!")
        else:
            st.info("Kick tracking begins around week 16")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# NUTRITION TAB
# ============================================
def show_nutrition_tab(user_id):
    st.markdown("""
    <div class="fade-in">
        <h2 style="color: var(--dark); margin-bottom: 1.5rem;">🍎 Nutrition & Diet Tracker</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<div class="card-modern">', unsafe_allow_html=True)
        st.markdown('<div class="card-header-modern"><span class="card-icon-modern">📝</span><h3 class="card-title-modern">Log Meal</h3></div>', unsafe_allow_html=True)
        
        meal_type = st.selectbox(
            "Meal Type:",
            ["Breakfast", "Lunch", "Dinner", "Snack", "Other"]
        )
        
        food_items = st.text_input("Food Items:", placeholder="e.g., Oatmeal, banana, milk")
        
        calories = st.number_input("Calories (approx):", min_value=0, max_value=2000, value=300)
        
        nutrients = st.multiselect(
            "Main Nutrients:",
            ["Protein", "Carbs", "Fats", "Fiber", "Iron", "Calcium", "Vitamin C", "Folate"]
        )
        
        notes = st.text_input("Notes (optional):")
        
        if st.button("➕ Log Meal", use_container_width=True):
            add_nutrition_log(user_id, meal_type, food_items, calories, ", ".join(nutrients), notes)
            st.success(f"✅ Logged {meal_type}!")
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="card-modern">', unsafe_allow_html=True)
        st.markdown('<div class="card-header-modern"><span class="card-icon-modern">📊</span><h3 class="card-title-modern">Today\'s Nutrition</h3></div>', unsafe_allow_html=True)
        
        today_nutrition = get_nutrition_history(user_id, 1)
        if not today_nutrition.empty:
            total_calories = today_nutrition['calories'].sum()
            meal_count = len(today_nutrition)
            
            st.metric("Total Calories", total_calories)
            st.metric("Meals Logged", meal_count)
            
            st.markdown("#### 🥗 Nutrient Summary")
            all_nutrients = []
            for nutrients_str in today_nutrition['nutrients']:
                if nutrients_str:
                    all_nutrients.extend([n.strip() for n in nutrients_str.split(',')])
            
            if all_nutrients:
                nutrient_counts = pd.Series(all_nutrients).value_counts()
                for nutrient, count in nutrient_counts.items():
                    st.markdown(f"- **{nutrient}**: {count} meal(s)")
        else:
            st.info("No meals logged today yet.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        trimester = st.session_state.trimester
        week = st.session_state.pregnancy_week
        
        st.markdown('<div class="card-modern">', unsafe_allow_html=True)
        st.markdown('<div class="card-header-modern"><span class="card-icon-modern">💡</span><h3 class="card-title-modern">Nutrition Recommendations</h3></div>', unsafe_allow_html=True)
        
        trimester_nutrition = {
            1: {
                "focus": "Folic acid, iron, hydration",
                "calories": "No extra calories needed",
                "key_foods": ["Leafy greens", "Citrus fruits", "Whole grains", "Lean protein"]
            },
            2: {
                "focus": "Protein, calcium, omega-3",
                "calories": "+300-350 calories/day",
                "key_foods": ["Dairy", "Nuts & seeds", "Fish", "Legumes"]
            },
            3: {
                "focus": "Iron, vitamin K, fiber",
                "calories": "+450-500 calories/day",
                "key_foods": ["Lean meats", "Berries", "Avocado", "Sweet potatoes"]
            }
        }
        
        current_rec = trimester_nutrition.get(trimester, trimester_nutrition[1])
        
        st.markdown(f"""
        **Trimester {trimester} Focus:** {current_rec['focus']}
        
        **Calorie Needs:** {current_rec['calories']}
        
        **Key Foods to Include:**
        """)
        
        for food in current_rec['key_foods']:
            st.markdown(f"- {food}")
        
        week_tips = {
            6: ["🍵 Ginger tea for nausea", "🍪 Crackers before getting out of bed"],
            12: ["🥩 Increase protein intake", "🍊 Focus on iron-rich foods"],
            20: ["🐟 Add Omega-3 foods", "🥛 Boost calcium intake"],
            28: ["🌾 Increase fiber", "💧 Stay well-hydrated"],
            36: ["🍎 Small frequent meals", "🥦 Nutrient-dense foods"]
        }
        
        if week in week_tips:
            st.markdown("#### 📅 This Week's Tips")
            for tip in week_tips[week]:
                st.markdown(f"- {tip}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="card-modern">', unsafe_allow_html=True)
        st.markdown('<div class="card-header-modern"><span class="card-icon-modern">📈</span><h3 class="card-title-modern">Nutrition Trends</h3></div>', unsafe_allow_html=True)
        
        nutrition_7d = get_nutrition_history(user_id, 7)
        if not nutrition_7d.empty:
            nutrition_7d['date'] = pd.to_datetime(nutrition_7d['date'])
            daily_calories = nutrition_7d.groupby('date')['calories'].sum().reset_index()
            
            fig = px.bar(daily_calories, x='date', y='calories',
                        title="Daily Calories (7 Days)",
                        color='calories',
                        color_continuous_scale='viridis')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Log your meals to see nutrition trends!")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# EXERCISE TAB
# ============================================
def show_exercise_tab(user_id):
    st.markdown("""
    <div class="fade-in">
        <h2 style="color: var(--dark); margin-bottom: 1.5rem;">💪 Exercise & Activity Tracker</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<div class="card-modern">', unsafe_allow_html=True)
        st.markdown('<div class="card-header-modern"><span class="card-icon-modern">📝</span><h3 class="card-title-modern">Log Exercise</h3></div>', unsafe_allow_html=True)
        
        exercise_type = st.selectbox(
            "Exercise Type:",
            ["Walking", "Prenatal Yoga", "Swimming", "Light Strength", "Stretching", 
             "Stationary Bike", "Pilates", "Dancing", "Other"]
        )
        
        duration = st.number_input("Duration (minutes):", min_value=1, max_value=180, value=30)
        
        intensity = st.select_slider(
            "Intensity:",
            options=["Very Light", "Light", "Moderate", "Vigorous"],
            value="Moderate"
        )
        
        calories = st.number_input("Calories Burned (approx):", min_value=0, max_value=1000, value=150)
        
        notes = st.text_input("Notes (optional):")
        
        if st.button("➕ Log Exercise", use_container_width=True):
            add_exercise_log(user_id, exercise_type, duration, intensity, calories, notes)
            st.success(f"✅ Logged {exercise_type}!")
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="card-modern">', unsafe_allow_html=True)
        st.markdown('<div class="card-header-modern"><span class="card-icon-modern">📊</span><h3 class="card-title-modern">Today\'s Activity</h3></div>', unsafe_allow_html=True)
        
        today_exercise = get_exercise_history(user_id, 1)
        if not today_exercise.empty:
            total_minutes = today_exercise['duration_minutes'].sum()
            total_calories = today_exercise['calories_burned'].sum()
            
            st.metric("Total Minutes", total_minutes)
            st.metric("Calories Burned", total_calories)
            
            st.markdown("#### 🏃‍♀️ Activities Today")
            for _, row in today_exercise.iterrows():
                st.markdown(f"- **{row['exercise_type']}**: {row['duration_minutes']} min")
        else:
            st.info("No exercise logged today yet.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        trimester = st.session_state.trimester
        
        st.markdown('<div class="card-modern">', unsafe_allow_html=True)
        st.markdown('<div class="card-header-modern"><span class="card-icon-modern">💡</span><h3 class="card-title-modern">Exercise Recommendations</h3></div>', unsafe_allow_html=True)
        
        trimester_exercise = {
            1: {
                "safe": ["Walking", "Swimming", "Prenatal yoga", "Light stretching"],
                "avoid": ["High-impact sports", "Contact sports", "Hot yoga"],
                "frequency": "30 minutes daily",
                "benefits": "Reduces fatigue, improves mood"
            },
            2: {
                "safe": ["Walking", "Swimming", "Prenatal yoga", "Light strength training"],
                "avoid": ["Exercises on back", "Heavy lifting", "Balance exercises"],
                "frequency": "30 minutes daily",
                "benefits": "Reduces back pain, improves circulation"
            },
            3: {
                "safe": ["Walking", "Swimming", "Prenatal yoga", "Pelvic exercises"],
                "avoid": ["High-intensity", "Exercises on back", "Jumping"],
                "frequency": "20-30 minutes daily",
                "benefits": "Eases labor, reduces swelling"
            }
        }
        
        current_rec = trimester_exercise.get(trimester, trimester_exercise[1])
        
        st.markdown(f"""
        **Trimester {trimester} Guidelines:**
        
        **Safe Exercises:**
        """)
        for exercise in current_rec["safe"]:
            st.markdown(f"- {exercise}")
        
        st.markdown(f"""
        **Avoid:**
        """)
        for exercise in current_rec["avoid"]:
            st.markdown(f"- {exercise}")
        
        st.markdown(f"""
        **Frequency:** {current_rec['frequency']}
        
        **Benefits:** {current_rec['benefits']}
        """)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="card-modern">', unsafe_allow_html=True)
        st.markdown('<div class="card-header-modern"><span class="card-icon-modern">📈</span><h3 class="card-title-modern">Activity Trends</h3></div>', unsafe_allow_html=True)
        
        exercise_7d = get_exercise_history(user_id, 7)
        if not exercise_7d.empty:
            exercise_7d['date'] = pd.to_datetime(exercise_7d['date'])
            daily_minutes = exercise_7d.groupby('date')['duration_minutes'].sum().reset_index()
            
            fig = px.bar(daily_minutes, x='date', y='duration_minutes',
                        title="Daily Exercise Minutes (7 Days)",
                        color='duration_minutes',
                        color_continuous_scale='blues')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Log your exercises to see activity trends!")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# VITAMINS TAB
# ============================================
def show_vitamins_tab(user_id):
    st.markdown("""
    <div class="fade-in">
        <h2 style="color: var(--dark); margin-bottom: 1.5rem;">💊 Vitamins & Supplements</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<div class="card-modern">', unsafe_allow_html=True)
        st.markdown('<div class="card-header-modern"><span class="card-icon-modern">📝</span><h3 class="card-title-modern">Log Vitamin</h3></div>', unsafe_allow_html=True)
        
        vitamin_name = st.selectbox(
            "Vitamin/Supplement:",
            ["Prenatal Multivitamin", "Folic Acid", "Iron", "Calcium", "Vitamin D", 
             "Omega-3 DHA", "Vitamin C", "Magnesium", "Probiotics", "Other"]
        )
        
        taken = st.radio("Taken today?", ["Yes", "No"], horizontal=True)
        
        dosage = st.text_input("Dosage (optional):", placeholder="e.g., 400 mcg")
        
        notes = st.text_input("Notes (optional):")
        
        if st.button("➕ Log Vitamin", use_container_width=True):
            add_vitamin_log(user_id, vitamin_name, taken == "Yes", dosage, notes)
            st.success(f"✅ Logged {vitamin_name}!")
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="card-modern">', unsafe_allow_html=True)
        st.markdown('<div class="card-header-modern"><span class="card-icon-modern">📊</span><h3 class="card-title-modern">Today\'s Intake</h3></div>', unsafe_allow_html=True)
        
        today_vitamins = get_vitamin_history(user_id, 1)
        if not today_vitamins.empty:
            taken_count = today_vitamins['taken'].sum()
            total_count = len(today_vitamins)
            
            st.metric("Taken Today", f"{taken_count}/{total_count}")
            
            st.markdown("#### 💊 Today's Vitamins")
            for _, row in today_vitamins.iterrows():
                status = "✅" if row['taken'] else "❌"
                st.markdown(f"{status} **{row['vitamin_name']}**")
                if row['dosage']:
                    st.markdown(f"  _Dosage: {row['dosage']}_")
        else:
            st.info("No vitamins logged today yet.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        trimester = st.session_state.trimester
        
        st.markdown('<div class="card-modern">', unsafe_allow_html=True)
        st.markdown('<div class="card-header-modern"><span class="card-icon-modern">💡</span><h3 class="card-title-modern">Vitamin Recommendations</h3></div>', unsafe_allow_html=True)
        
        essential_vitamins = [
            "💊 Prenatal Multivitamin: Daily",
            "💊 Folic Acid: 400-800 mcg daily",
            "💊 Iron: 27 mg daily (as needed)",
            "💊 Calcium + Vitamin D: 1000 mg + 600 IU",
            "💊 Omega-3 DHA: 200-300 mg daily"
        ]
        
        st.markdown("#### 💊 Essential Vitamins")
        for vitamin in essential_vitamins:
            st.markdown(f"- {vitamin}")
        
        optional_supplements = [
            "🌿 Ginger: For nausea (as tea or supplement)",
            "🌿 Probiotics: For digestive health",
            "🌿 Magnesium: For leg cramps (consult doctor)",
            "🌿 Vitamin B6: For nausea relief"
        ]
        
        st.markdown("#### 🌿 Optional Supplements")
        for supplement in optional_supplements:
            st.markdown(f"- {supplement}")
        
        st.markdown("#### 💡 Important Tips")
        tips = [
            "Take prenatal vitamins with food",
            "Iron is best absorbed with Vitamin C",
            "Calcium can interfere with iron absorption",
            "Always consult doctor before adding supplements"
        ]
        
        for tip in tips:
            st.markdown(f"- {tip}")
        
        trimester_tips = {
            1: ["Focus on folic acid", "Start prenatal vitamins early"],
            2: ["Continue all essentials", "Consider Omega-3 for brain development"],
            3: ["Maintain all vitamins", "Extra iron may be needed"]
        }
        
        if trimester in trimester_tips:
            st.markdown(f"#### 📅 Trimester {trimester} Specific")
            for tip in trimester_tips[trimester]:
                st.markdown(f"- {tip}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="card-modern">', unsafe_allow_html=True)
        st.markdown('<div class="card-header-modern"><span class="card-icon-modern">📈</span><h3 class="card-title-modern">Compliance History</h3></div>', unsafe_allow_html=True)
        
        vitamins_7d = get_vitamin_history(user_id, 7)
        if not vitamins_7d.empty:
            vitamins_7d['date'] = pd.to_datetime(vitamins_7d['date'])
            daily_compliance = vitamins_7d.groupby('date')['taken'].mean().reset_index()
            daily_compliance['compliance_percent'] = daily_compliance['taken'] * 100
            
            fig = px.line(daily_compliance, x='date', y='compliance_percent',
                         title="Daily Vitamin Compliance (7 Days)",
                         markers=True,
                         labels={'compliance_percent': 'Compliance %', 'date': 'Date'})
            fig.update_yaxes(range=[0, 100])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Log your vitamins to see compliance trends!")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# RECOMMENDATIONS TAB
# ============================================
def show_recommendations_tab(user_id):
    st.markdown("""
    <div class="fade-in">
        <h2 style="color: var(--dark); margin-bottom: 1.5rem;">🎯 Personalized Recommendations</h2>
    </div>
    """, unsafe_allow_html=True)
    
    user = st.session_state.user
    week = user["weeks_pregnant"]
    trimester = user["trimester"]
    baby_name = user["baby_name"]
    
    emotions_df = get_emotion_history(user_id, 1)
    if not emotions_df.empty:
        latest_emotion = emotions_df.iloc[0]['emotion']
        latest_confidence = emotions_df.iloc[0]['confidence']
    else:
        latest_emotion = "Calm"
        latest_confidence = 0.5
    
    symptoms_df = get_symptoms_history(user_id, 3)
    
    st.markdown(f"""
    <div class="card-modern">
        <div class="card-header-modern">
            <span class="card-icon-modern">👤</span>
            <h3 class="card-title-modern">Personalized for You</h3>
        </div>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 1rem;">
            <div style="text-align: center;">
                <div style="font-size: 0.875rem; color: var(--gray-600);">Current Emotion</div>
                <div style="font-size: 1.25rem; font-weight: 600; color: var(--dark);">{latest_emotion}</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 0.875rem; color: var(--gray-600);">Pregnancy Week</div>
                <div style="font-size: 1.25rem; font-weight: 600; color: var(--dark);">{week}</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 0.875rem; color: var(--gray-600);">Trimester</div>
                <div style="font-size: 1.25rem; font-weight: 600; color: var(--dark);">{trimester}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎭 Emotional", "🤒 Symptoms", "🍎 Nutrition", "💪 Exercise", "💊 Vitamins"])
    
    with tab1:
        st.markdown('<div class="card-modern">', unsafe_allow_html=True)
        st.markdown('<div class="card-header-modern"><span class="card-icon-modern">🎭</span><h3 class="card-title-modern">Emotional Wellness</h3></div>', unsafe_allow_html=True)
        
        emotional_recs = {
            'Anxious': [
                "Practice deep breathing: 4 seconds in, 7 hold, 8 out",
                "Write down your worries in a pregnancy journal",
                "Talk to your partner about how you're feeling",
                "Listen to calming music or nature sounds",
                "Try prenatal yoga or gentle stretching"
            ],
            'Calm': [
                "Enjoy this peaceful moment - it's precious",
                "Practice gratitude journaling about your pregnancy",
                "Share your calm feelings with your partner",
                "Take a gentle walk in nature",
                "Meditate for 10 minutes focusing on baby"
            ],
            'Happy': [
                "Capture this happy moment in your pregnancy journal",
                "Share the joy with loved ones",
                "Do something special to celebrate",
                "Take prenatal photos to remember this time",
                "Play your favorite music for you and baby"
            ],
            'Sad': [
                "Allow yourself to feel these emotions - they're valid",
                "Reach out to a loved one or support group",
                "Gentle movement can help boost mood",
                "Consider speaking with a counselor specializing in prenatal care",
                "Remember this is temporary and help is available"
            ]
        }
        
        recs = emotional_recs.get(latest_emotion, [
            "Be kind to yourself today",
            "Rest when you need to",
            "Stay hydrated and nourished",
            "Connect with your baby through gentle touch"
        ])
        
        st.markdown("#### 💭 Based on your current emotion:")
        for i, rec in enumerate(recs[:4], 1):
            st.markdown(f"**{i}.** {rec}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="card-modern">', unsafe_allow_html=True)
        st.markdown('<div class="card-header-modern"><span class="card-icon-modern">🤒</span><h3 class="card-title-modern">Symptom Management</h3></div>', unsafe_allow_html=True)
        
        if not symptoms_df.empty:
            common_symptoms = symptoms_df['symptom'].value_counts().head(3)
            
            st.markdown("#### 📋 Based on your recent symptoms:")
            for symptom, count in common_symptoms.items():
                st.markdown(f"**{symptom}** ({count} times recently)")
                
                symptom_tips = {
                    "Nausea/Vomiting": ["Eat small, frequent meals", "Try ginger tea or candies", "Avoid strong smells"],
                    "Headache": ["Stay hydrated", "Rest in a dark room", "Gentle neck stretches"],
                    "Back Pain": ["Use pregnancy pillow", "Practice good posture", "Gentle stretching"],
                    "Fatigue": ["Rest when possible", "Short naps during day", "Gentle walks for energy"],
                    "Swelling": ["Elevate feet", "Stay hydrated", "Limit salt intake"],
                    "Heartburn": ["Eat smaller meals", "Avoid spicy/fatty foods", "Sleep propped up"]
                }
                
                tips = symptom_tips.get(symptom, ["Rest and hydrate", "Monitor symptoms", "Contact doctor if worsens"])
                for tip in tips[:2]:
                    st.markdown(f"  • {tip}")
                st.markdown("")
        else:
            st.markdown("#### 🌟 Keep up the good work!")
            st.markdown("No recent symptoms logged. Continue monitoring how you feel.")
        
        trimester_symptom_tips = {
            1: ["Focus on managing nausea", "Rest often for fatigue", "Eat small frequent meals"],
            2: ["Manage back pain with good posture", "Stay active to boost energy", "Practice pelvic exercises"],
            3: ["Elevate feet to reduce swelling", "Practice breathing exercises", "Rest frequently"]
        }
        
        if trimester in trimester_symptom_tips:
            st.markdown(f"#### 📅 Trimester {trimester} Tips:")
            for tip in trimester_symptom_tips[trimester]:
                st.markdown(f"• {tip}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="card-modern">', unsafe_allow_html=True)
        st.markdown('<div class="card-header-modern"><span class="card-icon-modern">🍎</span><h3 class="card-title-modern">Nutrition Guidance</h3></div>', unsafe_allow_html=True)
        
        week_nutrition = {
            1: ["Start prenatal vitamins", "Focus on folate-rich foods"],
            12: ["Increase protein intake", "Focus on iron-rich foods"],
            20: ["Add Omega-3 foods", "Boost calcium intake"],
            28: ["Increase fiber", "Stay well-hydrated"],
            36: ["Small frequent meals", "Nutrient-dense foods"]
        }
        
        st.markdown(f"#### 🗓️ Week {week} Nutrition Focus:")
        if week in week_nutrition:
            for tip in week_nutrition[week]:
                st.markdown(f"• {tip}")
        else:
            st.markdown("• Eat balanced meals with protein, carbs, and healthy fats")
            st.markdown("• Stay hydrated with 8-10 glasses of water")
            st.markdown("• Include colorful fruits and vegetables")
        
        trimester_nutrition_focus = {
            1: ["Focus on folate for neural tube development", "Small meals for nausea"],
            2: ["Increase calories by 300-350/day", "Focus on protein and calcium"],
            3: ["Small, frequent meals", "Focus on iron and fiber"]
        }
        
        if trimester in trimester_nutrition_focus:
            st.markdown(f"#### 🤰 Trimester {trimester} Focus:")
            for focus in trimester_nutrition_focus[trimester]:
                st.markdown(f"• {focus}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab4:
        st.markdown('<div class="card-modern">', unsafe_allow_html=True)
        st.markdown('<div class="card-header-modern"><span class="card-icon-modern">💪</span><h3 class="card-title-modern">Exercise Suggestions</h3></div>', unsafe_allow_html=True)
        
        safe_exercises = {
            1: ["Walking 30 minutes daily", "Prenatal yoga", "Swimming", "Gentle stretching"],
            2: ["Continue walking", "Modified strength training", "Prenatal Pilates", "Stationary biking"],
            3: ["Shorter, more frequent walks", "Pelvic exercises", "Birth ball exercises", "Gentle stretching"]
        }
        
        st.markdown(f"#### 🏃‍♀️ Safe Exercises for Trimester {trimester}:")
        if trimester in safe_exercises:
            for exercise in safe_exercises[trimester]:
                st.markdown(f"• {exercise}")
        
        st.markdown("#### 🌟 Exercise Benefits:")
        benefits = [
            "Improves mood and energy levels",
            "Reduces pregnancy discomfort",
            "Prepares body for labor",
            "Promotes better sleep",
            "Helps maintain healthy weight"
        ]
        
        for benefit in benefits[:3]:
            st.markdown(f"• {benefit}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab5:
        st.markdown('<div class="card-modern">', unsafe_allow_html=True)
        st.markdown('<div class="card-header-modern"><span class="card-icon-modern">💊</span><h3 class="card-title-modern">Vitamin Guidance</h3></div>', unsafe_allow_html=True)
        
        st.markdown("#### 💊 Essential Daily Vitamins:")
        essentials = [
            "Prenatal multivitamin with folic acid",
            "Iron supplement (as needed)",
            "Calcium + Vitamin D",
            "Omega-3 DHA for brain development"
        ]
        
        for essential in essentials:
            st.markdown(f"• {essential}")
        
        st.markdown("#### ⏰ Best Practices:")
        timing_tips = [
            "Take vitamins with food to reduce nausea",
            "Take iron with Vitamin C for better absorption",
            "Space calcium and iron by 2-3 hours",
            "Take Omega-3 with meals containing fat"
        ]
        
        for tip in timing_tips:
            st.markdown(f"• {tip}")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# PROFILE SETTINGS TAB
# ============================================
def show_profile_settings_tab(user_id):
    st.markdown("""
    <div class="fade-in">
        <h2 style="color: var(--dark); margin-bottom: 1.5rem;">⚙️ Profile & Settings</h2>
    </div>
    """, unsafe_allow_html=True)
    
    c.execute("SELECT * FROM profile_settings WHERE user_id = ?", (user_id,))
    settings = c.fetchone()
    
    user_data = get_user_data(user_id)
    
    tab1, tab2, tab3, tab4 = st.tabs(["👤 Profile", "🔔 Notifications", "🔒 Privacy", "⚡ Advanced"])
    
    with tab1:
        st.markdown('<div class="card-modern">', unsafe_allow_html=True)
        st.markdown('<div class="card-header-modern"><span class="card-icon-modern">👤</span><h3 class="card-title-modern">Personal Information</h3></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            new_username = st.text_input("Username", value=user_data[1], disabled=True)
            new_email = st.text_input("Email Address", value=user_data[3])
        
        with col2:
            new_baby_name = st.text_input("Baby's Name", value=user_data[7] or "Our Little One")
            phone = st.text_input("Phone Number", placeholder="+1 (555) 123-4567")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="card-modern">', unsafe_allow_html=True)
        st.markdown('<div class="card-header-modern"><span class="card-icon-modern">🤰</span><h3 class="card-title-modern">Pregnancy Information</h3></div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            current_week = st.number_input("Current Week", min_value=1, max_value=42, 
                                          value=user_data[6], key="settings_week")
        
        with col2:
            trimester_options = {1: "First Trimester (1-13 weeks)", 
                               2: "Second Trimester (14-27 weeks)", 
                               3: "Third Trimester (28-40 weeks)"}
            selected_trimester = st.selectbox(
                "Trimester",
                options=list(trimester_options.keys()),
                format_func=lambda x: trimester_options[x],
                index=user_data[5]-1,
                key="settings_trimester"
            )
        
        with col3:
            due_date = st.date_input(
                "Expected Due Date",
                value=datetime.datetime.strptime(user_data[8], "%Y-%m-%d").date() if user_data[8] else datetime.date.today() + datetime.timedelta(weeks=40),
                key="settings_due_date"
            )
        
        auto_update = st.checkbox(
            "🔄 Automatically advance pregnancy week each week",
            value=settings[5] if settings else True,
            help="System will automatically update your pregnancy week each Monday"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="card-modern">', unsafe_allow_html=True)
        st.markdown('<div class="card-header-modern"><span class="card-icon-modern">🔔</span><h3 class="card-title-modern">Notification Preferences</h3></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            email_notifications = st.checkbox("📧 Email Notifications", value=settings[1] if settings else True)
            weekly_updates = st.checkbox("📅 Weekly Progress Updates", value=settings[2] if settings else True)
        
        with col2:
            baby_kick_reminders = st.checkbox("👣 Baby Kick Reminders", value=True)
            appointment_reminders = st.checkbox("📋 Appointment Reminders", value=True)
        
        notification_time = st.select_slider(
            "⏰ Daily Reminder Time",
            options=["8:00 AM", "12:00 PM", "4:00 PM", "8:00 PM"],
            value="8:00 PM"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="card-modern">', unsafe_allow_html=True)
        st.markdown('<div class="card-header-modern"><span class="card-icon-modern">🔒</span><h3 class="card-title-modern">Privacy & Security</h3></div>', unsafe_allow_html=True)
        
        privacy_level = st.selectbox(
            "Privacy Level",
            options=[
                ("1", "Private (Only you can see your data)"),
                ("2", "Shared (Share with healthcare provider)"),
                ("3", "Anonymous (Share anonymized data for research)")
            ],
            format_func=lambda x: x[1],
            index=settings[3]-1 if settings else 0
        )
        
        col1, col2 = st.columns(2)
        with col1:
            data_retention = st.selectbox(
                "Data Retention Period",
                ["6 months", "1 year", "3 years", "Indefinitely"],
                index=2
            )
        
        with col2:
            data_export = st.checkbox("Allow data export", value=True)
        
        st.markdown("---")
        st.markdown("#### 🔑 Change Password")
        
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_new_password = st.text_input("Confirm New Password", type="password")
        
        if new_password:
            is_valid, message = validate_password_strength(new_password)
            if is_valid:
                st.success("✅ Password meets requirements")
            else:
                st.error(f"❌ {message}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab4:
        st.markdown('<div class="card-modern">', unsafe_allow_html=True)
        st.markdown('<div class="card-header-modern"><span class="card-icon-modern">⚡</span><h3 class="card-title-modern">Advanced Settings</h3></div>', unsafe_allow_html=True)
        
        theme = st.selectbox(
            "Theme",
            ["Light", "Dark", "Auto"],
            index=0
        )
        
        col1, col2 = st.columns(2)
        with col1:
            analytics_optin = st.checkbox("Share usage analytics", value=True)
            auto_backup = st.checkbox("Automatic backup", value=True)
        
        with col2:
            high_contrast = st.checkbox("High contrast mode", value=False)
            reduced_motion = st.checkbox("Reduce animations", value=False)
        
        st.markdown("---")
        st.markdown("#### 🗄️ Data Management")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Export All Data", use_container_width=True):
                st.info("Data export initiated. You will receive an email.")
        
        with col2:
            if st.button("Clear Cache", use_container_width=True):
                st.success("Cache cleared successfully")
        
        with col3:
            if st.button("Reset Settings", use_container_width=True):
                st.warning("This will reset all settings to defaults")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    col1, col2 = st.columns([4, 1])
    with col1:
        if st.button("💾 Save All Changes", use_container_width=True, type="primary"):
            if settings:
                c.execute("""UPDATE profile_settings SET 
                            notifications_enabled = ?, weekly_updates = ?, 
                            privacy_level = ?, theme = ?, auto_week_update = ?
                            WHERE user_id = ?""",
                         (email_notifications, weekly_updates, 
                          int(privacy_level[0]), theme.lower(), auto_update, user_id))
            else:
                c.execute("""INSERT INTO profile_settings 
                            (user_id, notifications_enabled, weekly_updates, 
                             privacy_level, theme, auto_week_update) 
                            VALUES (?, ?, ?, ?, ?, ?)""",
                         (user_id, email_notifications, weekly_updates, 
                          int(privacy_level[0]), theme.lower(), auto_update))
            
            c.execute("""UPDATE users SET 
                        email = ?, baby_name = ?, trimester = ?, 
                        weeks_pregnant = ?, due_date = ?
                        WHERE id = ?""",
                     (new_email, new_baby_name, selected_trimester, 
                      current_week, str(due_date), user_id))
            
            if current_password and new_password and confirm_new_password:
                if verify_password(current_password, user_data[2], user_data[4]):
                    if new_password == confirm_new_password:
                        new_hash, new_salt = hash_password(new_password)
                        c.execute("UPDATE users SET password_hash = ?, salt = ? WHERE id = ?",
                                 (new_hash, new_salt, user_id))
                        st.success("✅ Password updated successfully")
                    else:
                        st.error("New passwords do not match")
                else:
                    st.error("Current password is incorrect")
            
            conn.commit()
            
            st.session_state.user["email"] = new_email
            st.session_state.user["baby_name"] = new_baby_name
            st.session_state.user["trimester"] = selected_trimester
            st.session_state.user["weeks_pregnant"] = current_week
            st.session_state.trimester = selected_trimester
            st.session_state.pregnancy_week = current_week
            
            st.success("✅ Settings saved successfully!")
            st.rerun()
    
    with col2:
        if st.button("🔄 Discard Changes", use_container_width=True, type="secondary"):
            st.rerun()

# ============================================
# REPORTS TAB
# ============================================
def show_reports_tab(user_id):
    st.markdown("""
    <div class="fade-in">
        <h2 style="color: var(--dark); margin-bottom: 1.5rem;">📄 Reports & Data Export</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="card-modern">', unsafe_allow_html=True)
        st.markdown('<div class="card-header-modern"><span class="card-icon-modern">📊</span><h3 class="card-title-modern">Generate Wellness Report</h3></div>', unsafe_allow_html=True)
        
        report_type = st.selectbox(
            "Report Type:",
            ["Weekly Summary", "Monthly Overview", "Trimester Progress", "Complete History"]
        )
        
        if st.button("📋 Generate PDF Report", use_container_width=True):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            
            pdf.cell(200, 10, txt="MaternalMind AI - Pregnancy Wellness Report", ln=1, align='C')
            pdf.cell(200, 10, txt=f"For: {st.session_state.user['username']}", ln=1)
            pdf.cell(200, 10, txt=f"Date: {datetime.date.today()}", ln=1)
            pdf.cell(200, 10, txt=f"Baby: {st.session_state.user['baby_name']} - Week {st.session_state.pregnancy_week}, Trimester {st.session_state.trimester}", ln=1)
            pdf.ln(10)
            
            if report_type != "Complete History":
                days = 7 if report_type == "Weekly Summary" else 30 if report_type == "Monthly Overview" else 90
                
                pdf.cell(200, 10, txt="Recent Emotions:", ln=1)
                emotions = get_emotion_history(user_id, days)
                for _, row in emotions.iterrows():
                    pdf.cell(200, 10, txt=f"{row['date']}: {row['emotion']} ({row['confidence']:.0%})", ln=1)
                
                pdf.ln(5)
                
                pdf.cell(200, 10, txt="Symptom Summary:", ln=1)
                symptoms = get_symptoms_history(user_id, days)
                if not symptoms.empty:
                    symptom_count = len(symptoms)
                    pdf.cell(200, 10, txt=f"Total Symptoms: {symptom_count}", ln=1)
                
                pdf.ln(5)
                
                pdf.cell(200, 10, txt="Nutrition Summary:", ln=1)
                nutrition = get_nutrition_history(user_id, days)
                if not nutrition.empty:
                    total_calories = nutrition['calories'].sum()
                    pdf.cell(200, 10, txt=f"Total Calories: {total_calories}", ln=1)
            
            pdf_bytes = pdf.output(dest='S').encode('latin1')
            
            st.download_button(
                label="⬇️ Download PDF Report",
                data=pdf_bytes,
                file_name=f"wellness_report_{datetime.date.today()}.pdf",
                mime="application/pdf"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card-modern">', unsafe_allow_html=True)
        st.markdown('<div class="card-header-modern"><span class="card-icon-modern">💾</span><h3 class="card-title-modern">Export Data</h3></div>', unsafe_allow_html=True)
        
        export_format = st.selectbox(
            "Format:",
            ["JSON", "CSV"],
            key="export_format"
        )
        
        if st.button("📤 Export All Data", use_container_width=True):
            export_data = {
                'user_info': st.session_state.user,
                'emotions': get_emotion_history(user_id, 365).to_dict('records'),
                'symptoms': get_symptoms_history(user_id, 365).to_dict('records'),
                'baby_kicks': get_baby_kicks_history(user_id, 365).to_dict('records'),
                'nutrition': get_nutrition_history(user_id, 365).to_dict('records'),
                'exercise': get_exercise_history(user_id, 365).to_dict('records'),
                'vitamins': get_vitamin_history(user_id, 365).to_dict('records'),
                'export_date': datetime.datetime.now().isoformat()
            }
            
            if export_format == "JSON":
                export_json = json.dumps(export_data, indent=2, default=str)
                
                st.download_button(
                    label="⬇️ Download JSON",
                    data=export_json,
                    file_name=f"pregnancy_data_{datetime.date.today()}.json",
                    mime="application/json"
                )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📊 Your Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_emotions = len(get_emotion_history(user_id, 365))
        st.metric("Total Emotions", total_emotions)
    
    with col2:
        total_symptoms = len(get_symptoms_history(user_id, 365))
        st.metric("Symptoms Logged", total_symptoms)
    
    with col3:
        total_kicks = get_baby_kicks_history(user_id, 365)['kicks'].sum() if not get_baby_kicks_history(user_id, 365).empty else 0
        st.metric("Total Kicks", total_kicks)
    
    with col4:
        total_meals = len(get_nutrition_history(user_id, 365))
        st.metric("Meals Logged", total_meals)

# ============================================
# MAIN APP
# ============================================
def show_main_app():
    if not st.session_state.login:
        st.session_state.page = "login"
        st.rerun()
    
    user_id = st.session_state.user["id"]
    
    create_modern_sidebar()
    
    st.markdown('<div class="modern-container">', unsafe_allow_html=True)
    
    if st.session_state.current_tab == "dashboard":
        show_dashboard_tab(user_id)
    elif st.session_state.current_tab == "symptoms":
        show_symptoms_tab(user_id)
    elif st.session_state.current_tab == "voice":
        show_voice_tab(user_id)
    elif st.session_state.current_tab == "text":
        show_text_analysis_tab(user_id)
    elif st.session_state.current_tab == "baby":
        show_baby_tracker_tab(user_id)
    elif st.session_state.current_tab == "nutrition":
        show_nutrition_tab(user_id)
    elif st.session_state.current_tab == "exercise":
        show_exercise_tab(user_id)
    elif st.session_state.current_tab == "vitamins":
        show_vitamins_tab(user_id)
    elif st.session_state.current_tab == "recommendations":
        show_recommendations_tab(user_id)
    elif st.session_state.current_tab == "settings":
        show_profile_settings_tab(user_id)
    elif st.session_state.current_tab == "reports":
        show_reports_tab(user_id)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    footer_col1, footer_col2, footer_col3 = st.columns(3)
    
    with footer_col1:
        st.caption("🤰 MaternalMind AI")
        st.caption("Version 1.0.0")
    
    with footer_col2:
        st.caption("💖 AI-Powered Pregnancy Wellness")
        st.caption("Not a substitute for medical care")
    
    with footer_col3:
        st.caption("🔒 Your data is stored locally")
        st.caption("Built with Streamlit & SQLite")

# ============================================
# MAIN APP ROUTING
# ============================================
def main():
    # Show loading screen on initial load
    if 'initial_load' not in st.session_state:
        st.session_state.initial_load = True
        show_loading_screen()
    
    if st.session_state.page == "login":
        show_modern_login()
    elif st.session_state.page == "signup":
        show_modern_signup()
    elif st.session_state.page == "main":
        show_main_app()
    else:
        st.session_state.page = "login"
        show_modern_login()

# ============================================
# RUN THE APP
# ============================================
if __name__ == "__main__":
    main()
    
    conn.close()