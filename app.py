import os
import re
from datetime import datetime

import pandas as pd
import streamlit as st
from llama_cpp import Llama


# ------------------ Load GGUF Model ------------------ #
@st.cache_resource
def load_model():
    return Llama(
        model_path="Phi-3-mini-4k-instruct-q4.gguf",  # update path if needed
        n_ctx=4096,
        n_threads=8,
        n_gpu_layers=20,
        temperature=0.3,  # Lower temperature for consistent output
        top_p=0.9
    )

llm = load_model()

# ------------------ Validators ------------------ #
def valid_name(name): 
    return bool(re.match(r"^[A-Za-z ]+$", name)) and len(name.strip()) > 1

def valid_email(email): 
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email))

def valid_phone(phone): 
    return bool(re.match(r"^\d{9}$", phone))  # exactly 9 digits

def valid_experience(exp):
    try:
        years = int(exp)
        return 0 <= years <= 50
    except:
        return False

# ------------------ Question Quality Validator ------------------ #
def is_valid_question(question):
    """Check if a question is technically valid and meaningful"""
    if len(question.strip()) < 10:
        return False
    if not question.strip().endswith('?'):
        return False
    words = question.strip().split()
    if len(words) < 4:
        return False
    return True

# ------------------ Excel Export ------------------ #
def append_to_excel():
    """Append candidate data + Q&A into interview_database.xlsx (single sheet)."""
    filename = "interview_database.xlsx"

    # Flatten Q&A into one row
    qa_pairs = {}
    for i, (q, a) in enumerate(zip(st.session_state.questions, st.session_state.answers)):
        qa_pairs[f"Q{i+1}"] = q
        qa_pairs[f"A{i+1}"] = a

    # Candidate + metadata
    record = {
        **st.session_state.candidate,
        **qa_pairs,
        "Interview_Date": datetime.now().strftime("%Y-%m-%d"),
        "Interview_Time": datetime.now().strftime("%H:%M:%S"),
    }

    new_df = pd.DataFrame([record])

    if os.path.exists(filename):
        # Open in append mode safely
        with pd.ExcelWriter(filename, engine="openpyxl", mode="a", if_sheet_exists="overlay") as writer:
            existing = pd.read_excel(filename, sheet_name="All_Candidates")
            updated = pd.concat([existing, new_df], ignore_index=True)
            updated.to_excel(writer, sheet_name="All_Candidates", index=False)
    else:
        new_df.to_excel(filename, sheet_name="All_Candidates", index=False)

    return filename


# ------------------ Session State ------------------ #
if "candidate" not in st.session_state:
    st.session_state.candidate = {}
if "questions" not in st.session_state:
    st.session_state.questions = []
if "answers" not in st.session_state:
    st.session_state.answers = []
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🤖 AI Interview Chatbot")

# ------------------ Helper: Add message ------------------ #
def add_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})

# ------------------ Generate Interview Questions ------------------ #
def generate_interview_questions(position, experience, tech_stack):
    prompt = f"""<|system|>
You are an expert technical interviewer conducting interviews for software engineering positions.

<|user|>
Generate exactly 5 technical interview questions for a candidate with the following profile:
- Position: {position}
- Experience: {experience} years
- Tech Stack: {tech_stack}

Requirements:
1. Generate EXACTLY 5 questions, numbered 1-5
2. Each question must be a complete, well-formed technical question
3. Questions should be relevant to the candidate's tech stack and experience level
4. Adjust difficulty based on experience level:
   - 0-1 years: Basic concepts, syntax, simple problem-solving
   - 2-5 years: Intermediate concepts, optimization, design patterns
   - 5+ years: System design, scalability, architecture, advanced concepts
5. Each question must end with a question mark
6. Focus on practical, job-relevant technical skills

Example format:
1. What is the difference between let, const, and var in JavaScript?
2. How would you optimize a slow SQL query?
3. Explain the concept of dependency injection in software design?
4. What are the trade-offs between using a microservices vs monolithic architecture?
5. How would you implement rate limiting in a REST API?

Now generate 5 questions for this candidate:

<|assistant|>"""

    try:
        response = llm(
            prompt,
            max_tokens=800,
            temperature=0.3,
            top_p=0.9,
            stop=["<|user|>", "<|system|>"]
        )
        raw_text = response["choices"][0]["text"].strip()
        lines = raw_text.split('\n')
        questions = []

        for line in lines:
            line = line.strip()
            if re.match(r'^\d+\.', line):
                question = re.sub(r'^\d+\.\s*', '', line).strip()
                if is_valid_question(question):
                    questions.append(question)

        if len(questions) < 5:
            questions = generate_fallback_questions(position, experience, tech_stack)

        return questions[:5]

    except Exception as e:
        st.error(f"Error generating questions: {e}")

# ------------------ Initial Greeting ------------------ #
if not st.session_state.messages:
    add_message("assistant", "Hello 👋, welcome to your technical interview! What's your full name?")

# ------------------ Show chat history ------------------ #
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ------------------ Chat input ------------------ #
user_input = st.chat_input("Type your response...")

if user_input:
    add_message("user", user_input)

    # Candidate onboarding
    if "Full Name" not in st.session_state.candidate:
        if valid_name(user_input):
            st.session_state.candidate["Full Name"] = user_input
            add_message("assistant", "Great! What's your email?")
        else:
            add_message("assistant", "❌ Invalid name. Please enter again (letters and spaces only).")

    elif "Email" not in st.session_state.candidate:
        if valid_email(user_input):
            st.session_state.candidate["Email"] = user_input
            add_message("assistant", "Got it ✅. Please share your phone number (9 digits).")
        else:
            add_message("assistant", "❌ Invalid email format. Try again.")

    elif "Phone" not in st.session_state.candidate:
        if valid_phone(user_input):
            st.session_state.candidate["Phone"] = user_input
            add_message("assistant", "Thanks! How many years of experience do you have?")
        else:
            add_message("assistant", "❌ Invalid phone number. Must be 9 digits.")

    elif "Experience" not in st.session_state.candidate:
        if valid_experience(user_input):
            st.session_state.candidate["Experience"] = int(user_input)
            add_message("assistant", "Perfect. What position are you applying for?")
        else:
            add_message("assistant", "❌ Enter a valid number between 0 and 50.")

    elif "Desired Position" not in st.session_state.candidate:
        st.session_state.candidate["Desired Position"] = user_input
        add_message("assistant", "Nice! Where are you currently located?")

    elif "Location" not in st.session_state.candidate:
        st.session_state.candidate["Location"] = user_input
        add_message("assistant", "Great! Finally, please list your tech stack (comma-separated).")

    elif "Tech Stack" not in st.session_state.candidate:
        st.session_state.candidate["Tech Stack"] = user_input

        with st.spinner("Generating your personalized interview questions..."):
            questions = generate_interview_questions(
                st.session_state.candidate["Desired Position"],
                st.session_state.candidate["Experience"],
                user_input
            )
            st.session_state.questions = questions
            st.session_state.q_index = 0

        add_message("assistant", "Thanks for the details! Let's start your technical interview.")
        add_message("assistant", f"**Question 1:** {st.session_state.questions[0]}")

    # ------------------ Conduct Interview ------------------ #
    else:
        idx = st.session_state.q_index
        if idx < len(st.session_state.questions):
            st.session_state.answers.append(user_input)
            st.session_state.q_index += 1

            if st.session_state.q_index < len(st.session_state.questions):
                next_q = st.session_state.q_index + 1
                add_message("assistant", f"**Question {next_q}:** {st.session_state.questions[st.session_state.q_index]}")
            else:
                add_message("assistant", "✅ That concludes the interview. Thank you for your time!")

                # Candidate summary
                summary = "### 📋 Interview Summary\n\n"
                summary += "**Candidate Information:**\n"
                for k, v in st.session_state.candidate.items():
                    summary += f"- **{k}:** {v}\n"

                summary += "\n**Interview Q&A:**\n"
                for i, (q, a) in enumerate(zip(st.session_state.questions, st.session_state.answers)):
                    summary += f"\n**Q{i+1}:** {q}\n"
                    summary += f"**Answer:** {a}\n"

                add_message("assistant", summary)

                # Save results to Excel
                filename = append_to_excel()
                

    st.rerun()

# ------------------ Sidebar with candidate info ------------------ #
if st.session_state.candidate:
    with st.sidebar:
        st.subheader("👤 Candidate Info")
        for key, value in st.session_state.candidate.items():
            st.write(f"**{key}:** {value}")

        if st.session_state.questions:
            st.subheader("📝 Interview Progress")
            st.progress(st.session_state.q_index / len(st.session_state.questions))
            st.write(f"Question {st.session_state.q_index}/{len(st.session_state.questions)}")

# ------------------ Debug info ------------------ #
if st.checkbox("Show Debug Info"):
    st.json({
        "candidate": st.session_state.candidate,
        "questions": st.session_state.questions,
        "answers": st.session_state.answers,
        "q_index": st.session_state.q_index
    })
