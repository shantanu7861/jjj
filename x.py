import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import pandas as pd
import json
import time
import secrets
import string
import os
from google.oauth2.service_account import Credentials
import base64

# Page configuration
st.set_page_config(
    page_title="VOLAR FASHION - Leave Management",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS that works for both light and dark themes
st.markdown("""
    <style>
    /* Base styles that work in both themes */
    :root {
        --primary-color: #673ab7;
        --secondary-color: #9c27b0;
        --accent-color: #2196f3;
        --success-color: #4caf50;
        --warning-color: #ff9800;
        --danger-color: #dc3545;
        --text-primary: #1a1a1a;
        --text-secondary: #666666;
        --bg-primary: #ffffff;
        --bg-secondary: #f8f9ff;
        --bg-tertiary: #f5f7fa;
        --border-color: #e2e8f0;
    }
    
    @media (prefers-color-scheme: dark) {
        :root {
            --text-primary: #ffffff;
            --text-secondary: #cccccc;
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-tertiary: #334155;
            --border-color: #475569;
        }
    }
    
    /* Override Streamlit's theme variables */
    .stApp {
        background-color: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
    }
    
    * {
        font-family: 'Inter', sans-serif;
        color: var(--text-primary);
    }
    
    .main {
        background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
        min-height: 100vh;
    }
    
    .form-container {
        background: var(--bg-primary);
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(103, 58, 183, 0.1);
        margin: 2rem auto;
        max-width: 1000px;
        border: 1px solid var(--border-color);
        position: relative;
        overflow: hidden;
    }
    
    .form-container:before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #673ab7, #9c27b0, #2196f3);
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary) !important;
    }
    
    h1 {
        background: linear-gradient(135deg, #673ab7 0%, #2196f3 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 2.8rem;
        margin-bottom: 0.5rem;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    h2 {
        color: var(--text-secondary) !important;
        text-align: center;
        font-size: 1.4rem;
        margin-bottom: 2rem;
        font-weight: 400;
        opacity: 0.9;
    }
    
    h3 {
        color: var(--text-primary) !important;
        font-size: 1.3rem;
        margin-top: 2rem;
        margin-bottom: 1.2rem;
        font-weight: 600;
        position: relative;
        padding-bottom: 10px;
    }
    
    h3:after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 60px;
        height: 3px;
        background: linear-gradient(90deg, #673ab7, #9c27b0);
        border-radius: 2px;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #673ab7 0%, #9c27b0 100%);
        color: white !important;
        border: none;
        padding: 1rem 3rem;
        font-size: 1.1rem;
        border-radius: 12px;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 8px 25px rgba(103, 58, 183, 0.25);
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 35px rgba(103, 58, 183, 0.35);
    }
    
    /* Input fields styling that works in both themes */
    .stTextInput>div>div>input, 
    .stSelectbox>div>div>select, 
    .stTextArea>div>div>textarea, 
    .stDateInput>div>div>input {
        border-radius: 12px;
        border: 2px solid var(--border-color);
        padding: 0.875rem 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
        background: var(--bg-primary);
        color: var(--text-primary) !important;
    }
    
    .stTextInput>div>div>input:focus, 
    .stSelectbox>div>div>select:focus, 
    .stTextArea>div>div>textarea:focus, 
    .stDateInput>div>div>input:focus {
        border-color: #673ab7;
        box-shadow: 0 0 0 4px rgba(103, 58, 183, 0.1);
        background: var(--bg-primary);
        outline: none;
    }
    
    /* Labels */
    label {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Success, Error, Info boxes */
    .success-message {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-left: 4px solid #28a745;
        color: #155724 !important;
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        font-weight: 500;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(40, 167, 69, 0.1);
        animation: slideIn 0.5s ease-out;
    }
    
    .error-message {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border-left: 4px solid #dc3545;
        color: #721c24 !important;
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        font-weight: 500;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(220, 53, 69, 0.1);
        animation: shake 0.5s ease;
    }
    
    .info-box {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-left: 4px solid #2196f3;
        color: #0d47a1 !important;
        padding: 1.5rem;
        border-radius: 16px;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(33, 150, 243, 0.1);
    }
    
    .thumbsup-box {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        border-left: 4px solid #4caf50;
        color: #2e7d32 !important;
        padding: 1.5rem;
        border-radius: 16px;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(76, 175, 80, 0.1);
        text-align: center;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: var(--bg-primary);
        padding: 8px;
        border-radius: 16px;
        border: 1px solid var(--border-color);
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: var(--bg-primary);
        border-radius: 12px;
        color: var(--text-secondary);
        font-weight: 500;
        padding: 12px 28px;
        border: 1px solid var(--border-color);
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #673ab7 0%, #9c27b0 100%);
        color: white !important;
        border-color: #673ab7;
        box-shadow: 0 4px 12px rgba(103, 58, 183, 0.2);
    }
    
    /* Company Header */
    .company-header {
        text-align: center;
        margin-bottom: 2rem;
        padding: 2rem;
        background: var(--bg-primary);
        border-radius: 24px;
        box-shadow: 0 15px 40px rgba(103, 58, 183, 0.08);
        border: 1px solid var(--border-color);
        position: relative;
        overflow: hidden;
    }
    
    /* Metric Card */
    .metric-card {
        background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(156, 39, 176, 0.1);
        border: 1px solid rgba(156, 39, 176, 0.1);
    }
    
    /* Approval Card */
    .approval-card {
        background: var(--bg-primary);
        padding: 1.5rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        margin: 1rem 0;
        border: 1px solid var(--border-color);
    }
    
    /* Status badges */
    .status-pending {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        color: #856404 !important;
        padding: 0.5rem 1.25rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 600;
        border: 1px solid rgba(255, 193, 7, 0.3);
    }
    
    .status-approved {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        color: #155724 !important;
        padding: 0.5rem 1.25rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 600;
        border: 1px solid rgba(40, 167, 69, 0.3);
    }
    
    .status-rejected {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        color: #721c24 !important;
        padding: 0.5rem 1.25rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 600;
        border: 1px solid rgba(220, 53, 69, 0.3);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: var(--text-secondary) !important;
        padding: 3rem 2rem;
        margin-top: 4rem;
        position: relative;
    }
    
    .footer:before {
        content: '';
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 200px;
        height: 2px;
        background: linear-gradient(90deg, transparent, #673ab7, transparent);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Animations */
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    .floating-element {
        animation: float 6s ease-in-out infinite;
    }
    
    /* Icon Badge */
    .icon-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 40px;
        height: 40px;
        border-radius: 12px;
        background: linear-gradient(135deg, #673ab7 0%, #9c27b0 100%);
        color: white !important;
        margin-right: 12px;
        font-size: 1.2rem;
    }
    
    /* Section Header */
    .section-header {
        display: flex;
        align-items: center;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid var(--border-color);
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-tertiary);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #673ab7 0%, #9c27b0 100%);
        border-radius: 4px;
    }
    
    /* Ensure text in input fields is visible in dark mode */
    input, select, textarea {
        color: var(--text-primary) !important;
    }
    
    /* Override Streamlit's default text colors */
    .st-emotion-cache-1qg05tj, 
    .st-emotion-cache-1v0mbdj, 
    .st-emotion-cache-16idsys, 
    .st-emotion-cache-1y4p8pa {
        color: var(--text-primary) !important;
    }
    
    /* Fix for selectbox options visibility */
    .stSelectbox [role="listbox"] {
        background-color: var(--bg-primary) !important;
        color: var(--text-primary) !important;
    }
    
    .stSelectbox [role="option"] {
        color: var(--text-primary) !important;
        background-color: var(--bg-primary) !important;
    }
    
    .stSelectbox [role="option"]:hover {
        background-color: var(--bg-secondary) !important;
    }
    
    /* Fix for date picker */
    .stDateInput [data-baseweb="calendar"] {
        background-color: var(--bg-primary) !important;
        color: var(--text-primary) !important;
    }
    
    /* Add background to all Streamlit elements */
    .stTextInput, .stSelectbox, .stTextArea, .stDateInput {
        background-color: var(--bg-primary) !important;
    }
    </style>
""", unsafe_allow_html=True)

# Superior details dictionary
SUPERIORS = {
    "Shantanu": "s37@vfemails.com",
    "Demo": "Shinde78617@gmail.com",
    "Ayushi": "ayushi@volarfashion.in",
    "Sandip Sir": "sandip@ragunited.com",
    "Akshaya": "Akshaya@vfemails.com",
    "Vitika": "vitika@vfemails.com",
    "MANISH": "Manish@vfemails.com",
    "TAHIR": "tahir@vfemails.com",
    "Tariq": "dn1@volarfashion.in",
    "HR": "hrvolarfashion@gmail.com",
    "Rajeev": "Rajeev@vfemails.com",
    "Krishna": "Krishna@vfemails.com",
    "Sarath": "Sarath@vfemails.com"
}

# Google Sheets configuration
SHEET_NAME = "Leave_Applications"
SCOPES = ['https://spreadsheets.google.com/feeds', 
          'https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/spreadsheets']

# Department options
DEPARTMENTS = [
    "Human Resources",
    "Finance",
    "Ecom",
    "Graphic Design",
    "Sales and Marketing",
    "Quality Control",
    "IT",
    "Administration"
]

def get_secrets():
    """Get credentials from Streamlit secrets or environment variables"""
    try:
        # Try Streamlit secrets first
        if 'GOOGLE_CREDENTIALS' in st.secrets:
            creds_dict = dict(st.secrets['GOOGLE_CREDENTIALS'])
        elif 'google_credentials' in st.secrets:
            creds_dict = dict(st.secrets['google_credentials'])
        else:
            # Fallback to environment variables (for local development)
            import json
            creds_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
            if creds_json:
                creds_dict = json.loads(creds_json)
            else:
                st.error("Google credentials not found in secrets or environment variables")
                return None
        
        # Ensure private key is properly formatted
        if 'private_key' in creds_dict:
            creds_dict['private_key'] = creds_dict['private_key'].replace('\\n', '\n')
        
        return creds_dict
        
    except Exception as e:
        st.error(f"Error loading credentials: {str(e)}")
        return None

def setup_google_sheets():
    """Setup Google Sheets connection"""
    try:
        creds_dict = get_secrets()
        if not creds_dict:
            return None
        
        # Create credentials
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPES)
        client = gspread.authorize(creds)
        
        # Try to open the sheet
        try:
            sheet = client.open(SHEET_NAME).sheet1
        except gspread.SpreadsheetNotFound:
            # Try to find by URL if sheet name doesn't work
            sheet_url = st.secrets.get("SHEET_URL", "") if hasattr(st.secrets, 'get') else ""
            if sheet_url:
                sheet = client.open_by_url(sheet_url).sheet1
            else:
                st.error(f"❌ Google Sheet '{SHEET_NAME}' not found!")
                st.info(f"Please check if the sheet name is correct or provide SHEET_URL in secrets")
                return None
        
        # Initialize headers if sheet is empty
        if sheet.row_count == 0 or not sheet.row_values(1):
            headers = [
                "Submission Date", "Employee Name", "Employee Code", "Department",
                "Type of Leave", "No of Days", "Purpose of Leave", "From Date",
                "Till Date", "Superior Name", "Superior Email", "Status", 
                "Approval Date", "Approval Password"
            ]
            sheet.append_row(headers)
        
        return sheet
        
    except Exception as e:
        st.error(f"❌ Error connecting to Google Sheets: {str(e)}")
        return None

def generate_approval_password():
    """Generate a 5-digit alphanumeric password"""
    alphabet = string.ascii_uppercase + string.digits
    # Remove confusing characters (0, O, 1, I, L)
    alphabet = alphabet.replace('0', '').replace('O', '').replace('1', '').replace('I', '').replace('L', '')
    return ''.join(secrets.choice(alphabet) for _ in range(5))

def calculate_days(from_date, till_date, leave_type):
    """Calculate number of days"""
    if leave_type == "Half Day":
        return 0.5
    elif leave_type == "Early Exit":
        return "N/A"
    else:
        delta = till_date - from_date
        return delta.days + 1

def get_email_credentials():
    """Get email credentials from Streamlit secrets"""
    try:
        if hasattr(st.secrets, 'get'):
            sender_email = st.secrets.get("SENDER_EMAIL", "hrvolarfashion@gmail.com")
            sender_password = st.secrets.get("SENDER_PASSWORD", "")
        else:
            # For local development
            sender_email = os.getenv("SENDER_EMAIL", "hrvolarfashion@gmail.com")
            sender_password = os.getenv("SENDER_PASSWORD", "")
        
        return sender_email, sender_password
    except:
        return "hrvolarfashion@gmail.com", ""

def send_approval_email(employee_name, superior_name, superior_email, leave_details, approval_password):
    """Send approval request email to superior"""
    try:
        sender_email, sender_password = get_email_credentials()
        
        if not sender_password:
            st.warning("⚠️ Email password not configured. Skipping email notification.")
            return False
            
        if "@" not in superior_email or "." not in superior_email:
            st.warning(f"⚠️ Invalid email format for {superior_name}: {superior_email}")
            return False
            
        msg = MIMEMultipart('alternative')
        msg['From'] = f"VOLAR FASHION HR <{sender_email}>"
        msg['To'] = superior_email
        msg['Subject'] = f"Leave Approval Required: {employee_name}"
        
        # Simple HTML email
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #673ab7;">Leave Approval Required</h2>
                <p>Dear {superior_name},</p>
                
                <p>An employee has submitted a leave request that requires your approval.</p>
                
                <div style="background: #f8f9ff; padding: 20px; border-radius: 10px; margin: 20px 0;">
                    <h3 style="color: #333; margin-top: 0;">Request Details:</h3>
                    <p><strong>Employee:</strong> {leave_details['employee_name']}</p>
                    <p><strong>Employee Code:</strong> {leave_details['employee_code']}</p>
                    <p><strong>Department:</strong> {leave_details['department']}</p>
                    <p><strong>Leave Type:</strong> {leave_details['leave_type']}</p>
                    <p><strong>Dates:</strong> {leave_details['from_date']} to {leave_details['till_date']}</p>
                    <p><strong>Purpose:</strong> {leave_details['purpose']}</p>
                </div>
                
                <div style="background: #e8f5e9; padding: 20px; border-radius: 10px; margin: 20px 0;">
                    <h3 style="color: #2e7d32; margin-top: 0;">Approval Code:</h3>
                    <div style="font-size: 24px; font-weight: bold; color: #673ab7; letter-spacing: 3px; 
                         font-family: monospace; text-align: center; padding: 10px;">
                        {approval_password}
                    </div>
                    <p>Use this code in the approval portal along with your email address.</p>
                </div>
                
                <p>To approve or reject this request, please visit the approval portal.</p>
                
                <p>Best regards,<br>
                VOLAR FASHION HR Team</p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, 'html'))
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        return True
        
    except Exception as e:
        st.error(f"❌ Email sending error: {str(e)}")
        return False

def update_leave_status(sheet, superior_email, approval_password, status):
    """Update leave status in Google Sheet"""
    try:
        all_records = sheet.get_all_values()
        
        for idx, row in enumerate(all_records):
            if idx == 0:  # Skip header
                continue
            
            if len(row) > 13 and row[10] == superior_email and row[13] == approval_password:
                sheet.update_cell(idx + 1, 12, status)  # Status column
                sheet.update_cell(idx + 1, 13, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))  # Approval Date
                sheet.update_cell(idx + 1, 14, "USED")  # Mark password as used
                return True
        
        return False
    except Exception as e:
        st.error(f"Error updating status: {str(e)}")
        return False

# Main Application UI
st.markdown("""
    <div class="company-header">
        <h1>VOLAR FASHION</h1>
        <h2>Leave Management System</h2>
    </div>
""", unsafe_allow_html=True)

# Create tabs
tab1, tab2 = st.tabs(["📝 Submit Leave Application", "✅ Approval Portal"])

with tab1:
    st.markdown("""
        <div class="section-header">
            <div class="icon-badge">📋</div>
            <div>
                <h3 style="margin: 0;">Leave Application Form</h3>
                <p style="margin: 5px 0 0 0; color: var(--text-secondary); font-size: 0.95rem;">
                    Complete all fields below to submit your leave request
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Two-column layout
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        employee_name = st.text_input(
            "👤 Full Name",
            placeholder="Enter your full name"
        )
        employee_code = st.text_input(
            "🔢 Employee ID",
            placeholder="e.g., VF-EMP-001"
        )
        department = st.selectbox(
            "🏛️ Department",
            ["Select Department"] + DEPARTMENTS
        )
    
    with col2:
        leave_type = st.selectbox(
            "📋 Leave Type",
            ["Select Type", "Full Day", "Half Day", "Early Exit"]
        )
        from_date = st.date_input(
            "📅 Start Date",
            min_value=datetime.now().date()
        )
        till_date = st.date_input(
            "📅 End Date",
            min_value=datetime.now().date()
        )
    
    # Calculate days if valid inputs
    if leave_type != "Select Type" and from_date and till_date:
        no_of_days = calculate_days(from_date, till_date, leave_type)
        
        if leave_type != "Early Exit":
            st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 0.9rem; color: #6b46c1; font-weight: 500;">Leave Duration</div>
                    <div style="font-size: 2rem; font-weight: 700; color: #553c9a; margin: 10px 0;">
                        {no_of_days}
                    </div>
                    <div style="font-size: 0.9rem; color: #805ad5;">days requested</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="thumbsup-box">
                    <div style="font-size: 2rem; margin-bottom: 1rem;">👍</div>
                    <div style="font-size: 1.1rem; font-weight: 600; margin-bottom: 8px;">Early Exit Request</div>
                    <div style="font-size: 0.95rem;">
                        You're requesting to leave early from work today.
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    # Purpose Section
    purpose = st.text_area(
        "Purpose of Leave",
        placeholder="Please provide a clear and detailed explanation for your leave request...",
        height=100
    )
    
    # Manager Selection
    superior_name = st.selectbox(
        "👔 Reporting Manager",
        ["Select Manager"] + list(SUPERIORS.keys())
    )
    
    # Information Box
    st.markdown("""
        <div class="info-box">
            <div style="display: flex; align-items: flex-start;">
                <div style="font-size: 1.5rem; margin-right: 15px;">ℹ️</div>
                <div>
                    <strong style="display: block; margin-bottom: 8px;">Important Guidelines</strong>
                    • All fields are required for submission<br>
                    • Your manager will receive an approval code via email<br>
                    • Approval decisions are typically made within 24 hours<br>
                    • You'll be notified once a decision is made
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Submit Button
    if st.button("🚀 Submit Leave Request", type="primary", use_container_width=True):
        # Validation
        if not all([employee_name, employee_code, department != "Select Department", 
                    leave_type != "Select Type", purpose, superior_name != "Select Manager"]):
            st.markdown('''
                <div class="error-message">
                    <div style="display: flex; align-items: center; justify-content: center;">
                        <div style="font-size: 1.5rem; margin-right: 10px;">⚠️</div>
                        <div>
                            <strong>Please complete all required fields</strong>
                        </div>
                    </div>
                </div>
            ''', unsafe_allow_html=True)
        elif from_date > till_date:
            st.markdown('''
                <div class="error-message">
                    <div style="display: flex; align-items: center; justify-content: center;">
                        <div style="font-size: 1.5rem; margin-right: 10px;">📅</div>
                        <div>
                            <strong>Date Error</strong><br>
                            End date must be after or equal to start date
                        </div>
                    </div>
                </div>
            ''', unsafe_allow_html=True)
        else:
            # Show processing
            with st.spinner("Processing your request..."):
                # Prepare data
                submission_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                superior_email = SUPERIORS[superior_name]
                approval_password = generate_approval_password()
                
                # Calculate days
                no_of_days = calculate_days(from_date, till_date, leave_type)
                
                # Connect to Google Sheets
                sheet = setup_google_sheets()
                
                if sheet:
                    try:
                        # Prepare row data
                        row_data = [
                            submission_date,
                            employee_name,
                            employee_code,
                            department,
                            leave_type,
                            str(no_of_days),
                            purpose,
                            from_date.strftime("%Y-%m-%d"),
                            till_date.strftime("%Y-%m-%d"),
                            superior_name,
                            superior_email,
                            "Pending",
                            "",  # Approval Date
                            approval_password
                        ]
                        
                        # Write to Google Sheets
                        sheet.append_row(row_data)
                        
                        # Send email
                        leave_details = {
                            'employee_name': employee_name,
                            'employee_code': employee_code,
                            'department': department,
                            'leave_type': leave_type,
                            'no_of_days': no_of_days,
                            'purpose': purpose,
                            'from_date': from_date.strftime("%Y-%m-%d"),
                            'till_date': till_date.strftime("%Y-%m-%d")
                        }
                        
                        email_sent = send_approval_email(
                            employee_name,
                            superior_name,
                            superior_email,
                            leave_details,
                            approval_password
                        )
                        
                        if email_sent:
                            st.markdown('''
                                <div class="success-message">
                                    <div style="font-size: 2rem; margin-bottom: 1rem;">✨</div>
                                    <div style="font-size: 1.3rem; font-weight: 600; margin-bottom: 10px;">
                                        Application Submitted Successfully!
                                    </div>
                                    <div>
                                        Your leave request has been sent to your manager for approval.
                                    </div>
                                </div>
                            ''', unsafe_allow_html=True)
                            st.balloons()
                        else:
                            st.markdown(f'''
                                <div class="info-box">
                                    <div style="display: flex; align-items: center; justify-content: center;">
                                        <div style="font-size: 1.5rem; margin-right: 10px;">📧</div>
                                        <div>
                                            <strong>Application Saved but Email Failed</strong><br>
                                            Your application was saved to the database.<br>
                                            Please inform your manager about approval code: <strong>{approval_password}</strong>
                                        </div>
                                    </div>
                                </div>
                            ''', unsafe_allow_html=True)
                            
                    except Exception as e:
                        st.error(f"Error submitting application: {str(e)}")
                else:
                    st.error("Could not connect to database. Please try again later.")

with tab2:
    # Approval Portal
    st.markdown("""
        <div class="section-header">
            <div class="icon-badge" style="background: linear-gradient(135deg, #2196f3 0%, #03a9f4 100%);">✅</div>
            <div>
                <h3 style="margin: 0;">Manager Approval Portal</h3>
                <p style="margin: 5px 0 0 0; color: var(--text-secondary); font-size: 0.95rem;">
                    Approve or reject leave requests using your approval code
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Security Info
    st.markdown("""
        <div class="info-box">
            <div style="display: flex; align-items: center;">
                <div style="font-size: 1.5rem; margin-right: 15px;">🔒</div>
                <div>
                    <strong>Secure Authentication Required</strong><br>
                    Use the unique approval code sent to your email for authentication
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Form Fields
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        superior_email_input = st.text_input(
            "📧 Manager Email",
            placeholder="your.email@volarfashion.com"
        )
    
    with col2:
        approval_password_input = st.text_input(
            "🔑 Approval Code",
            type="password",
            placeholder="Enter 5-character code"
        )
    
    # Decision
    st.markdown("---")
    action = st.selectbox(
        "Select Decision",
        ["Select Decision", "✅ Approve", "❌ Reject"]
    )
    
    # Submit Decision
    if st.button("Submit Decision", type="primary", use_container_width=True):
        if not all([superior_email_input, approval_password_input, action != "Select Decision"]):
            st.error("Please complete all fields and select a decision")
        elif superior_email_input not in SUPERIORS.values():
            st.error("Unauthorized email address")
        elif len(approval_password_input) != 5:
            st.error("Invalid code format. Please enter the exact 5-character code")
        else:
            sheet = setup_google_sheets()
            if sheet:
                status = "Approved" if action == "✅ Approve" else "Rejected"
                success = update_leave_status(sheet, superior_email_input, approval_password_input, status)
                
                if success:
                    st.success(f"✅ Decision submitted successfully! The request has been {status.lower()}.")
                    st.balloons()
                else:
                    st.error("Authentication failed. Invalid code or code already used.")

# Footer
st.markdown("""
    <div class="footer">
        <div style="margin-bottom: 1rem;">
            <strong style="color: #673ab7;">VOLAR FASHION PVT LTD</strong><br>
            Human Resources Management System
        </div>
        <div style="font-size: 0.9rem;">
            📧 hrvolarfashion@gmail.com<br>
            © 2024 VOLAR FASHION.
        </div>
    </div>
""", unsafe_allow_html=True)
