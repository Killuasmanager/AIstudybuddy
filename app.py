"""
🎓 StudyBuddy AI - Your Intelligent Study Companion
An AI-powered study assistant with adaptive quizzing, flashcards, and smart summarization.
Built with Streamlit and Google Gemini API.
"""

import streamlit as st
import google.generativeai as genai
from streamlit_option_menu import option_menu
import json
import time
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
import PyPDF2
import io

# ============================================================
# CONFIGURATION & STYLING
# ============================================================

st.set_page_config(
    page_title="StudyBuddy AI 🎓",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for stunning UI
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&family=Space+Mono:wght@400;700&display=swap');

/* Global Styles */
.stApp {
    font-family: 'Poppins', sans-serif;
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* Main container styling */
.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem 2.5rem;
    border-radius: 20px;
    margin-bottom: 2rem;
    box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
}

.main-header h1 {
    color: white;
    font-size: 2.5rem;
    font-weight: 800;
    margin: 0;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
}

.main-header p {
    color: rgba(255,255,255,0.9);
    font-size: 1.1rem;
    margin-top: 0.5rem;
}

/* Card styling */
.feature-card {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    border: 1px solid rgba(0,0,0,0.05);
    transition: all 0.3s ease;
    height: 100%;
}

.feature-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 30px rgba(102, 126, 234, 0.2);
}

/* Flashcard styling */
.flashcard-container {
    perspective: 1000px;
    margin: 1rem 0;
}

.flashcard {
    background: linear-gradient(145deg, #ffffff 0%, #f8f9ff 100%);
    border-radius: 20px;
    padding: 2.5rem;
    min-height: 250px;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    box-shadow: 0 8px 32px rgba(102, 126, 234, 0.15);
    border: 2px solid rgba(102, 126, 234, 0.1);
    transition: all 0.4s ease;
}

.flashcard:hover {
    box-shadow: 0 12px 40px rgba(102, 126, 234, 0.25);
}

.flashcard-front {
    background: linear-gradient(145deg, #667eea 0%, #764ba2 100%);
    color: white;
}

.flashcard-back {
    background: linear-gradient(145deg, #11998e 0%, #38ef7d 100%);
    color: white;
}

.flashcard h3 {
    font-size: 1.4rem;
    font-weight: 600;
    line-height: 1.6;
    margin: 0;
}

/* Quiz styling */
.quiz-option {
    background: white;
    border: 2px solid #e0e0e0;
    border-radius: 12px;
    padding: 1rem 1.5rem;
    margin: 0.5rem 0;
    cursor: pointer;
    transition: all 0.3s ease;
}

.quiz-option:hover {
    border-color: #667eea;
    background: rgba(102, 126, 234, 0.05);
}

.quiz-correct {
    background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
    border-color: #28a745;
}

.quiz-incorrect {
    background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
    border-color: #dc3545;
}

/* Progress bar custom */
.progress-container {
    background: #e9ecef;
    border-radius: 10px;
    height: 12px;
    overflow: hidden;
    margin: 1rem 0;
}

.progress-bar {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    height: 100%;
    border-radius: 10px;
    transition: width 0.5s ease;
}

/* Metric cards */
.metric-card {
    background: linear-gradient(145deg, #ffffff 0%, #f8f9ff 100%);
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    border: 1px solid rgba(102, 126, 234, 0.1);
}

.metric-value {
    font-size: 2.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.metric-label {
    color: #6c757d;
    font-size: 0.9rem;
    font-weight: 500;
    margin-top: 0.5rem;
}

/* Timer styling */
.timer-display {
    font-family: 'Space Mono', monospace;
    font-size: 4rem;
    font-weight: 700;
    text-align: center;
    padding: 2rem;
    border-radius: 20px;
    margin: 1rem 0;
}

.timer-work {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

.timer-break {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    color: white;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.75rem 2rem;
    font-weight: 600;
    font-size: 1rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f8f9ff 0%, #ffffff 100%);
}

[data-testid="stSidebar"] .stMarkdown h1 {
    color: #667eea;
}

/* Text area and inputs */
.stTextArea textarea, .stTextInput input {
    border-radius: 12px;
    border: 2px solid #e0e0e0;
    transition: all 0.3s ease;
}

.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* Tabs styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    padding: 10px 20px;
    background: #f8f9ff;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Expander styling */
.streamlit-expanderHeader {
    background: #f8f9ff;
    border-radius: 12px;
}

/* Animation keyframes */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.animate-fade-in {
    animation: fadeInUp 0.5s ease forwards;
}

@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
}

.pulse {
    animation: pulse 2s infinite;
}

/* Celebration animation */
@keyframes celebrate {
    0%, 100% { transform: rotate(0deg); }
    25% { transform: rotate(-10deg); }
    75% { transform: rotate(10deg); }
}

.celebrate {
    animation: celebrate 0.5s ease;
}

/* Summary box */
.summary-box {
    background: linear-gradient(145deg, #f8f9ff 0%, #ffffff 100%);
    border-left: 4px solid #667eea;
    border-radius: 0 12px 12px 0;
    padding: 1.5rem;
    margin: 1rem 0;
}

/* ELI5 box */
.eli5-box {
    background: linear-gradient(145deg, #fff9e6 0%, #fff5d6 100%);
    border-left: 4px solid #ffc107;
    border-radius: 0 12px 12px 0;
    padding: 1.5rem;
    margin: 1rem 0;
}

/* Topic tags */
.topic-tag {
    display: inline-block;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 500;
    margin: 0.2rem;
}

/* Streak badge */
.streak-badge {
    background: linear-gradient(135deg, #ff6b6b 0%, #ffa500 100%);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 25px;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ============================================================
# DATA CLASSES & ENUMS
# ============================================================

class Difficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

@dataclass
class Flashcard:
    """Represents a study flashcard"""
    id: int
    front: str  # Question or term
    back: str   # Answer or definition
    topic: str
    difficulty: Difficulty = Difficulty.MEDIUM
    times_reviewed: int = 0
    times_correct: int = 0
    
    @property
    def mastery_score(self) -> float:
        """Calculate mastery score (0-100)"""
        if self.times_reviewed == 0:
            return 0
        return (self.times_correct / self.times_reviewed) * 100

@dataclass
class QuizQuestion:
    """Represents a quiz question"""
    id: int
    question: str
    options: List[str]
    correct_answer: int  # Index of correct option
    explanation: str
    topic: str
    difficulty: Difficulty = Difficulty.MEDIUM

@dataclass
class StudySession:
    """Tracks a study session"""
    start_time: datetime
    end_time: Optional[datetime] = None
    topics_studied: List[str] = field(default_factory=list)
    flashcards_reviewed: int = 0
    quiz_questions_answered: int = 0
    quiz_correct: int = 0
    pomodoros_completed: int = 0
    
    @property
    def duration_minutes(self) -> int:
        """Calculate session duration in minutes"""
        end = self.end_time or datetime.now()
        return int((end - self.start_time).total_seconds() / 60)

@dataclass 
class UserProgress:
    """Tracks overall user progress"""
    total_study_time: int = 0  # minutes
    total_flashcards_reviewed: int = 0
    total_quizzes_taken: int = 0
    total_quiz_correct: int = 0
    topics_mastery: Dict[str, float] = field(default_factory=dict)
    study_streak: int = 0
    last_study_date: Optional[str] = None
    sessions: List[StudySession] = field(default_factory=list)

# ============================================================
# AI SERVICE CLASS
# ============================================================

class GeminiAIService:
    """Handles all AI interactions using Google Gemini API"""
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def summarize_content(self, content: str, style: str = "detailed") -> str:
        """Generate a summary of the content"""
        prompts = {
            "detailed": f"""Summarize the following content in a clear, structured way. 
            Include key concepts, main ideas, and important details.
            Use bullet points for clarity.
            
            Content:
            {content}
            
            Provide a comprehensive summary:""",
            
            "brief": f"""Provide a brief, concise summary (3-5 sentences) of the following content:
            
            {content}
            
            Brief summary:""",
            
            "eli5": f"""Explain the following content as if explaining to a 5-year-old child.
            Use simple words, fun analogies, and relatable examples.
            Make it engaging and easy to understand.
            
            Content:
            {content}
            
            Simple explanation:"""
        }
        
        try:
            response = self.model.generate_content(prompts.get(style, prompts["detailed"]))
            return response.text
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def generate_flashcards(self, content: str, num_cards: int = 10, topic: str = "General") -> List[Dict]:
        """Generate flashcards from content"""
        prompt = f"""Based on the following content, generate exactly {num_cards} flashcards for studying.
        
        Content:
        {content}
        
        Return ONLY a valid JSON array with this exact format (no markdown, no extra text):
        [
            {{"front": "Question or term here", "back": "Answer or definition here", "difficulty": "easy/medium/hard"}},
            ...
        ]
        
        Make the flashcards:
        - Cover the most important concepts
        - Have clear, concise questions
        - Provide comprehensive but focused answers
        - Vary difficulty levels
        
        JSON array:"""
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            # Clean up response
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            text = text.strip()
            
            cards_data = json.loads(text)
            return cards_data
        except Exception as e:
            # Return sample flashcards on error
            return [
                {"front": "What is the main topic?", "back": "Unable to parse content. Please try again.", "difficulty": "easy"}
            ]
    
    def generate_quiz(self, content: str, num_questions: int = 5, difficulty: str = "mixed") -> List[Dict]:
        """Generate quiz questions from content"""
        prompt = f"""Based on the following content, generate exactly {num_questions} multiple choice quiz questions.
        
        Content:
        {content}
        
        Difficulty preference: {difficulty}
        
        Return ONLY a valid JSON array with this exact format (no markdown, no extra text):
        [
            {{
                "question": "Question text here?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": 0,
                "explanation": "Brief explanation of why this is correct",
                "difficulty": "easy/medium/hard"
            }},
            ...
        ]
        
        Make sure:
        - Questions test understanding, not just memorization
        - All 4 options are plausible
        - correct_answer is the index (0-3) of the correct option
        - Explanations are educational
        
        JSON array:"""
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            # Clean up response
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            text = text.strip()
            
            questions_data = json.loads(text)
            return questions_data
        except Exception as e:
            return [
                {
                    "question": "Error generating quiz. Please try again.",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": 0,
                    "explanation": "Quiz generation failed.",
                    "difficulty": "easy"
                }
            ]
    
    def explain_concept(self, concept: str, context: str = "") -> str:
        """Explain a specific concept in detail"""
        prompt = f"""Explain the following concept in detail:
        
        Concept: {concept}
        {"Context: " + context if context else ""}
        
        Provide:
        1. A clear definition
        2. Key characteristics or components
        3. Real-world examples
        4. Common misconceptions (if any)
        5. How it relates to other concepts
        
        Make the explanation thorough but accessible:"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error explaining concept: {str(e)}"
    
    def identify_weak_areas(self, quiz_results: List[Dict]) -> str:
        """Analyze quiz results and identify weak areas"""
        prompt = f"""Analyze these quiz results and identify areas that need more study:
        
        Quiz Results:
        {json.dumps(quiz_results, indent=2)}
        
        Provide:
        1. Overall performance assessment
        2. Specific topics/concepts that need review
        3. Recommended study strategies
        4. Encouragement and motivation
        
        Be constructive and helpful:"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return "Unable to analyze results. Keep studying!"

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def extract_text_from_pdf(pdf_file) -> str:
    """Extract text content from uploaded PDF"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.read()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def init_session_state():
    """Initialize all session state variables"""
    defaults = {
        'api_key': '',
        'ai_service': None,
        'content': '',
        'topic': 'General',
        'flashcards': [],
        'current_card_index': 0,
        'show_answer': False,
        'quiz_questions': [],
        'current_question_index': 0,
        'quiz_answers': [],
        'quiz_submitted': False,
        'user_progress': UserProgress(),
        'current_session': None,
        'timer_running': False,
        'timer_seconds': 25 * 60,
        'timer_mode': 'work',
        'pomodoro_count': 0,
        'summaries': [],
        'study_history': []
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def render_metric_card(value: str, label: str, icon: str = "📊"):
    """Render a styled metric card"""
    st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 1.5rem;">{icon}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
        </div>
    """, unsafe_allow_html=True)

def format_time(seconds: int) -> str:
    """Format seconds into MM:SS"""
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins:02d}:{secs:02d}"

# ============================================================
# PAGE COMPONENTS
# ============================================================

def render_header():
    """Render the main header"""
    st.markdown("""
        <div class="main-header">
            <h1>🎓 StudyBuddy AI</h1>
            <p>Your intelligent study companion powered by AI • Learn smarter, not harder</p>
        </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Render the sidebar with navigation and settings"""
    with st.sidebar:
        st.markdown("## 🎯 Navigation")
        
        selected = option_menu(
            menu_title=None,
            options=["📚 Study Material", "🎴 Flashcards", "❓ Quiz Mode", "⏱️ Pomodoro Timer", "📊 Progress"],
            icons=["book", "card-text", "question-circle", "clock", "graph-up"],
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#667eea", "font-size": "18px"},
                "nav-link": {
                    "font-size": "14px",
                    "text-align": "left",
                    "margin": "5px 0",
                    "border-radius": "10px",
                    "padding": "10px 15px",
                },
                "nav-link-selected": {
                    "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                    "color": "white",
                },
            }
        )
        
        st.markdown("---")
        
        # API Key input
        st.markdown("### 🔑 API Configuration")
        api_key = st.text_input(
            "Gemini API Key",
            type="password",
            value=st.session_state.api_key,
            help="Get your free API key from Google AI Studio"
        )
        
        if api_key != st.session_state.api_key:
            st.session_state.api_key = api_key
            if api_key:
                st.session_state.ai_service = GeminiAIService(api_key)
                st.success("✅ API Key configured!")
        
        st.markdown("""
            <small>
            <a href="https://makersuite.google.com/app/apikey" target="_blank">
            🔗 Get free Gemini API Key
            </a>
            </small>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Study streak
        progress = st.session_state.user_progress
        if progress.study_streak > 0:
            st.markdown(f"""
                <div class="streak-badge">
                    🔥 {progress.study_streak} Day Streak!
                </div>
            """, unsafe_allow_html=True)
        
        return selected

def page_study_material():
    """Study Material page - upload and process content"""
    st.markdown("## 📚 Study Material")
    st.markdown("Upload your study materials and let AI help you learn effectively.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Topic input
        topic = st.text_input(
            "📌 Topic Name",
            value=st.session_state.topic,
            placeholder="e.g., Machine Learning Basics, World History, etc."
        )
        st.session_state.topic = topic
        
        # Content input tabs
        tab1, tab2, tab3 = st.tabs(["📝 Paste Text", "📄 Upload PDF", "🔗 From Summary"])
        
        with tab1:
            content = st.text_area(
                "Paste your study content here",
                height=300,
                placeholder="Paste lecture notes, textbook excerpts, or any study material...",
                value=st.session_state.content
            )
            if content:
                st.session_state.content = content
        
        with tab2:
            uploaded_file = st.file_uploader(
                "Upload a PDF file",
                type=['pdf'],
                help="Upload lecture slides, textbooks, or notes in PDF format"
            )
            
            if uploaded_file:
                with st.spinner("📖 Extracting text from PDF..."):
                    extracted_text = extract_text_from_pdf(uploaded_file)
                    st.session_state.content = extracted_text
                    st.success(f"✅ Extracted {len(extracted_text)} characters from PDF")
                    with st.expander("Preview extracted text"):
                        st.text(extracted_text[:2000] + "..." if len(extracted_text) > 2000 else extracted_text)
        
        with tab3:
            if st.session_state.summaries:
                selected_summary = st.selectbox(
                    "Select a previous summary",
                    options=range(len(st.session_state.summaries)),
                    format_func=lambda x: f"Summary {x+1}: {st.session_state.summaries[x][:50]}..."
                )
                if st.button("Use this summary"):
                    st.session_state.content = st.session_state.summaries[selected_summary]
                    st.success("Content loaded!")
            else:
                st.info("No summaries yet. Generate some summaries first!")
    
    with col2:
        st.markdown("### ⚡ Quick Actions")
        
        if st.session_state.content and st.session_state.ai_service:
            
            # Summarization options
            st.markdown("#### 📝 Summarize")
            summary_style = st.radio(
                "Summary style",
                ["detailed", "brief", "eli5"],
                format_func=lambda x: {
                    "detailed": "📚 Detailed",
                    "brief": "⚡ Brief",
                    "eli5": "👶 ELI5 (Simple)"
                }[x],
                horizontal=True
            )
            
            if st.button("🪄 Generate Summary", use_container_width=True):
                with st.spinner("🤖 AI is summarizing..."):
                    summary = st.session_state.ai_service.summarize_content(
                        st.session_state.content,
                        summary_style
                    )
                    st.session_state.summaries.append(summary)
            
            st.markdown("---")
            
            # Flashcard generation
            st.markdown("#### 🎴 Flashcards")
            num_cards = st.slider("Number of cards", 5, 20, 10)
            
            if st.button("🎴 Generate Flashcards", use_container_width=True):
                with st.spinner("🤖 Creating flashcards..."):
                    cards_data = st.session_state.ai_service.generate_flashcards(
                        st.session_state.content,
                        num_cards,
                        st.session_state.topic
                    )
                    
                    flashcards = []
                    for i, card in enumerate(cards_data):
                        flashcards.append(Flashcard(
                            id=i,
                            front=card.get('front', 'Question'),
                            back=card.get('back', 'Answer'),
                            topic=st.session_state.topic,
                            difficulty=Difficulty(card.get('difficulty', 'medium'))
                        ))
                    
                    st.session_state.flashcards = flashcards
                    st.success(f"✅ Generated {len(flashcards)} flashcards!")
            
            st.markdown("---")
            
            # Quiz generation
            st.markdown("#### ❓ Quiz")
            num_questions = st.slider("Number of questions", 3, 15, 5)
            
            if st.button("❓ Generate Quiz", use_container_width=True):
                with st.spinner("🤖 Creating quiz..."):
                    questions_data = st.session_state.ai_service.generate_quiz(
                        st.session_state.content,
                        num_questions
                    )
                    
                    quiz_questions = []
                    for i, q in enumerate(questions_data):
                        quiz_questions.append(QuizQuestion(
                            id=i,
                            question=q.get('question', 'Question'),
                            options=q.get('options', ['A', 'B', 'C', 'D']),
                            correct_answer=q.get('correct_answer', 0),
                            explanation=q.get('explanation', ''),
                            topic=st.session_state.topic,
                            difficulty=Difficulty(q.get('difficulty', 'medium'))
                        ))
                    
                    st.session_state.quiz_questions = quiz_questions
                    st.session_state.quiz_answers = [None] * len(quiz_questions)
                    st.session_state.quiz_submitted = False
                    st.session_state.current_question_index = 0
                    st.success(f"✅ Generated {len(quiz_questions)} questions!")
        
        elif not st.session_state.ai_service:
            st.warning("⚠️ Please enter your Gemini API key in the sidebar")
        else:
            st.info("📝 Add some study content to get started")
    
    # Display summaries
    if st.session_state.summaries:
        st.markdown("---")
        st.markdown("### 📋 Generated Summaries")
        
        for i, summary in enumerate(reversed(st.session_state.summaries[-3:])):  # Show last 3
            with st.expander(f"Summary {len(st.session_state.summaries) - i}", expanded=(i == 0)):
                if "simple" in summary.lower() or "like" in summary.lower()[:50]:
                    st.markdown(f'<div class="eli5-box">{summary}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)

def page_flashcards():
    """Flashcards page - review and learn"""
    st.markdown("## 🎴 Flashcards")
    
    if not st.session_state.flashcards:
        st.info("📝 No flashcards yet! Go to Study Material to generate some.")
        return
    
    cards = st.session_state.flashcards
    current_idx = st.session_state.current_card_index
    current_card = cards[current_idx]
    
    # Progress bar
    progress = (current_idx + 1) / len(cards)
    st.markdown(f"""
        <div class="progress-container">
            <div class="progress-bar" style="width: {progress * 100}%"></div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"**Card {current_idx + 1} of {len(cards)}** • Topic: `{current_card.topic}` • Difficulty: `{current_card.difficulty.value}`")
    
    # Flashcard display
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        if st.session_state.show_answer:
            st.markdown(f"""
                <div class="flashcard flashcard-back animate-fade-in">
                    <div>
                        <small style="opacity: 0.8;">ANSWER</small>
                        <h3>{current_card.back}</h3>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="flashcard flashcard-front animate-fade-in">
                    <div>
                        <small style="opacity: 0.8;">QUESTION</small>
                        <h3>{current_card.front}</h3>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        # Control buttons
        bcol1, bcol2, bcol3 = st.columns(3)
        
        with bcol1:
            if st.button("⬅️ Previous", use_container_width=True, disabled=current_idx == 0):
                st.session_state.current_card_index -= 1
                st.session_state.show_answer = False
                st.rerun()
        
        with bcol2:
            if st.button("🔄 Flip Card", use_container_width=True):
                st.session_state.show_answer = not st.session_state.show_answer
                st.rerun()
        
        with bcol3:
            if st.button("➡️ Next", use_container_width=True, disabled=current_idx == len(cards) - 1):
                st.session_state.current_card_index += 1
                st.session_state.show_answer = False
                # Update progress
                st.session_state.user_progress.total_flashcards_reviewed += 1
                st.rerun()
        
        # Self-assessment buttons (when answer is shown)
        if st.session_state.show_answer:
            st.markdown("---")
            st.markdown("**How well did you know this?**")
            
            acol1, acol2, acol3 = st.columns(3)
            
            with acol1:
                if st.button("😕 Still Learning", use_container_width=True):
                    current_card.times_reviewed += 1
                    st.session_state.show_answer = False
                    if current_idx < len(cards) - 1:
                        st.session_state.current_card_index += 1
                    st.rerun()
            
            with acol2:
                if st.button("🤔 Getting There", use_container_width=True):
                    current_card.times_reviewed += 1
                    current_card.times_correct += 0.5
                    st.session_state.show_answer = False
                    if current_idx < len(cards) - 1:
                        st.session_state.current_card_index += 1
                    st.rerun()
            
            with acol3:
                if st.button("😎 Got It!", use_container_width=True):
                    current_card.times_reviewed += 1
                    current_card.times_correct += 1
                    st.session_state.show_answer = False
                    if current_idx < len(cards) - 1:
                        st.session_state.current_card_index += 1
                    st.rerun()
    
    # Card overview
    st.markdown("---")
    st.markdown("### 📑 All Cards")
    
    card_cols = st.columns(5)
    for i, card in enumerate(cards):
        with card_cols[i % 5]:
            mastery = card.mastery_score
            color = "#28a745" if mastery >= 70 else "#ffc107" if mastery >= 40 else "#6c757d"
            
            if st.button(
                f"{'✅' if mastery >= 70 else '🔶' if mastery >= 40 else '⬜'} {i+1}",
                key=f"card_nav_{i}",
                use_container_width=True
            ):
                st.session_state.current_card_index = i
                st.session_state.show_answer = False
                st.rerun()

def page_quiz():
    """Quiz page - test knowledge"""
    st.markdown("## ❓ Quiz Mode")
    
    if not st.session_state.quiz_questions:
        st.info("📝 No quiz questions yet! Go to Study Material to generate some.")
        return
    
    questions = st.session_state.quiz_questions
    
    if not st.session_state.quiz_submitted:
        # Quiz in progress
        progress = sum(1 for a in st.session_state.quiz_answers if a is not None) / len(questions)
        st.markdown(f"""
            <div class="progress-container">
                <div class="progress-bar" style="width: {progress * 100}%"></div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"**Progress: {sum(1 for a in st.session_state.quiz_answers if a is not None)}/{len(questions)} answered**")
        
        # Display all questions
        for i, question in enumerate(questions):
            with st.container():
                st.markdown(f"""
                    <div class="feature-card">
                        <span class="topic-tag">{question.topic}</span>
                        <span class="topic-tag" style="background: linear-gradient(135deg, #6c757d 0%, #495057 100%);">
                            {question.difficulty.value}
                        </span>
                        <h4 style="margin-top: 1rem;">Question {i+1}</h4>
                        <p style="font-size: 1.1rem;">{question.question}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Radio buttons for options
                answer = st.radio(
                    f"Select your answer for Q{i+1}",
                    options=range(len(question.options)),
                    format_func=lambda x, q=question: f"{chr(65+x)}. {q.options[x]}",
                    key=f"quiz_q_{i}",
                    index=st.session_state.quiz_answers[i] if st.session_state.quiz_answers[i] is not None else None,
                    label_visibility="collapsed"
                )
                
                if answer is not None:
                    st.session_state.quiz_answers[i] = answer
                
                st.markdown("---")
        
        # Submit button
        if st.button("📊 Submit Quiz", use_container_width=True, type="primary"):
            if None in st.session_state.quiz_answers:
                st.warning("⚠️ Please answer all questions before submitting!")
            else:
                st.session_state.quiz_submitted = True
                # Update progress
                correct = sum(1 for i, q in enumerate(questions) 
                            if st.session_state.quiz_answers[i] == q.correct_answer)
                st.session_state.user_progress.total_quizzes_taken += 1
                st.session_state.user_progress.total_quiz_correct += correct
                st.rerun()
    
    else:
        # Quiz results
        correct_count = sum(1 for i, q in enumerate(questions) 
                          if st.session_state.quiz_answers[i] == q.correct_answer)
        score = (correct_count / len(questions)) * 100
        
        # Score display
        if score >= 80:
            emoji = "🏆"
            message = "Excellent work!"
            color = "#28a745"
        elif score >= 60:
            emoji = "👍"
            message = "Good job! Keep practicing!"
            color = "#ffc107"
        else:
            emoji = "💪"
            message = "Keep learning! You'll get there!"
            color = "#dc3545"
        
        st.markdown(f"""
            <div style="text-align: center; padding: 2rem; background: linear-gradient(145deg, #f8f9ff 0%, #ffffff 100%); 
                        border-radius: 20px; margin-bottom: 2rem;">
                <div style="font-size: 4rem;">{emoji}</div>
                <h2 style="color: {color}; margin: 1rem 0;">{score:.0f}%</h2>
                <p style="font-size: 1.2rem; color: #6c757d;">{correct_count}/{len(questions)} correct • {message}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Detailed results
        st.markdown("### 📋 Detailed Results")
        
        for i, question in enumerate(questions):
            user_answer = st.session_state.quiz_answers[i]
            is_correct = user_answer == question.correct_answer
            
            with st.expander(
                f"{'✅' if is_correct else '❌'} Question {i+1}: {question.question[:50]}...",
                expanded=not is_correct
            ):
                st.markdown(f"**Question:** {question.question}")
                
                for j, option in enumerate(question.options):
                    if j == question.correct_answer:
                        st.markdown(f"✅ **{chr(65+j)}. {option}** (Correct)")
                    elif j == user_answer and not is_correct:
                        st.markdown(f"❌ ~~{chr(65+j)}. {option}~~ (Your answer)")
                    else:
                        st.markdown(f"⬜ {chr(65+j)}. {option}")
                
                st.markdown(f"**Explanation:** {question.explanation}")
        
        # Action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Retake Quiz", use_container_width=True):
                st.session_state.quiz_answers = [None] * len(questions)
                st.session_state.quiz_submitted = False
                st.rerun()
        
        with col2:
            if st.button("📝 New Quiz", use_container_width=True):
                st.session_state.quiz_questions = []
                st.session_state.quiz_answers = []
                st.session_state.quiz_submitted = False
                st.rerun()

def page_pomodoro():
    """Pomodoro Timer page"""
    st.markdown("## ⏱️ Pomodoro Timer")
    st.markdown("Stay focused with the Pomodoro Technique - 25 minutes of focused study, then a 5-minute break!")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Timer display
        timer_class = "timer-work" if st.session_state.timer_mode == "work" else "timer-break"
        mode_text = "🎯 FOCUS TIME" if st.session_state.timer_mode == "work" else "☕ BREAK TIME"
        
        st.markdown(f"""
            <div class="timer-display {timer_class}">
                <div style="font-size: 1rem; margin-bottom: 0.5rem;">{mode_text}</div>
                {format_time(st.session_state.timer_seconds)}
            </div>
        """, unsafe_allow_html=True)
        
        # Timer controls
        bcol1, bcol2, bcol3, bcol4 = st.columns(4)
        
        with bcol1:
            if st.button("▶️ Start" if not st.session_state.timer_running else "⏸️ Pause", 
                        use_container_width=True):
                st.session_state.timer_running = not st.session_state.timer_running
        
        with bcol2:
            if st.button("🔄 Reset", use_container_width=True):
                st.session_state.timer_seconds = 25 * 60 if st.session_state.timer_mode == "work" else 5 * 60
                st.session_state.timer_running = False
        
        with bcol3:
            if st.button("🎯 Work (25m)", use_container_width=True):
                st.session_state.timer_mode = "work"
                st.session_state.timer_seconds = 25 * 60
                st.session_state.timer_running = False
                st.rerun()
        
        with bcol4:
            if st.button("☕ Break (5m)", use_container_width=True):
                st.session_state.timer_mode = "break"
                st.session_state.timer_seconds = 5 * 60
                st.session_state.timer_running = False
                st.rerun()
        
        # Auto-update timer
        if st.session_state.timer_running and st.session_state.timer_seconds > 0:
            time.sleep(1)
            st.session_state.timer_seconds -= 1
            
            if st.session_state.timer_seconds == 0:
                st.session_state.timer_running = False
                if st.session_state.timer_mode == "work":
                    st.session_state.pomodoro_count += 1
                    st.session_state.user_progress.total_study_time += 25
                    st.balloons()
                    st.success("🎉 Pomodoro complete! Time for a break!")
                    st.session_state.timer_mode = "break"
                    st.session_state.timer_seconds = 5 * 60
                else:
                    st.info("☕ Break over! Ready for another focus session?")
                    st.session_state.timer_mode = "work"
                    st.session_state.timer_seconds = 25 * 60
            
            st.rerun()
    
    with col2:
        st.markdown("### 📊 Today's Progress")
        
        render_metric_card(str(st.session_state.pomodoro_count), "Pomodoros Completed", "🍅")
        st.markdown("<br>", unsafe_allow_html=True)
        render_metric_card(f"{st.session_state.pomodoro_count * 25}m", "Focus Time", "⏱️")
        
        st.markdown("---")
        st.markdown("### 💡 Tips")
        st.markdown("""
        - 🎯 **Focus**: Avoid distractions during work sessions
        - 📵 **Disconnect**: Put your phone on silent
        - 💧 **Hydrate**: Drink water during breaks
        - 🚶 **Move**: Stretch or walk during breaks
        """)

def page_progress():
    """Progress tracking page"""
    st.markdown("## 📊 Your Progress")
    
    progress = st.session_state.user_progress
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_metric_card(f"{progress.total_study_time}m", "Total Study Time", "⏱️")
    
    with col2:
        render_metric_card(str(progress.total_flashcards_reviewed), "Flashcards Reviewed", "🎴")
    
    with col3:
        render_metric_card(str(progress.total_quizzes_taken), "Quizzes Taken", "❓")
    
    with col4:
        accuracy = (progress.total_quiz_correct / max(progress.total_quizzes_taken * 5, 1)) * 100
        render_metric_card(f"{accuracy:.0f}%", "Quiz Accuracy", "🎯")
    
    st.markdown("---")
    
    # Flashcard mastery
    if st.session_state.flashcards:
        st.markdown("### 🎴 Flashcard Mastery")
        
        mastery_data = {
            "Mastered (>70%)": len([c for c in st.session_state.flashcards if c.mastery_score >= 70]),
            "Learning (40-70%)": len([c for c in st.session_state.flashcards if 40 <= c.mastery_score < 70]),
            "New (<40%)": len([c for c in st.session_state.flashcards if c.mastery_score < 40])
        }
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("✅ Mastered", mastery_data["Mastered (>70%)"])
        with col2:
            st.metric("🔶 Learning", mastery_data["Learning (40-70%)"])
        with col3:
            st.metric("⬜ New", mastery_data["New (<40%)"])
    
    # Study suggestions
    st.markdown("---")
    st.markdown("### 💡 Study Suggestions")
    
    suggestions = []
    
    if progress.total_flashcards_reviewed < 10:
        suggestions.append("📚 Review more flashcards to build your knowledge base")
    
    if progress.total_quizzes_taken < 2:
        suggestions.append("❓ Take more quizzes to test your understanding")
    
    if progress.total_study_time < 25:
        suggestions.append("⏱️ Complete a full Pomodoro session (25 minutes) for better focus")
    
    if st.session_state.flashcards:
        weak_cards = [c for c in st.session_state.flashcards if c.mastery_score < 50]
        if weak_cards:
            suggestions.append(f"🎯 Focus on the {len(weak_cards)} flashcards you're still learning")
    
    if not suggestions:
        suggestions.append("🌟 Great job! Keep up the excellent work!")
    
    for suggestion in suggestions:
        st.info(suggestion)
    
    # Reset progress button
    st.markdown("---")
    if st.button("🗑️ Reset All Progress", type="secondary"):
        st.session_state.user_progress = UserProgress()
        st.session_state.flashcards = []
        st.session_state.quiz_questions = []
        st.session_state.summaries = []
        st.session_state.pomodoro_count = 0
        st.success("Progress reset!")
        st.rerun()

# ============================================================
# MAIN APPLICATION
# ============================================================

def main():
    """Main application entry point"""
    init_session_state()
    render_header()
    
    selected_page = render_sidebar()
    
    # Route to selected page
    if selected_page == "📚 Study Material":
        page_study_material()
    elif selected_page == "🎴 Flashcards":
        page_flashcards()
    elif selected_page == "❓ Quiz Mode":
        page_quiz()
    elif selected_page == "⏱️ Pomodoro Timer":
        page_pomodoro()
    elif selected_page == "📊 Progress":
        page_progress()
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: #6c757d; padding: 1rem;">
            <p>Made with ❤️ using Streamlit & Google Gemini AI</p>
            <p><small>StudyBuddy AI - Learn Smarter, Not Harder 🎓</small></p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
