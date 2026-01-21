"""
🎓 StudyBuddy AI - Your Intelligent Study Companion
An AI-powered study assistant with adaptive quizzing, flashcards, and smart summarization.
Built with Streamlit - Supports Multiple AI Providers (Gemini, Groq) + Demo Mode
"""

import streamlit as st
import json
import time
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable
from enum import Enum
import io
import re

# ============================================================
# PDF SUPPORT (with fallback)
# ============================================================
try:
    import PyPDF2
    PDF_SUPPORTED = True
except ImportError:
    PDF_SUPPORTED = False

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

.stApp {
    font-family: 'Poppins', sans-serif;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

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
}

.main-header p {
    color: rgba(255,255,255,0.9);
    font-size: 1.1rem;
    margin-top: 0.5rem;
}

.feature-card {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    border: 1px solid rgba(0,0,0,0.05);
    transition: all 0.3s ease;
}

.feature-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 30px rgba(102, 126, 234, 0.2);
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

.summary-box {
    background: linear-gradient(145deg, #f8f9ff 0%, #ffffff 100%);
    border-left: 4px solid #667eea;
    border-radius: 0 12px 12px 0;
    padding: 1.5rem;
    margin: 1rem 0;
    color: #333333 !important;
}

.summary-box p, .summary-box li, .summary-box h1, .summary-box h2, .summary-box h3, .summary-box h4, .summary-box strong {
    color: #333333 !important;
}

.eli5-box {
    background: linear-gradient(145deg, #fff9e6 0%, #fff5d6 100%);
    border-left: 4px solid #ffc107;
    border-radius: 0 12px 12px 0;
    padding: 1.5rem;
    margin: 1rem 0;
    color: #333333 !important;
}

.eli5-box p, .eli5-box li, .eli5-box h1, .eli5-box h2, .eli5-box h3, .eli5-box h4, .eli5-box strong {
    color: #333333 !important;
}

/* Fix expander content text color */
.streamlit-expanderContent {
    color: #333333 !important;
}

.streamlit-expanderContent p, .streamlit-expanderContent li, .streamlit-expanderContent strong {
    color: #333333 !important;
}

/* Force all text in expanders to be dark */
[data-testid="stExpander"] {
    background-color: #f8f9ff !important;
}

[data-testid="stExpander"] p,
[data-testid="stExpander"] li,
[data-testid="stExpander"] span,
[data-testid="stExpander"] div {
    color: #1a1a1a !important;
}

/* Expander header styling */
[data-testid="stExpander"] summary {
    color: #333333 !important;
    font-weight: 600;
}

/* Main content area text fix */
.main .block-container {
    color: #1a1a1a;
}

/* Headers visible */
h1, h2, h3, h4, h5, h6 {
    color: #333333 !important;
}

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

.api-status-ok {
    background: #d4edda;
    color: #155724;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    font-size: 0.85rem;
}

.api-status-demo {
    background: #fff3cd;
    color: #856404;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    font-size: 0.85rem;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%) !important;
}

[data-testid="stSidebar"] [data-testid="stMarkdown"] {
    color: #ffffff;
}

[data-testid="stSidebar"] .stRadio label {
    color: #ffffff !important;
}

[data-testid="stSidebar"] .stRadio > div {
    background: rgba(255,255,255,0.1);
    border-radius: 10px;
    padding: 0.5rem;
}

[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stTextInput label {
    color: #ffffff !important;
}

[data-testid="stSidebar"] p, 
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label {
    color: #e0e0e0 !important;
}

[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    width: 100%;
}

[data-testid="stSidebar"] a {
    color: #a0d2ff !important;
}

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
    id: int
    front: str
    back: str
    topic: str
    difficulty: Difficulty = Difficulty.MEDIUM
    times_reviewed: int = 0
    times_correct: int = 0
    
    @property
    def mastery_score(self) -> float:
        if self.times_reviewed == 0:
            return 0
        return (self.times_correct / self.times_reviewed) * 100

@dataclass
class QuizQuestion:
    id: int
    question: str
    options: List[str]
    correct_answer: int
    explanation: str
    topic: str
    difficulty: Difficulty = Difficulty.MEDIUM

@dataclass 
class UserProgress:
    total_study_time: int = 0
    total_flashcards_reviewed: int = 0
    total_quizzes_taken: int = 0
    total_quiz_correct: int = 0
    study_streak: int = 0

# ============================================================
# AI SERVICE - MULTI-PROVIDER SUPPORT
# ============================================================

class AIService:
    """Universal AI Service with multiple provider support and demo fallback"""
    
    def __init__(self):
        self.provider = "demo"
        self.model_name = "Demo Mode"
        self.client = None
        self.is_connected = False
    
    def configure_gemini(self, api_key: str) -> tuple:
        """Configure Google Gemini API"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            
            # Try multiple model names
            models_to_try = [
                'gemini-2.0-flash',
                'gemini-2.5-flash-lite', 
                'gemini-1.5-flash-latest',
                'gemini-1.5-flash',
                'gemini-pro',
            ]
            
            for model_name in models_to_try:
                try:
                    model = genai.GenerativeModel(model_name)
                    # Quick test
                    response = model.generate_content("Say 'OK' if you work")
                    if response and response.text:
                        self.client = model
                        self.provider = "gemini"
                        self.model_name = model_name
                        self.is_connected = True
                        return True, f"✅ Connected to Gemini ({model_name})"
                except Exception as e:
                    continue
            
            # Try to find any available model
            try:
                for m in genai.list_models():
                    if 'generateContent' in str(m.supported_generation_methods):
                        model_name = m.name.replace('models/', '')
                        try:
                            model = genai.GenerativeModel(model_name)
                            response = model.generate_content("Say OK")
                            if response:
                                self.client = model
                                self.provider = "gemini"
                                self.model_name = model_name
                                self.is_connected = True
                                return True, f"✅ Connected to Gemini ({model_name})"
                        except:
                            continue
            except:
                pass
            
            return False, "❌ No working Gemini model found. Using Demo Mode."
            
        except ImportError:
            return False, "❌ google-generativeai not installed. Using Demo Mode."
        except Exception as e:
            return False, f"❌ Gemini error: {str(e)[:50]}. Using Demo Mode."
    
    def configure_openai(self, api_key: str) -> tuple:
        """Configure OpenAI API (Recommended)"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            
            # Test connection
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Say OK"}],
                max_tokens=10
            )
            
            if response.choices[0].message.content:
                self.client = client
                self.provider = "openai"
                self.model_name = "gpt-3.5-turbo"
                self.is_connected = True
                self.api_key = api_key
                return True, "✅ Connected to OpenAI (GPT-3.5 Turbo)"
                
        except ImportError:
            return False, "❌ openai not installed. Run: pip install openai"
        except Exception as e:
            error_msg = str(e)
            if "invalid_api_key" in error_msg.lower() or "incorrect api key" in error_msg.lower():
                return False, "❌ Invalid API key. Please check your OpenAI API key."
            return False, f"❌ OpenAI error: {error_msg[:50]}"
        
        return False, "❌ Could not connect to OpenAI."
    
    def configure_openrouter(self, api_key: str) -> tuple:
        """Configure OpenRouter API"""
        try:
            from openai import OpenAI
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
                default_headers={
                    "HTTP-Referer": "https://studybuddy.streamlit.app",
                    "X-Title": "StudyBuddy AI"
                }
            )
            
            # Models - paid first (better), free as fallback
            models = [
                # Paid - better quality
                "openai/gpt-4o-mini",           # Best value
                "google/gemini-flash-1.5",      # Fast & good
                "anthropic/claude-3-haiku",     # Good structured output
                "openai/gpt-3.5-turbo",         # Reliable
                # Free - fallback
                "google/gemma-2-9b-it:free",
                "meta-llama/llama-3.2-3b-instruct:free",
                "qwen/qwen-2-7b-instruct:free",
            ]
            
            last_error = ""
            for model in models:
                try:
                    response = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "user", "content": "Say 'OK' only"}
                        ],
                        max_tokens=10
                    )
                    
                    if response.choices and response.choices[0].message.content:
                        self.client = client
                        self.provider = "openrouter"
                        self.model_name = model
                        self.is_connected = True
                        short_name = model.split('/')[1].replace(':free', '')
                        is_free = ':free' in model
                        status = "🆓 Free" if is_free else "⚡ Paid"
                        return True, f"✅ Connected: {short_name} ({status})"
                except Exception as e:
                    last_error = str(e)
                    continue
            
            return False, f"❌ No model available. Error: {last_error[:60]}"
                
        except ImportError:
            return False, "❌ openai package not installed."
        except Exception as e:
            return False, f"❌ OpenRouter error: {str(e)[:80]}"
    
    def generate(self, prompt: str) -> str:
        """Generate response from configured AI or demo"""
        if self.provider == "gemini" and self.client:
            try:
                response = self.client.generate_content(prompt)
                return response.text
            except Exception as e:
                return f"Error: {str(e)}"
        
        elif self.provider == "openai" and self.client:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=2000
                )
                return response.choices[0].message.content
            except Exception as e:
                return f"Error: {str(e)}"
        
        elif self.provider == "openrouter" and self.client:
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant. Always respond with valid content."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=2000,
                    temperature=0.7
                )
                content = response.choices[0].message.content
                if content:
                    return content
                else:
                    return "Error: Empty response from AI"
            except Exception as e:
                error_str = str(e)
                # Check for rate limit
                if "rate" in error_str.lower() or "limit" in error_str.lower():
                    return f"Error: Rate limited - wait a moment and try again. ({error_str[:50]})"
                return f"Error: {error_str[:100]}"
        
        # Demo mode - return helpful placeholder
        return None
    
    def summarize(self, content: str, style: str = "detailed") -> str:
        """Summarize content"""
        # Truncate content if too long
        max_content_length = 4000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "...[truncated]"
        
        prompts = {
            "detailed": f"""Summarize this content with clear key points:

{content}

Provide a detailed summary with:
- Overview
- Key Points (as bullet points)
- Main Takeaways""",
            "brief": f"""Give a brief 3-5 sentence summary of this content:

{content}""",
            "eli5": f"""Explain this content like I'm 5 years old. Use simple words, fun examples, and analogies:

{content}"""
        }
        
        result = self.generate(prompts.get(style, prompts["detailed"]))
        
        # Check if result is None or an error
        if result is None or (isinstance(result, str) and result.startswith("Error:")):
            print(f"AI Error in summarize: {result}")
            # Demo mode responses
            if style == "eli5":
                return self._demo_eli5_summary(content)
            elif style == "brief":
                return self._demo_brief_summary(content)
            else:
                return self._demo_detailed_summary(content)
        
        return result
    
    def generate_flashcards(self, content: str, num_cards: int, topic: str) -> List[Dict]:
        """Generate flashcards from content"""
        # Truncate content if too long
        max_content_length = 3000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."
        
        prompt = f"""Buat {num_cards} flashcard untuk belajar berdasarkan materi berikut.

MATERI:
{content}

ATURAN PENTING:
1. Setiap flashcard HARUS punya pertanyaan (front) dan jawaban (back) yang NYAMBUNG
2. Pertanyaan harus JELAS dan SPESIFIK
3. Jawaban harus LANGSUNG menjawab pertanyaan
4. Gunakan bahasa yang sama dengan materi (Indonesia/Inggris)
5. JANGAN mulai jawaban dengan "Namun" atau kata penghubung

CONTOH FORMAT YANG BENAR:
- front: "Apa itu ICC?"
- back: "ICC (International Criminal Court) adalah pengadilan pidana internasional yang bertugas mengadili kejahatan berat seperti genosida."

CONTOH FORMAT YANG SALAH:
- front: "Apa peran ICC?"
- back: "Namun, perkembangan hukum..." (SALAH karena tidak langsung menjawab)

Kembalikan HANYA JSON array:
[
  {{"front": "Pertanyaan spesifik?", "back": "Jawaban langsung dan jelas.", "difficulty": "easy"}},
  {{"front": "Pertanyaan lain?", "back": "Jawaban yang nyambung.", "difficulty": "medium"}}
]

JSON array saja, tanpa teks lain:"""

        result = self.generate(prompt)
        
        # Check if result is None or an error
        if result is None or (isinstance(result, str) and result.startswith("Error:")):
            print(f"AI Error in flashcards: {result}")
            return self._demo_flashcards(content, num_cards, topic)
        
        try:
            # Clean up response
            text = result.strip()
            
            # Remove markdown code blocks
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                parts = text.split("```")
                for part in parts:
                    if "[" in part and "]" in part:
                        text = part
                        break
            
            # Find JSON array
            start = text.find('[')
            end = text.rfind(']') + 1
            if start >= 0 and end > start:
                text = text[start:end]
            
            cards = json.loads(text)
            if isinstance(cards, list) and len(cards) > 0:
                # Validate cards have required fields
                valid_cards = []
                for card in cards:
                    if isinstance(card, dict) and 'front' in card and 'back' in card:
                        if 'difficulty' not in card:
                            card['difficulty'] = 'medium'
                        valid_cards.append(card)
                
                if valid_cards:
                    return valid_cards
                    
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            print(f"Raw text: {result[:300]}")
        except Exception as e:
            print(f"Error parsing flashcards: {e}")
        
        return self._demo_flashcards(content, num_cards, topic)
    
    def generate_quiz(self, content: str, num_questions: int) -> List[Dict]:
        """Generate quiz questions from content"""
        # Truncate content if too long
        max_content_length = 3000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."
            
        prompt = f"""Buat {num_questions} soal pilihan ganda berdasarkan materi berikut.

MATERI:
{content}

ATURAN:
1. Setiap soal harus punya 4 pilihan jawaban (A, B, C, D)
2. Hanya 1 jawaban yang benar
3. Soal harus berdasarkan materi yang diberikan
4. Gunakan bahasa yang sama dengan materi

FORMAT OUTPUT (JSON array saja):
[
  {{
    "question": "Apa yang dimaksud dengan X?",
    "options": ["Jawaban A", "Jawaban B", "Jawaban C", "Jawaban D"],
    "correct_answer": 0,
    "explanation": "Penjelasan mengapa jawaban A benar",
    "difficulty": "easy"
  }}
]

correct_answer adalah index (0=A, 1=B, 2=C, 3=D).

Kembalikan HANYA JSON array:"""

        result = self.generate(prompt)
        
        # Check if result is None or an error
        if result is None or (isinstance(result, str) and result.startswith("Error:")):
            print(f"AI Error in quiz: {result}")
            return self._demo_quiz(content, num_questions)
        
        try:
            text = result.strip()
            if "```" in text:
                text = text.split("```")[1] if "```" in text else text
                text = text.replace("json", "").strip()
            
            start = text.find('[')
            end = text.rfind(']') + 1
            if start >= 0 and end > start:
                text = text[start:end]
            
            questions = json.loads(text)
            if isinstance(questions, list) and len(questions) > 0:
                return questions
        except:
            pass
        
        return self._demo_quiz(content, num_questions)
    
    # Demo mode helpers
    def _demo_detailed_summary(self, content: str) -> str:
        words = content.split()
        word_count = len(words)
        sentences = content.split('.')
        
        return f"""📝 **Summary** (Demo Mode)

**Overview:**
This content contains approximately {word_count} words and covers several important concepts.

**Key Points:**
• The material discusses foundational concepts in the subject area
• Multiple interconnected ideas are presented throughout
• Understanding these concepts is essential for mastery

**Main Takeaways:**
• Focus on understanding the core principles
• Practice applying these concepts regularly
• Review this material periodically for retention

💡 *Connect an AI API for intelligent, content-specific summaries!*"""

    def _demo_brief_summary(self, content: str) -> str:
        word_count = len(content.split())
        return f"""📝 **Brief Summary** (Demo Mode)

This content ({word_count} words) covers important concepts in your study area. The key ideas focus on fundamental principles that build upon each other. Review regularly for best retention.

💡 *Connect an AI API for intelligent summaries!*"""

    def _demo_eli5_summary(self, content: str) -> str:
        return f"""🧒 **Simple Explanation** (Demo Mode)

Imagine you have a big box of LEGO pieces. This content is like the instruction manual that shows you how to build something cool!

Each idea is like a LEGO piece - they all fit together to make something bigger. The more you practice putting them together, the better you get!

🎮 Think of learning like a video game - you start with easy levels and work your way up!

💡 *Connect an AI API for fun, personalized explanations!*"""

    def _demo_flashcards(self, content: str, num_cards: int, topic: str) -> List[Dict]:
        """Generate demo flashcards based on content"""
        words = content.split()
        
        # Extract potential key terms (capitalized words, longer words)
        key_terms = []
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word)
            if len(clean_word) > 5 and clean_word[0].isupper():
                key_terms.append(clean_word)
        
        key_terms = list(set(key_terms))[:num_cards] if key_terms else ["Concept"]
        
        cards = []
        templates = [
            ("What is {term}?", "A key concept in {topic} that relates to the fundamental principles discussed in the material."),
            ("Why is {term} important?", "It plays a crucial role in understanding {topic} and connects to other core concepts."),
            ("How does {term} work?", "It operates based on the principles outlined in the study material for {topic}."),
            ("Define {term}", "An important element of {topic} covered in the study material."),
            ("Explain the role of {term}", "This concept contributes to the overall understanding of {topic}."),
        ]
        
        for i in range(min(num_cards, max(len(key_terms), 5))):
            term = key_terms[i] if i < len(key_terms) else f"Concept {i+1}"
            template = templates[i % len(templates)]
            difficulty = ["easy", "medium", "hard"][i % 3]
            
            cards.append({
                "front": template[0].format(term=term),
                "back": template[1].format(term=term, topic=topic) + "\n\n💡 *Demo mode - connect AI for better flashcards!*",
                "difficulty": difficulty
            })
        
        return cards

    def _demo_quiz(self, content: str, num_questions: int) -> List[Dict]:
        """Generate demo quiz questions"""
        questions = []
        
        templates = [
            {
                "question": "What is the main purpose of studying this material?",
                "options": [
                    "To understand fundamental concepts",
                    "To memorize random facts",
                    "To skip the learning process",
                    "None of the above"
                ],
                "correct_answer": 0,
                "explanation": "Understanding fundamental concepts is key to mastery."
            },
            {
                "question": "Which approach is best for learning this material?",
                "options": [
                    "Cramming the night before",
                    "Regular review and practice",
                    "Only reading once",
                    "Avoiding all practice"
                ],
                "correct_answer": 1,
                "explanation": "Regular review and spaced repetition improve retention."
            },
            {
                "question": "How are the concepts in this material related?",
                "options": [
                    "They are completely unrelated",
                    "They build upon each other",
                    "Only the first concept matters",
                    "They contradict each other"
                ],
                "correct_answer": 1,
                "explanation": "Educational concepts typically build on foundational knowledge."
            },
            {
                "question": "What is the benefit of using flashcards?",
                "options": [
                    "They waste time",
                    "They help with active recall",
                    "They are only for children",
                    "They replace understanding"
                ],
                "correct_answer": 1,
                "explanation": "Flashcards promote active recall, a proven learning technique."
            },
            {
                "question": "Why is self-testing important?",
                "options": [
                    "It identifies knowledge gaps",
                    "It's not important at all",
                    "Only final exams matter",
                    "Testing causes stress only"
                ],
                "correct_answer": 0,
                "explanation": "Self-testing helps identify areas that need more review."
            },
        ]
        
        for i in range(min(num_questions, len(templates))):
            q = templates[i].copy()
            q["difficulty"] = ["easy", "medium", "hard"][i % 3]
            q["explanation"] += "\n\n💡 *Demo mode - connect AI for content-specific questions!*"
            questions.append(q)
        
        return questions

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def extract_text_from_pdf(pdf_file) -> str:
    """Extract text from PDF with fallback"""
    if not PDF_SUPPORTED:
        return "PDF extraction not available. Please paste your text directly."
    
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.read()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip() if text.strip() else "Could not extract text from PDF."
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def get_timer_remaining() -> int:
    """Get remaining seconds on timer"""
    if not st.session_state.get('timer_running', False):
        return st.session_state.get('timer_duration', 25 * 60)
    
    start_time = st.session_state.get('timer_start_time')
    if start_time is None:
        return st.session_state.get('timer_duration', 25 * 60)
    
    elapsed = time.time() - start_time
    remaining = st.session_state.get('timer_duration', 25 * 60) - int(elapsed)
    return max(0, remaining)

def check_timer_complete():
    """Check if timer completed and handle it"""
    if not st.session_state.get('timer_running', False):
        return False
    
    remaining = get_timer_remaining()
    
    if remaining <= 0:
        st.session_state.timer_running = False
        st.session_state.timer_start_time = None
        
        if st.session_state.timer_mode == "work":
            st.session_state.pomodoro_count += 1
            st.session_state.user_progress.total_study_time += 25
            # Switch to break
            st.session_state.timer_mode = "break"
            st.session_state.timer_duration = 5 * 60
            return "work_complete"
        else:
            # Switch to work
            st.session_state.timer_mode = "work"
            st.session_state.timer_duration = 25 * 60
            return "break_complete"
    
    return False

def init_session_state():
    """Initialize all session state variables"""
    defaults = {
        'ai_service': AIService(),
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
        # Timer - timestamp based (works across pages)
        'timer_running': False,
        'timer_start_time': None,  # When timer started
        'timer_duration': 25 * 60,  # Duration in seconds
        'timer_mode': 'work',  # 'work' or 'break'
        'pomodoro_count': 0,
        'summaries': [],
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
        # Custom sidebar header with visible styling
        st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 1rem; border-radius: 12px; margin-bottom: 1rem;">
                <h3 style="color: white; margin: 0; font-size: 1.2rem;">🎯 Navigation</h3>
            </div>
        """, unsafe_allow_html=True)
        
        pages = ["📚 Study Material", "🎴 Flashcards", "❓ Quiz Mode", "⏱️ Pomodoro Timer", "📊 Progress"]
        selected = st.radio("Select Page", pages, label_visibility="collapsed")
        
        # Timer status (visible from all pages)
        if st.session_state.get('timer_running', False):
            remaining = get_timer_remaining()
            timer_status = check_timer_complete()
            
            if timer_status == "work_complete":
                st.success("🎉 Pomodoro selesai! Waktunya istirahat!")
                st.session_state.timer_running = False
            elif timer_status == "break_complete":
                st.info("☕ Break selesai! Siap fokus lagi?")
                st.session_state.timer_running = False
            else:
                mode_icon = "🎯" if st.session_state.timer_mode == "work" else "☕"
                mode_text = "Focus" if st.session_state.timer_mode == "work" else "Break"
                st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                                padding: 0.6rem; border-radius: 8px; margin: 0.5rem 0; text-align: center;">
                        <span style="color: white; font-weight: bold;">
                            {mode_icon} {mode_text}: {format_time(remaining)}
                        </span>
                    </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # API Configuration with visible header
        st.markdown("""
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                        padding: 0.8rem; border-radius: 10px; margin-bottom: 1rem;">
                <h4 style="color: white; margin: 0; font-size: 1rem;">🔑 AI Configuration</h4>
            </div>
        """, unsafe_allow_html=True)
        
        ai_service = st.session_state.ai_service
        
        # Show current status with clear indicator
        if ai_service.is_connected:
            st.success(f"✅ Connected: {ai_service.provider.upper()}")
            st.caption(f"Model: {ai_service.model_name}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🧪 Test AI", use_container_width=True):
                    with st.spinner("Testing AI..."):
                        test_prompt = "Generate a simple flashcard about cats in JSON format: {\"front\": \"question\", \"back\": \"answer\"}"
                        result = ai_service.generate(test_prompt)
                        
                        if result is None:
                            st.error("❌ AI returned None - not connected properly")
                        elif result.startswith("Error:"):
                            st.error(f"❌ {result}")
                        else:
                            st.success("✅ AI is working!")
                            with st.expander("Response preview"):
                                st.code(result[:500])
            with col2:
                if st.button("🔄 Disconnect", use_container_width=True):
                    st.session_state.ai_service = AIService()
                    st.rerun()
        else:
            st.warning("🎮 Demo Mode - Connect API for AI features")
            
            # Provider selection - OpenRouter recommended
            provider = st.selectbox(
                "Select AI Provider",
                ["OpenRouter (Recommended)", "Google Gemini", "OpenAI"],
                key="provider_select"
            )
            
            if provider == "OpenRouter (Recommended)":
                st.markdown('<small style="color: #28a745;">⭐ GPT-4o-mini, Gemini, Claude + Free fallback</small>', unsafe_allow_html=True)
                openrouter_key = st.text_input(
                    "OpenRouter API Key", 
                    type="password", 
                    key="input_openrouter_key",
                    placeholder="sk-or-v1-..."
                )
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    connect_btn = st.button("🚀 Connect", use_container_width=True, type="primary")
                with col2:
                    st.link_button("🔑", "https://openrouter.ai/settings/keys")
                
                if connect_btn:
                    if openrouter_key and openrouter_key.startswith("sk-or-"):
                        with st.spinner("Connecting to OpenRouter..."):
                            success, message = ai_service.configure_openrouter(openrouter_key)
                            if success:
                                st.session_state.ai_service = ai_service
                                st.success(message)
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(message)
                    else:
                        st.error("Please enter a valid OpenRouter API key (starts with 'sk-or-')")
            
            elif provider == "Google Gemini":
                gemini_key = st.text_input(
                    "Gemini API Key", 
                    type="password", 
                    key="input_gemini_key",
                    placeholder="AIza..."
                )
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    connect_btn = st.button("🔗 Connect", use_container_width=True)
                with col2:
                    st.link_button("🔑", "https://aistudio.google.com/apikey")
                
                if connect_btn:
                    if gemini_key and len(gemini_key) > 10:
                        with st.spinner("Connecting to Gemini..."):
                            success, message = ai_service.configure_gemini(gemini_key)
                            if success:
                                st.session_state.ai_service = ai_service
                                st.success(message)
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(message)
                    else:
                        st.error("Please enter a valid Gemini API key")
                        
            else:  # OpenAI
                st.markdown('<small style="color: #666;">💰 Paid API - requires credit</small>', unsafe_allow_html=True)
                openai_key = st.text_input(
                    "OpenAI API Key", 
                    type="password", 
                    key="input_openai_key",
                    placeholder="sk-..."
                )
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    connect_btn = st.button("🔗 Connect", use_container_width=True)
                with col2:
                    st.link_button("🔑", "https://platform.openai.com/api-keys")
                
                if connect_btn:
                    if openai_key and openai_key.startswith("sk-"):
                        with st.spinner("Connecting to OpenAI..."):
                            success, message = ai_service.configure_openai(openai_key)
                            if success:
                                st.session_state.ai_service = ai_service
                                st.success(message)
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(message)
                    else:
                        st.error("Please enter a valid OpenAI API key (starts with 'sk-')")
        
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
    """Study Material page"""
    st.markdown("## 📚 Study Material")
    st.markdown("Upload your study materials and let AI help you learn effectively.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        topic = st.text_input(
            "📌 Topic Name",
            value=st.session_state.topic,
            placeholder="e.g., Machine Learning, History, etc."
        )
        st.session_state.topic = topic
        
        tab1, tab2 = st.tabs(["📝 Paste Text", "📄 Upload PDF"])
        
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
            if PDF_SUPPORTED:
                uploaded_file = st.file_uploader("Upload PDF", type=['pdf'])
                if uploaded_file:
                    with st.spinner("📖 Extracting text..."):
                        extracted_text = extract_text_from_pdf(uploaded_file)
                        st.session_state.content = extracted_text
                        st.success(f"✅ Extracted {len(extracted_text)} characters")
                        with st.expander("Preview"):
                            st.text(extracted_text[:1500] + "..." if len(extracted_text) > 1500 else extracted_text)
            else:
                st.warning("📦 Install PyPDF2 for PDF support: `pip install PyPDF2`")
    
    with col2:
        st.markdown("### ⚡ Quick Actions")
        
        if st.session_state.content:
            st.markdown("#### 📝 Summarize")
            summary_style = st.radio(
                "Style",
                ["detailed", "brief", "eli5"],
                format_func=lambda x: {"detailed": "📚 Detailed", "brief": "⚡ Brief", "eli5": "👶 ELI5"}[x],
                horizontal=True
            )
            
            if st.button("🪄 Generate Summary", use_container_width=True):
                with st.spinner("Creating summary..."):
                    summary = st.session_state.ai_service.summarize(
                        st.session_state.content,
                        summary_style
                    )
                    st.session_state.summaries.append(summary)
                    st.rerun()
            
            st.markdown("---")
            
            st.markdown("#### 🎴 Flashcards")
            num_cards = st.slider("Number of cards", 3, 15, 8)
            
            if st.button("🎴 Generate Flashcards", use_container_width=True):
                ai_service = st.session_state.ai_service
                source_name = ai_service.model_name if ai_service.is_connected else "Demo"
                
                with st.spinner(f"Creating flashcards with {source_name}..."):
                    # First test if AI is working
                    if ai_service.is_connected:
                        test_result = ai_service.generate("Say OK")
                        if test_result is None or test_result.startswith("Error:"):
                            st.error(f"⚠️ AI Error: {test_result}. Using Demo Mode instead.")
                            ai_service.is_connected = False  # Temporarily use demo
                    
                    cards_data = ai_service.generate_flashcards(
                        st.session_state.content,
                        num_cards,
                        st.session_state.topic
                    )
                    
                    # Check if we got demo cards (they have the demo message)
                    is_demo = any("Demo mode" in str(card.get('back', '')) for card in cards_data)
                    
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
                    st.session_state.current_card_index = 0
                    
                    # Show what happened
                    if is_demo:
                        st.warning(f"⚠️ Created {len(flashcards)} flashcards in DEMO mode. AI might have failed - try Test AI button.")
                    else:
                        st.success(f"✅ Created {len(flashcards)} flashcards with AI! ({source_name})")
            
            st.markdown("---")
            
            st.markdown("#### ❓ Quiz")
            num_questions = st.slider("Number of questions", 3, 10, 5)
            
            if st.button("❓ Generate Quiz", use_container_width=True):
                with st.spinner("Creating quiz..."):
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
                    st.success(f"✅ Created {len(quiz_questions)} questions!")
        else:
            st.info("📝 Add study content to get started")
    
    # Display summaries
    if st.session_state.summaries:
        st.markdown("---")
        st.markdown('<h3 style="color: #667eea;">📋 Generated Summaries</h3>', unsafe_allow_html=True)
        
        for i, summary in enumerate(reversed(st.session_state.summaries[-3:])):
            with st.expander(f"Summary {len(st.session_state.summaries) - i}", expanded=(i == 0)):
                # Display with forced dark text color
                st.markdown(f'<div style="color: #1a1a1a !important;">', unsafe_allow_html=True)
                st.write(summary)
                st.markdown('</div>', unsafe_allow_html=True)

def page_flashcards():
    """Flashcards page"""
    st.markdown("## 🎴 Flashcards")
    
    if not st.session_state.flashcards:
        st.info("📝 No flashcards yet! Go to Study Material to generate some.")
        return
    
    cards = st.session_state.flashcards
    current_idx = st.session_state.current_card_index
    current_card = cards[current_idx]
    
    # Progress
    progress = (current_idx + 1) / len(cards)
    st.markdown(f"""
        <div class="progress-container">
            <div class="progress-bar" style="width: {progress * 100}%"></div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"**Card {current_idx + 1} of {len(cards)}** • Topic: `{current_card.topic}` • Difficulty: `{current_card.difficulty.value}`")
    
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        if st.session_state.show_answer:
            st.markdown(f"""
                <div class="flashcard flashcard-back">
                    <div>
                        <small style="opacity: 0.8;">ANSWER</small>
                        <h3>{current_card.back}</h3>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="flashcard flashcard-front">
                    <div>
                        <small style="opacity: 0.8;">QUESTION</small>
                        <h3>{current_card.front}</h3>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
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
                st.session_state.user_progress.total_flashcards_reviewed += 1
                st.rerun()
        
        if st.session_state.show_answer:
            st.markdown("---")
            st.markdown("**How well did you know this?**")
            
            acol1, acol2, acol3 = st.columns(3)
            
            with acol1:
                if st.button("😕 Learning", use_container_width=True):
                    current_card.times_reviewed += 1
                    st.session_state.user_progress.total_flashcards_reviewed += 1
                    st.session_state.show_answer = False
                    if current_idx < len(cards) - 1:
                        st.session_state.current_card_index += 1
                    st.rerun()
            
            with acol2:
                if st.button("🤔 Almost", use_container_width=True):
                    current_card.times_reviewed += 1
                    current_card.times_correct += 0.5
                    st.session_state.user_progress.total_flashcards_reviewed += 1
                    st.session_state.show_answer = False
                    if current_idx < len(cards) - 1:
                        st.session_state.current_card_index += 1
                    st.rerun()
            
            with acol3:
                if st.button("😎 Got It!", use_container_width=True):
                    current_card.times_reviewed += 1
                    current_card.times_correct += 1
                    st.session_state.user_progress.total_flashcards_reviewed += 1
                    st.session_state.show_answer = False
                    if current_idx < len(cards) - 1:
                        st.session_state.current_card_index += 1
                    st.rerun()
    
    # Card navigation
    st.markdown("---")
    st.markdown("### 📑 All Cards")
    
    card_cols = st.columns(min(len(cards), 8))
    for i, card in enumerate(cards):
        with card_cols[i % len(card_cols)]:
            mastery = card.mastery_score
            icon = '✅' if mastery >= 70 else '🔶' if mastery >= 40 else '⬜'
            if st.button(f"{icon} {i+1}", key=f"nav_{i}", use_container_width=True):
                st.session_state.current_card_index = i
                st.session_state.show_answer = False
                st.rerun()

def page_quiz():
    """Quiz page"""
    st.markdown("## ❓ Quiz Mode")
    
    if not st.session_state.quiz_questions:
        st.info("📝 No quiz yet! Go to Study Material to generate one.")
        return
    
    questions = st.session_state.quiz_questions
    
    if not st.session_state.quiz_submitted:
        answered = sum(1 for a in st.session_state.quiz_answers if a is not None)
        progress = answered / len(questions)
        
        st.markdown(f"""
            <div class="progress-container">
                <div class="progress-bar" style="width: {progress * 100}%"></div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"**Progress: {answered}/{len(questions)} answered**")
        
        for i, question in enumerate(questions):
            with st.container():
                st.markdown(f"""
                    <div class="feature-card">
                        <span class="topic-tag">{question.topic}</span>
                        <span class="topic-tag" style="background: #6c757d;">{question.difficulty.value}</span>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"**Question {i+1}:** {question.question}")
                
                current_answer = st.session_state.quiz_answers[i]
                answer = st.radio(
                    f"Select answer for Q{i+1}",
                    options=range(len(question.options)),
                    format_func=lambda x, q=question: f"{chr(65+x)}. {q.options[x]}",
                    key=f"quiz_{i}",
                    index=current_answer if current_answer is not None else None,
                    label_visibility="collapsed"
                )
                
                if answer is not None:
                    st.session_state.quiz_answers[i] = answer
                
                st.markdown("---")
        
        if st.button("📊 Submit Quiz", use_container_width=True, type="primary"):
            if None in st.session_state.quiz_answers:
                st.warning("⚠️ Please answer all questions!")
            else:
                st.session_state.quiz_submitted = True
                correct = sum(1 for i, q in enumerate(questions) 
                            if st.session_state.quiz_answers[i] == q.correct_answer)
                st.session_state.user_progress.total_quizzes_taken += 1
                st.session_state.user_progress.total_quiz_correct += correct
                st.rerun()
    
    else:
        # Results
        correct_count = sum(1 for i, q in enumerate(questions) 
                          if st.session_state.quiz_answers[i] == q.correct_answer)
        score = (correct_count / len(questions)) * 100
        
        emoji = "🏆" if score >= 80 else "👍" if score >= 60 else "💪"
        message = "Excellent!" if score >= 80 else "Good job!" if score >= 60 else "Keep practicing!"
        color = "#28a745" if score >= 80 else "#ffc107" if score >= 60 else "#dc3545"
        
        st.markdown(f"""
            <div style="text-align: center; padding: 2rem; background: #f8f9ff; border-radius: 20px; margin-bottom: 2rem;">
                <div style="font-size: 4rem;">{emoji}</div>
                <h2 style="color: {color};">{score:.0f}%</h2>
                <p>{correct_count}/{len(questions)} correct • {message}</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📋 Review")
        
        for i, question in enumerate(questions):
            user_answer = st.session_state.quiz_answers[i]
            is_correct = user_answer == question.correct_answer
            
            with st.expander(f"{'✅' if is_correct else '❌'} Q{i+1}: {question.question[:50]}...", expanded=not is_correct):
                st.markdown(f"**Question:** {question.question}")
                
                for j, option in enumerate(question.options):
                    if j == question.correct_answer:
                        st.markdown(f"✅ **{chr(65+j)}. {option}** (Correct)")
                    elif j == user_answer and not is_correct:
                        st.markdown(f"❌ ~~{chr(65+j)}. {option}~~ (Your answer)")
                    else:
                        st.markdown(f"⬜ {chr(65+j)}. {option}")
                
                st.info(f"**Explanation:** {question.explanation}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Retake", use_container_width=True):
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
    st.markdown("Stay focused: 25 min work → 5 min break")
    
    # Check if timer completed
    timer_status = check_timer_complete()
    if timer_status == "work_complete":
        st.balloons()
        st.success("🎉 Pomodoro complete! Time for a break!")
    elif timer_status == "break_complete":
        st.info("☕ Break over! Ready to focus?")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        timer_class = "timer-work" if st.session_state.timer_mode == "work" else "timer-break"
        mode_text = "🎯 FOCUS TIME" if st.session_state.timer_mode == "work" else "☕ BREAK TIME"
        
        remaining = get_timer_remaining()
        
        st.markdown(f"""
            <div class="timer-display {timer_class}">
                <div style="font-size: 1rem; margin-bottom: 0.5rem;">{mode_text}</div>
                {format_time(remaining)}
            </div>
        """, unsafe_allow_html=True)
        
        bcol1, bcol2, bcol3, bcol4 = st.columns(4)
        
        with bcol1:
            if st.session_state.timer_running:
                if st.button("⏸️ Pause", use_container_width=True):
                    # Save remaining time as new duration
                    st.session_state.timer_duration = get_timer_remaining()
                    st.session_state.timer_running = False
                    st.session_state.timer_start_time = None
                    st.rerun()
            else:
                if st.button("▶️ Start", use_container_width=True):
                    st.session_state.timer_running = True
                    st.session_state.timer_start_time = time.time()
                    st.rerun()
        
        with bcol2:
            if st.button("🔄 Reset", use_container_width=True):
                st.session_state.timer_duration = 25 * 60 if st.session_state.timer_mode == "work" else 5 * 60
                st.session_state.timer_running = False
                st.session_state.timer_start_time = None
                st.rerun()
        
        with bcol3:
            if st.button("🎯 Work", use_container_width=True):
                st.session_state.timer_mode = "work"
                st.session_state.timer_duration = 25 * 60
                st.session_state.timer_running = False
                st.session_state.timer_start_time = None
                st.rerun()
        
        with bcol4:
            if st.button("☕ Break", use_container_width=True):
                st.session_state.timer_mode = "break"
                st.session_state.timer_duration = 5 * 60
                st.session_state.timer_running = False
                st.session_state.timer_start_time = None
                st.rerun()
        
        # Auto-refresh when timer is running
        if st.session_state.timer_running:
            time.sleep(1)
            st.rerun()
    
    with col2:
        st.markdown("### 📊 Today")
        render_metric_card(str(st.session_state.pomodoro_count), "Pomodoros", "🍅")
        st.markdown("<br>", unsafe_allow_html=True)
        render_metric_card(f"{st.session_state.pomodoro_count * 25}m", "Focus Time", "⏱️")
        
        st.markdown("---")
        st.markdown("### 💡 Tips")
        st.markdown("""
        - 🎯 Focus fully during work
        - 📵 Silence notifications
        - 💧 Hydrate on breaks
        - 🚶 Move during breaks
        """)

def page_progress():
    """Progress page"""
    st.markdown("## 📊 Your Progress")
    
    progress = st.session_state.user_progress
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_metric_card(f"{progress.total_study_time}m", "Study Time", "⏱️")
    
    with col2:
        render_metric_card(str(progress.total_flashcards_reviewed), "Cards Reviewed", "🎴")
    
    with col3:
        render_metric_card(str(progress.total_quizzes_taken), "Quizzes Taken", "❓")
    
    with col4:
        accuracy = (progress.total_quiz_correct / max(progress.total_quizzes_taken * 5, 1)) * 100
        render_metric_card(f"{accuracy:.0f}%", "Quiz Accuracy", "🎯")
    
    st.markdown("---")
    
    if st.session_state.flashcards:
        st.markdown("### 🎴 Flashcard Mastery")
        
        mastered = len([c for c in st.session_state.flashcards if c.mastery_score >= 70])
        learning = len([c for c in st.session_state.flashcards if 40 <= c.mastery_score < 70])
        new_cards = len([c for c in st.session_state.flashcards if c.mastery_score < 40])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("✅ Mastered", mastered)
        with col2:
            st.metric("🔶 Learning", learning)
        with col3:
            st.metric("⬜ New", new_cards)
    
    st.markdown("---")
    
    if st.button("🗑️ Reset All Progress"):
        st.session_state.user_progress = UserProgress()
        st.session_state.flashcards = []
        st.session_state.quiz_questions = []
        st.session_state.summaries = []
        st.session_state.pomodoro_count = 0
        st.success("Progress reset!")
        st.rerun()

# ============================================================
# MAIN
# ============================================================

def main():
    init_session_state()
    render_header()
    
    selected_page = render_sidebar()
    
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
    
    # Auto-refresh sidebar timer display when timer is running (every 5 seconds on non-pomodoro pages)
    if st.session_state.get('timer_running', False) and selected_page != "⏱️ Pomodoro Timer":
        # Check for completion
        timer_status = check_timer_complete()
        if timer_status:
            st.rerun()
        else:
            # Refresh every 5 seconds to update sidebar timer display
            time.sleep(5)
            st.rerun()
    
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: #6c757d; padding: 1rem;">
            <p>Made with ❤️ using Streamlit</p>
            <p><small>StudyBuddy AI v2.0 - Learn Smarter 🎓</small></p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
