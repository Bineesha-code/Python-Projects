"""
Streamlit frontend for Smart Resume Parser
"""
import streamlit as st
import requests
import json
import pandas as pd
from typing import Dict, Any
import time
import io

# Page configuration
st.set_page_config(
    page_title="Zumeparse",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .upload-section {
        background: #f8f9fa;
        border-radius: 10px;
        border: 2px dashed #dee2e6;
        text-align: center;
        margin: 2rem 0;
    }
    
    .results-section {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .skill-tag {
        display: inline-block;
        background: #e3f2fd;
        color: #1976d2;
        padding: 0.25rem 0.75rem;
        margin: 0.25rem;
        border-radius: 20px;
        font-size: 0.875rem;
    }
    
    .metric-card {
        color : black;
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        border-left: 4px solid #667eea;
    }
    
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
    
    .error-message {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://localhost:8000"

def main():
    """Main application function"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>Smart Resume Parser</h1>
        <p>Upload your resume and get structured insights powered by AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'parsed_data' not in st.session_state:
        st.session_state.parsed_data = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    
    # Upload section
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 📄 Upload Your Resume")
        st.markdown("Supported formats: PDF, DOCX | Max size: 10MB")
        
        uploaded_file = st.file_uploader(
            "Choose a resume file",
            type=['pdf', 'docx'],
            help="Upload your resume in PDF or DOCX format"
        )
        
        if uploaded_file is not None:
            if st.button("🚀 Parse Resume", type="primary", use_container_width=True):
                parse_resume(uploaded_file)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Results section
    if st.session_state.parsed_data:
        display_results(st.session_state.parsed_data)
    
   


def parse_resume(uploaded_file):
    """Parse uploaded resume file"""
    st.session_state.processing = True
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        status_text.text("📤 Uploading file...")
        progress_bar.progress(25)
        
        files = {
            "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
        }
        
        status_text.text("🔍 Processing resume...")
        progress_bar.progress(50)
        
        response = requests.post(f"{API_BASE_URL}/upload-resume", files=files)
        
        progress_bar.progress(75)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                st.session_state.parsed_data = result
                progress_bar.progress(100)
                status_text.markdown(
                    '<div class="success-message">✅ Resume parsed successfully!</div>',
                    unsafe_allow_html=True
                )
                time.sleep(1)
                status_text.empty()
                progress_bar.empty()
            else:
                show_error(result.get("message", "Unknown error occurred"))
        else:
            error_detail = response.json().get("detail", "Server error")
            show_error(f"Error: {error_detail}")
            
    except requests.exceptions.ConnectionError:
        show_error("❌ Cannot connect to the API server. Please make sure the backend is running on http://localhost:8000")
    except Exception as e:
        show_error(f"❌ An error occurred: {str(e)}")
    finally:
        st.session_state.processing = False
        progress_bar.empty()
        status_text.empty()


def show_error(message: str):
    """Display error message"""
    st.markdown(f'<div class="error-message">{message}</div>', unsafe_allow_html=True)


def display_results(result_data: Dict[str, Any]):
    """Display parsing results"""
    parsed_data = result_data.get("parsed_data", {})
    processing_time = result_data.get("processing_time", 0)
    
    st.markdown("## 📊 Parsing Results")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>⏱️</h3>
            <p><strong>{processing_time:.2f}s</strong></p>
            <p>Processing Time</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        skills_count = len(parsed_data.get("skills", {}).get("all_skills", []))
        st.markdown(f"""
        <div class="metric-card">
            <h3>🛠️</h3>
            <p><strong>{skills_count}</strong></p>
            <p>Skills Found</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        exp_count = len(parsed_data.get("experience", []))
        st.markdown(f"""
        <div class="metric-card">
            <h3>💼</h3>
            <p><strong>{exp_count}</strong></p>
            <p>Work Experience</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        edu_count = len(parsed_data.get("education", []))
        st.markdown(f"""
        <div class="metric-card">
            <h3>🎓</h3>
            <p><strong>{edu_count}</strong></p>
            <p>Education</p>
        </div>
        """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["👤 Contact", "🛠️ Skills", "💼 Experience", "🎓 Education", "📄 Raw Data"])
    
    with tab1:
        display_contact_info(parsed_data.get("contact_info", {}))
    
    with tab2:
        display_skills(parsed_data.get("skills", {}))
    
    with tab3:
        display_experience(parsed_data.get("experience", []))
    
    with tab4:
        display_education(parsed_data.get("education", []))
    
    with tab5:
        display_raw_data(parsed_data)


def display_contact_info(contact_info: Dict[str, Any]):
    st.markdown("### 📞 Contact Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if contact_info.get("name"):
            st.write(f"**Name:** {contact_info['name']}")
        if contact_info.get("email"):
            st.write(f"**Email:** {contact_info['email']}")
        if contact_info.get("phone"):
            st.write(f"**Phone:** {contact_info['phone']}")
    
    with col2:
        if contact_info.get("linkedin"):
            st.write(f"**LinkedIn:** [Profile]({contact_info['linkedin']})")
        if contact_info.get("github"):
            st.write(f"**GitHub:** [Profile]({contact_info['github']})")
        if contact_info.get("website"):
            st.write(f"**Website:** [Link]({contact_info['website']})")


def display_skills(skills: Dict[str, Any]):
    st.markdown("### 🛠️ Skills Analysis")
    
    skill_categories = [
        ("Programming Languages", "programming_languages", "💻"),
        ("Frameworks", "frameworks", "🔧"),
        ("Databases", "databases", "🗄️"),
        ("Tools", "tools", "⚙️"),
        ("Soft Skills", "soft_skills", "🤝"),
        ("Data Science", "data_science", "📊")
    ]
    
    for category_name, category_key, icon in skill_categories:
        category_skills = skills.get(category_key, [])
        if category_skills:
            st.markdown(f"**{icon} {category_name}:**")
            skills_html = "".join([f'<span class="skill-tag">{skill}</span>' for skill in category_skills])
            st.markdown(skills_html, unsafe_allow_html=True)
            st.markdown("")


def display_experience(experience: list):
    st.markdown("### 💼 Work Experience")
    
    if not experience:
        st.info("No work experience information found.")
        return
    
    for i, exp in enumerate(experience):
        with st.expander(f"{exp.get('title', 'Position')} at {exp.get('company', 'Company')}", expanded=i==0):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                if exp.get("title"):
                    st.write(f"**Position:** {exp['title']}")
                if exp.get("company"):
                    st.write(f"**Company:** {exp['company']}")
                if exp.get("location"):
                    st.write(f"**Location:** {exp['location']}")
            
            with col2:
                if exp.get("start_date") or exp.get("end_date"):
                    duration = f"{exp.get('start_date', 'N/A')} - {exp.get('end_date', 'N/A')}"
                    st.write(f"**Duration:** {duration}")
            
            if exp.get("description"):
                st.markdown("**Description:**")
                st.write(exp["description"])


def display_education(education: list):
    st.markdown("### 🎓 Education")
    
    if not education:
        st.info("No education information found.")
        return
    
    for edu in education:
        with st.expander(f"{edu.get('degree', 'Degree')} - {edu.get('institution', 'Institution')}"):
            if edu.get("degree"):
                st.write(f"**Degree:** {edu['degree']}")
            if edu.get("institution"):
                st.write(f"**Institution:** {edu['institution']}")
            if edu.get("graduation_date"):
                st.write(f"**Graduation:** {edu['graduation_date']}")
            if edu.get("gpa"):
                st.write(f"**GPA:** {edu['gpa']}")


...
# (rest of your Streamlit app code remains unchanged)

def display_raw_data(parsed_data: Dict[str, Any]):
    st.markdown("### 📄 Raw Parsed Data")

    col1, col2 = st.columns(2)

    contact = parsed_data.get("contact_info", {})
    skills = parsed_data.get("skills", {}).get("all_skills", [])
    education = parsed_data.get("education", [])
    experience = parsed_data.get("experience", [])

    combined = {
        "Name": contact.get("name", ""),
        "Email": contact.get("email", ""),
        "Phone": contact.get("phone", ""),
        "LinkedIn": contact.get("linkedin", ""),
        "GitHub": contact.get("github", ""),
        "Website": contact.get("website", ""),
        "Skills": ", ".join(skills),
        "Education": "; ".join([
            f"{e.get('degree', '')} - {e.get('institution', '')} ({e.get('graduation_date', '')})"
            for e in education
        ]),
        "Experience": "; ".join([
            f"{e.get('title', '')} at {e.get('company', '')} ({e.get('start_date', '')} to {e.get('end_date', '')})"
            for e in experience
        ])
    }

    df_combined = pd.DataFrame([combined])
    st.dataframe(df_combined, use_container_width=True)

    # Download button for the formatted table as CSV
    csv_download = df_combined.to_csv(index=False)
    st.download_button(
        label="📅 Download CSV",
        data=csv_download,
        file_name="structured_resume_data.csv",
        mime="text/csv"
    )

    # Download button for full parsed data as JSON
    json_download = json.dumps(parsed_data, indent=4)
    st.download_button(
        label="🔍 Download JSON",
        data=json_download,
        file_name="raw_resume_data.json",
        mime="application/json"
    )


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """Flatten nested dictionary for table display"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            if all(isinstance(i, dict) for i in v):
                for idx, item in enumerate(v):
                    items.extend(flatten_dict(item, f"{new_key}[{idx}]", sep=sep).items())
            else:
                items.append((new_key, ', '.join(str(i) for i in v)))
        else:
            items.append((new_key, v))
    return dict(items)


def create_csv_data(parsed_data: Dict[str, Any]) -> str:
    rows = []

    contact = parsed_data.get("contact_info", {})
    for key, value in contact.items():
        if value:
            rows.append({"Section": "Contact", "Field": key, "Value": value})

    skills = parsed_data.get("skills", {})
    for category, skill_list in skills.items():
        if skill_list and category != "all_skills":
            for skill in skill_list:
                rows.append({"Section": "Skills", "Field": category, "Value": skill})

    if rows:
        df = pd.DataFrame(rows)
        return df.to_csv(index=False)
    return "No data available"


if __name__ == "__main__":
    main()
