import streamlit as st
import google.generativeai as genai
import re
import os

# ====================================================================
# 🔑 API KEY CONFIGURATION
# ====================================================================
# Replace "abc-123" with your actual Google API key
# Get your API key from: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY = "AIzaSyC35mil4vDAAmBkEVFVGyY8XEA5qGP3HSs"
# ====================================================================

# Set page configuration
st.set_page_config(
    page_title="AI Answer Grader",
    page_icon="📝",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 20px 0;
        color: #1f77b4;
    }
    .grade-display {
        font-size: 2.5em;
        font-weight: bold;
        text-align: center;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
    }
    .grade-excellent {
        background-color: #d4edda;
        color: #155724;
        border: 2px solid #c3e6cb;
    }
    .grade-good {
        background-color: #d1ecf1;
        color: #0c5460;
        border: 2px solid #b8daff;
    }
    .grade-average {
        background-color: #fff3cd;
        color: #856404;
        border: 2px solid #ffeaa7;
    }
    .grade-poor {
        background-color: #f8d7da;
        color: #721c24;
        border: 2px solid #f5c6cb;
    }
    .feedback-box {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin: 10px 0;
    }
    .info-box {
        background-color: #e7f3ff;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #2196F3;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

def grade_answer(question, answer, api_key):
    """Grade an answer using Gemini API"""
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Try different model names
        model_names = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro', 'gemini-1.0-pro']
        model = None
        
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                # Test the model
                test_response = model.generate_content("Say hello")
                if test_response.text:
                    break
            except:
                continue
        
        if not model:
            return {"grade": 0, "feedback": "Could not connect to any Gemini model"}
        
        # Create grading prompt
        prompt = f"""
        You are an expert grader. Please evaluate this answer based on the given question.

        QUESTION:
        {question}

        STUDENT'S ANSWER:
        {answer}

        Please grade this answer on a scale of 0-10 based on:
        1. Accuracy and correctness
        2. Completeness of the answer
        3. Clarity and organization
        4. Relevance to the question
        5. Depth of understanding

        IMPORTANT: Please provide your response in this exact format:
        GRADE: [number from 0-10]
        FEEDBACK: [Your detailed feedback explaining the grade]

        Be fair but thorough in your evaluation.
        """
        
        # Generate response
        response = model.generate_content(prompt)
        
        if response.text:
            return parse_response(response.text)
        else:
            return {"grade": 0, "feedback": "No response from AI model"}
            
    except Exception as e:
        return {"grade": 0, "feedback": f"Error: {str(e)}"}

def parse_response(response_text):
    """Parse the AI response to extract grade and feedback"""
    try:
        # Extract grade
        grade_match = re.search(r'GRADE:\s*(\d+(?:\.\d+)?)', response_text, re.IGNORECASE)
        if grade_match:
            grade = float(grade_match.group(1))
            grade = max(0, min(10, int(round(grade))))
        else:
            # Try to find any number that could be a grade
            numbers = re.findall(r'\b(\d+(?:\.\d+)?)\b', response_text)
            grade = 5  # default
            for num in numbers:
                num_val = float(num)
                if 0 <= num_val <= 10:
                    grade = int(round(num_val))
                    break
        
        # Extract feedback
        feedback_match = re.search(r'FEEDBACK:\s*(.*)', response_text, re.IGNORECASE | re.DOTALL)
        if feedback_match:
            feedback = feedback_match.group(1).strip()
        else:
            feedback = response_text.strip()
        
        return {"grade": grade, "feedback": feedback}
        
    except Exception as e:
        return {"grade": 5, "feedback": f"Error parsing response: {str(e)}\n\nRaw response: {response_text}"}

def get_grade_class(grade):
    """Return CSS class based on grade"""
    if grade >= 8:
        return "grade-excellent"
    elif grade >= 6:
        return "grade-good"
    elif grade >= 4:
        return "grade-average"
    else:
        return "grade-poor"

def get_grade_emoji(grade):
    """Return emoji based on grade"""
    if grade >= 9:
        return "🏆"
    elif grade >= 8:
        return "🌟"
    elif grade >= 6:
        return "👍"
    elif grade >= 4:
        return "👌"
    else:
        return "📚"

def main():
    # Header
    st.markdown("<h1 class='main-header'>🤖 AI Answer Grader with Gemini</h1>", 
                unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key (hardcoded in codebase)
        api_key = GOOGLE_API_KEY  # Using the API key from top of file
        
        st.markdown(f"""
        <div style="background-color: #d4edda; padding: 10px; border-radius: 5px; border-left: 4px solid #28a745;">
            <strong>✅ API Key Configured</strong><br>
            Using built-in API key: <code>{api_key}</code>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Instructions
        st.header("📋 How to Use")
        st.markdown("""
        1. ✅ API key is already configured
        2. Input the question in the first text area
        3. Input the answer in the second text area
        4. Click 'Grade Answer' to get your score
        5. Review the detailed feedback
        """)
        
        st.markdown("---")
        
        # Grading criteria
        st.header("📊 Grading Criteria")
        st.markdown("""
        **Scores are based on:**
        - Accuracy & Correctness
        - Completeness
        - Clarity & Organization
        - Relevance
        - Depth of Understanding
        """)
        
        st.markdown("---")
        
        # API key link
        st.markdown(f"""
        **API Key Status:**
        
        ✅ Using hardcoded API key: `{GOOGLE_API_KEY}`
        
        To change the API key, modify `GOOGLE_API_KEY` at the top of `gemini_grader.py`
        """)
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Question input
        st.header("❓ Question")
        question = st.text_area(
            "Enter the question here:",
            height=150,
            placeholder="Example: What is the capital of France and what are its major landmarks?",
            help="Enter the question that needs to be answered"
        )
        
        # Answer input
        st.header("✍️ Answer")
        answer = st.text_area(
            "Enter the answer here:",
            height=200,
            placeholder="Example: The capital of France is Paris. Some major landmarks include the Eiffel Tower, Louvre Museum, and Notre-Dame Cathedral...",
            help="Enter the answer that needs to be graded"
        )
        
        # Grade button
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        with col_btn2:
            grade_button = st.button(
                "🎯 Grade Answer",
                use_container_width=True,
                type="primary"
            )
    
    with col2:
        # Results area
        st.header("📈 Results")
        
        # API key is always available now
        if 'last_result' in st.session_state:
            result = st.session_state.last_result
            grade = result['grade']
            feedback = result['feedback']
            
            # Display grade
            grade_class = get_grade_class(grade)
            grade_emoji = get_grade_emoji(grade)
            
            st.markdown(f"""
            <div class="grade-display {grade_class}">
                {grade_emoji} {grade}/10
            </div>
            """, unsafe_allow_html=True)
            
            # Display feedback
            st.markdown(f"""
            <div class="feedback-box">
                <strong>📝 Detailed Feedback:</strong><br>
                {feedback}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="info-box">
                <strong>🚀 Ready to Grade!</strong><br>
                Enter a question and answer, then click "Grade Answer" to see results here.
            </div>
            """, unsafe_allow_html=True)
    
    # Process grading
    if grade_button:
        if not question.strip():
            st.error("❌ Please enter a question!")
        elif not answer.strip():
            st.error("❌ Please enter an answer!")
        else:
            with st.spinner("🤔 AI is analyzing the answer..."):
                result = grade_answer(question, answer, api_key)
                st.session_state.last_result = result
                
                if result['grade'] > 0:
                    st.success("✅ Answer graded successfully!")
                else:
                    st.error("❌ " + result['feedback'])
                
                st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9em;'>
        Built with ❤️ using Streamlit and Google Gemini AI<br>
        <em>Powered by AI for intelligent answer evaluation</em>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
