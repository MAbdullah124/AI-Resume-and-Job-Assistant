import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from docx import Document


# =========================
# PAGE CONFIGURATION
# =========================

st.set_page_config(
    page_title="AI Resume & Job Assistant",
    page_icon="💼",
    layout="wide"
)


# =========================
# CUSTOM CSS
# =========================

st.markdown("""
<style>

.main-title {
    font-size: 42px;
    font-weight: bold;
    text-align: center;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    color: #666;
    font-size: 18px;
    margin-bottom: 30px;
}

.result-box {
    padding: 20px;
    border-radius: 10px;
    background-color: #f5f7fa;
    border: 1px solid #ddd;
}

</style>
""", unsafe_allow_html=True)


# =========================
# API CONFIGURATION
# =========================

try:
    API_KEY = st.secrets["API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    API_KEY = None


# =========================
# AI MODEL
# =========================

def get_model():

    if not API_KEY:
        return None

    return genai.GenerativeModel("gemini-3.6-flash")


# =========================
# FILE TEXT EXTRACTION
# =========================

def extract_text(uploaded_file):

    file_name = uploaded_file.name.lower()

    # PDF
    if file_name.endswith(".pdf"):

        reader = PdfReader(uploaded_file)

        text = ""

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        return text


    # DOCX
    elif file_name.endswith(".docx"):

        document = Document(uploaded_file)

        text = ""

        for paragraph in document.paragraphs:
            text += paragraph.text + "\n"

        return text


    # TXT
    elif file_name.endswith(".txt"):

        return uploaded_file.read().decode("utf-8")


    return ""


# =========================
# AI REQUEST FUNCTION
# =========================

def ask_ai(prompt):

    model = get_model()

    if model is None:

        return "❌ API key is missing. Please add your Gemini API key in Streamlit secrets."

    try:

        response = model.generate_content(prompt)

        return response.text

    except Exception as e:

        return f"❌ AI request failed: {str(e)}"


# =========================
# HEADER
# =========================

st.markdown(
    '<div class="main-title">💼 AI Resume & Job Assistant</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Analyze your resume, match jobs, improve your CV and prepare for interviews with AI.</div>',
    unsafe_allow_html=True
)


# =========================
# SIDEBAR
# =========================

st.sidebar.title("⚙️ Settings")

experience_level = st.sidebar.selectbox(
    "Experience Level",
    [
        "Student / Fresh Graduate",
        "Entry Level",
        "Intermediate",
        "Experienced"
    ]
)

response_length = st.sidebar.selectbox(
    "AI Response Length",
    [
        "Short",
        "Medium",
        "Detailed"
    ]
)


st.sidebar.markdown("---")

st.sidebar.info(
    "Upload your resume and provide a job description. "
    "The AI will analyze both and provide useful career suggestions."
)


# =========================
# RESUME UPLOAD
# =========================

st.header("📄 Upload Your Resume")

resume_file = st.file_uploader(
    "Upload your resume",
    type=["pdf", "docx", "txt"]
)

resume_text = ""


if resume_file:

    with st.spinner("Reading your resume..."):

        resume_text = extract_text(resume_file)

    if resume_text:

        st.success("✅ Resume successfully loaded!")

        with st.expander("👀 Preview Resume Text"):

            st.text(resume_text[:5000])

    else:

        st.error("❌ Could not extract text from this file.")


# =========================
# JOB DESCRIPTION
# =========================

st.header("💼 Job Description")

job_description = st.text_area(
    "Paste the job description here",
    height=250,
    placeholder="Example: We are looking for a Python Developer with experience in AI, APIs, Git and SQL..."
)


# =========================
# ANALYSIS BUTTON
# =========================

st.markdown("---")

if st.button("🔍 Analyze Resume & Job", use_container_width=True):

    if not resume_text:

        st.warning("⚠️ Please upload your resume first.")

    elif not job_description.strip():

        st.warning("⚠️ Please enter a job description.")

    else:

        prompt = f"""
You are an expert AI career assistant.

Analyze the following resume and job description.

Candidate experience level:
{experience_level}

Desired response length:
{response_length}

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Provide a clear analysis with these sections:

1. 🎯 Job Match
- Give an approximate match percentage.
- Explain why the resume matches the job.

2. 🛠️ Matching Skills
List the skills found in the resume that are relevant to the job.

3. ❌ Missing Skills
List important skills required by the job that are missing or weak in the resume.

4. 💪 Resume Strengths
Identify the strongest parts of the resume.

5. ⚠️ Resume Weaknesses
Identify areas that should be improved.

6. 📚 Skills to Learn
Suggest the most useful skills the candidate should learn.

7. 📝 Resume Improvement Suggestions
Give practical suggestions for improving the resume.

Do not invent qualifications or experience that are not present in the resume.
"""

        with st.spinner("🤖 AI is analyzing your resume..."):

            result = ask_ai(prompt)

        st.subheader("📊 AI Analysis")

        st.markdown(
            f'<div class="result-box">{result}</div>',
            unsafe_allow_html=True
        )


# =========================
# RESUME SUMMARY GENERATOR
# =========================

st.markdown("---")

st.header("📝 AI Professional Summary Generator")

if st.button("✨ Generate Professional Summary"):

    if not resume_text:

        st.warning("⚠️ Please upload your resume first.")

    else:

        prompt = f"""
You are a professional resume writer.

Based ONLY on the information in this resume, create a professional
resume summary for a {experience_level} candidate.

Resume:

{resume_text}

Requirements:

- 3 to 5 sentences
- Professional tone
- ATS-friendly
- Do not invent experience
- Highlight relevant technical and professional skills
"""

        with st.spinner("✍️ Creating professional summary..."):

            result = ask_ai(prompt)

        st.subheader("✨ Generated Summary")

        st.write(result)


# =========================
# INTERVIEW QUESTIONS
# =========================

st.markdown("---")

st.header("🎤 Interview Preparation")

if st.button("🎯 Generate Interview Questions"):

    if not resume_text:

        st.warning("⚠️ Please upload your resume first.")

    elif not job_description.strip():

        st.warning("⚠️ Please enter the job description first.")

    else:

        prompt = f"""
You are an expert technical interviewer.

Generate 10 interview questions for this candidate based on their
resume and the target job.

RESUME:

{resume_text}

JOB DESCRIPTION:

{job_description}

Include:

1. Technical questions
2. Experience questions
3. Project questions
4. Behavioral questions

For each question, also provide a short explanation of what the
interviewer is looking for.

Do not invent experience that is not present in the resume.
"""

        with st.spinner("🎤 Preparing interview questions..."):

            result = ask_ai(prompt)

        st.subheader("🎤 Interview Questions")

        st.write(result)


# =========================
# RESUME IMPROVEMENT
# =========================

st.markdown("---")

st.header("🛠️ Improve a Resume Section")

section = st.selectbox(
    "Select a section to improve",
    [
        "Professional Summary",
        "Skills",
        "Projects",
        "Education",
        "Experience"
    ]
)

if st.button("🚀 Improve Selected Section"):

    if not resume_text:

        st.warning("⚠️ Please upload your resume first.")

    else:

        prompt = f"""
You are an expert ATS resume writer.

Improve the "{section}" section of the following resume.

Resume:

{resume_text}

Candidate level:
{experience_level}

Rules:

- Make it professional
- Make it concise
- Make it ATS-friendly
- Keep the information truthful
- Do not invent experience, degrees, companies or skills
- Focus on clarity and impact
"""

        with st.spinner("🚀 Improving your resume section..."):

            result = ask_ai(prompt)

        st.subheader(f"✨ Improved {section}")

        st.write(result)


# =========================
# FOOTER
# =========================

st.markdown("---")

st.caption(
    "💼 AI Resume & Job Assistant | Built with Python, Streamlit and Generative AI"
)
