import gradio as gr
import google.generativeai as genai


class InterviewSimulator:
    def __init__(self, api_key):
        # Gemini API Configuration
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

        # Initialize session states
        self.state = {
            "boss_type": None,
            "job_role": None,
            "questions": [],
            "current_question": 0,
            "feedback": [],
            "interview_complete": False
        }

        # Animated emoji avatars for different boss types
        self.avatars = {
            "Calm": """<div class="emoji-avatar calm">
                <div class="emoji">😌</div>
                <div class="ripple"></div>
            </div>""",

            "Strict": """<div class="emoji-avatar strict">
                <div class="emoji">😠</div>
                <div class="ripple"></div>
            </div>""",

            "Neutral": """<div class="emoji-avatar neutral">
                <div class="emoji">😐</div>
                <div class="ripple"></div>
            </div>"""
        }

    def generate_questions(self, boss_type, job_role):
        """Generate interview questions based on the boss type and job role."""
        prompt = f"""Generate 5 professional interview questions for a {job_role} position. 
        The interviewer has a {boss_type} personality. 
        Include a mix of technical and behavioral questions.
        Format: Return only the questions numbered 1-5."""

        response = self.model.generate_content(prompt)
        questions = [q.strip() for q in response.text.split('\n') if q.strip()]

        # Add introduction as the first question
        self.state["questions"] = ["Tell me about yourself."] + questions
        self.state["current_question"] = 0
        self.state["feedback"] = []
        self.state["interview_complete"] = False

        return "Interview questions generated! Ready to begin."

    def evaluate_answer(self, question, answer):
        """Evaluate the user's answer to a question."""
        prompt = f"""Evaluate this interview response:
        Question: {question}
        Answer: {answer}

        Provide feedback in the following format:

        **Communication Score (1-10):** Provide a score (1-10)
        **Content Score (1-10):** Provide a score (1-10)
        **Overall Feedback:** Provide 2-3 sentences of constructive feedback.
        **Improvement Suggestions:** List specific suggestions for improvement.
        """

        response = self.model.generate_content(prompt)
        self.state["feedback"].append(response.text)

        return response.text

    def next_question(self):
        """Move to the next question if available."""
        self.state["current_question"] += 1

        if self.state["current_question"] >= len(self.state["questions"]):
            self.state["interview_complete"] = True

        return "Proceeding to the next question."

    def get_current_question(self):
        """Retrieve the current question or indicate completion."""
        if self.state["interview_complete"]:
            return "Interview Complete! Click 'Finish Interview' to see final feedback."

        question_num = self.state["current_question"] + 1
        total_questions = len(self.state["questions"])
        current_question = self.state["questions"][self.state["current_question"]]

        return f"**Question {question_num}/{total_questions}:** {current_question}"

    def get_final_feedback(self):
        """Provide final feedback summary."""
        combined_feedback = "\n".join(self.state["feedback"])

        prompt = f"""Analyze the following interview feedback and provide:

        **Overall Performance Summary:** Provide a summary of the candidate's overall performance.
        **Key Strengths:** List the candidate's key strengths demonstrated during the interview.
        **Areas for Improvement:** Identify areas where the candidate could improve.
        **Career Path Recommendations:** Suggest potential career paths based on the interview performance.

        Feedback: {combined_feedback}"""

        response = self.model.generate_content(prompt)

        return response.text


# Initialize the simulator
api_key = "AIzaSyBReuQ0vm_xuYG-0BAHFOZV701OeBiYCDs"
simulator = InterviewSimulator(api_key)


# Define Gradio interface functions
def start_interview(boss_type, job_role):
    simulator.state["boss_type"] = boss_type
    simulator.state["job_role"] = job_role
    simulator.generate_questions(boss_type, job_role)

    return (
        "Interview started! Ready for your first question.",
        simulator.get_current_question(),
        "",
        gr.update(visible=True),
        gr.update(visible=False),
        gr.update(visible=True)
    )


def ask_question():
    if simulator.state["current_question"] < len(simulator.state["questions"]):
        return simulator.get_current_question()

    return "Interview Complete!"


def submit_answer(answer):
    if simulator.state["current_question"] < len(simulator.state["questions"]):
        question = simulator.state["questions"][simulator.state["current_question"]]
        feedback = simulator.evaluate_answer(question, answer)

        return feedback, gr.update(visible=True)

    return "Interview is already complete. Click 'Finish Interview' to see final feedback.", gr.update(visible=True)


def next_question():
    simulator.next_question()

    return simulator.get_current_question(), "", gr.update(visible=False)


def clear_feedback_and_answer():
    return "", ""


def finish_interview():
    final_feedback = simulator.get_final_feedback()

    return final_feedback, gr.update(visible=True)


def update_interviewer_avatar(boss_type):
    if not boss_type:
        return None

    avatar_html = simulator.avatars.get(boss_type, "")

    return avatar_html


# Build the Gradio interface
with gr.Blocks(css="""
    /* Base Styles and Variables */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        /* Color Variables */
        --primary-gradient: linear-gradient(135deg, #FF4A99, #9A4DFF);
        --secondary-gradient: linear-gradient(135deg, #00C2FF, #6D28D9);
        --accent-color: #00FFC6;
        --dark-bg: #121212;
        --card-bg: #1E1E1E;
        --text-primary: #FFFFFF;
        --text-secondary: #ADADAD;
        --success-green: #00F5A0;
        --warning-yellow: #FFD600;

        /* Shadow Variables */
        --shadow-neon: 0 0 15px rgba(154, 77, 255, 0.5);
        --card-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);

        /* Border Radius Variables */
        --border-radius-lg: 20px;
        --border-radius-md: 12px;
        --border-radius-sm: 8px;

        /* Spacing Variables */
        --spacing-xs: 4px;
        --spacing-sm: 8px;
        --spacing-md: 16px;
        --spacing-lg: 24px;
        --spacing-xl: 32px;
        --spacing-xxl: 48px;
    }

    /* Reset and Base Layout */
    * {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
    }

    body, .gradio-container, .gradio-container > div {
        font-family: 'Poppins', sans-serif;
        background-color: var(--dark-bg);
        color: var(--text-primary);
        max-width: 100%;
        width: 100%;
        margin: 0;
        padding: 0;
    }

    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }

    ::-webkit-scrollbar-track {
        background: #1E1E1E;
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb {
        background: #3D3D3D;
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #9A4DFF;
    }

    /* Ensure content is scrollable */
    html, body {
        height: 100%;
        overflow-y: auto;
    }

    .gradio-container {
        height: 100%;
        overflow-y: auto;
        padding-bottom: var(--spacing-xxl);
    }

    .container {
        max-width: 1000px;
        margin: 0 auto;
        padding: var(--spacing-xl);
        overflow-y: auto;
    }

    /* Header Styling */
    .header {
        text-align: center;
        padding: var(--spacing-xxl) 0;
        position: relative;
        margin-bottom: var(--spacing-xl);
    }

    .header h1 {
        font-family: 'Inter', sans-serif;
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: var(--spacing-lg);
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: var(--shadow-neon);
        letter-spacing: -1px;
        line-height: 1.1;
    }

    .header h3 {
        font-family: 'Inter', sans-serif;
        font-size: 1.5rem;
        font-weight: 500;
        color: var(--text-secondary);
        margin-bottom: var(--spacing-lg);
    }

    /* Card Styling */
    .card {
        background-color: var(--card-bg);
        border-radius: var(--border-radius-lg);
        padding: var(--spacing-xl);
        box-shadow: var(--card-shadow);
        margin-bottom: var(--spacing-xl);
        border: 1px solid rgba(154, 77, 255, 0.2);
        position: relative;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        max-height: 90vh;
        overflow-y: auto;
    }

    .card:hover {
        transform: translateY(-3px);
        box-shadow: var(--shadow-neon), var(--card-shadow);
    }

    .card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: var(--primary-gradient);
        border-radius: var(--border-radius-lg) var(--border-radius-lg) 0 0;
    }

    /* Radio/Selection Styling */
    .gradio-radio {
        margin-bottom: var(--spacing-xl);
    }

    .gradio-radio label {
        background-color: #2D2D2D;
        padding: var(--spacing-md) var(--spacing-lg);
        border-radius: var(--border-radius-md);
        margin-right: var(--spacing-md);
        transition: all 0.3s ease;
        font-weight: 500;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .gradio-radio input:checked + label {
        background: var(--primary-gradient);
        color: white;
        box-shadow: var(--shadow-neon);
    }

    /* Inputs Styling */
    .gradio-textbox input, .gradio-textbox textarea {
        background-color: #2D2D2D;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: var(--border-radius-md);
        padding: var(--spacing-lg);
        color: var(--text-primary);
        font-family: 'Inter', sans-serif;
        transition: all 0.3s ease;
        font-size: 1.1rem;
        line-height: 1.6;
    }

    .gradio-textbox input:focus, .gradio-textbox textarea:focus {
        border-color: #9A4DFF;
        box-shadow: var(--shadow-neon);
        outline: none;
    }

    .gradio-textbox label, .gradio-radio label, .gradio-dropdown label {
        color: var(--text-secondary);
        font-size: 1.1rem;
        font-weight: 500;
        margin-bottom: var(--spacing-md);
    }

    /* Button Styling */
    .primary-button {
        background: var(--primary-gradient);
        color: white;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 1.1rem;
        padding: var(--spacing-md) var(--spacing-xl);
        border-radius: var(--border-radius-md);
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-right: var(--spacing-md);
        margin-bottom: var(--spacing-md);
    }

    .primary-button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-neon), 0 6px 12px rgba(0, 0, 0, 0.3);
    }

    .secondary-button {
        background: transparent;
        color: white;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 1.1rem;
        padding: var(--spacing-md) var(--spacing-xl);
        border-radius: var(--border-radius-md);
        border: 1px solid rgba(154, 77, 255, 0.5);
        cursor: pointer;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-right: var(--spacing-md);
        margin-bottom: var(--spacing-md);
    }

    .secondary-button:hover {
        background-color: rgba(154, 77, 255, 0.1);
        border-color: rgba(154, 77, 255, 0.8);
    }

    /* Emoji Avatar Styling */
    .avatar-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: var(--spacing-lg);
    }

    .emoji-avatar {
        width: 150px;
        height: 150px;
        margin: 0 auto var(--spacing-lg) auto;
        background: rgba(30, 30, 30, 0.6);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 3px solid rgba(154, 77, 255, 0.3);
        box-shadow: var(--shadow-neon);
        position: relative;
        overflow: hidden;
    }

    .emoji-avatar .emoji {
        font-size: 5rem;
        position: relative;
        z-index: 2;
    }

    .emoji-avatar .ripple {
        position: absolute;
        width: 100%;
        height: 100%;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(154, 77, 255, 0.4) 0%, rgba(154, 77, 255, 0) 70%);
        transform: scale(0);
animation: ripple 3s infinite ease-out;
    }

    @keyframes ripple {
        0% { transform: scale(0); opacity: 1; }
        100% { transform: scale(2.5); opacity: 0; }
    }

    .emoji-avatar.calm .emoji {
        animation: float 3s infinite ease-in-out;
    }

    .emoji-avatar.strict .emoji {
        animation: shake 2s infinite ease-in-out;
    }

    .emoji-avatar.neutral .emoji {
        animation: pulse 4s infinite ease-in-out;
    }

    @keyframes float {
        0% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0); }
    }

    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
        20%, 40%, 60%, 80% { transform: translateX(5px); }
    }

    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.08); }
        100% { transform: scale(1); }
    }

    /* Interview Question Styling */
    .question-container {
        background-color: #2D2D2D;
        border-left: 4px solid var(--accent-color);
        padding: var(--spacing-xl);
        margin-bottom: var(--spacing-xl);
        border-radius: 0 var(--border-radius-md) var(--border-radius-md) 0;
        font-size: 1.3rem;
        font-weight: 500;
        line-height: 1.6;
        max-height: 300px;
        overflow-y: auto;
    }

    /* Feedback Styling */
    .feedback-container {
        background-image: linear-gradient(to right, rgba(0, 242, 198, 0.1), rgba(0, 242, 198, 0.0));
        border-radius: var(--border-radius-md);
        padding: var(--spacing-xl);
        margin-top: var(--spacing-xl);
        position: relative;
        opacity: 0;
        transform: translateY(20px);
        animation: fadeIn 0.5s forwards;
        font-size: 1.1rem;
        line-height: 1.6;
        max-height: 400px;
        overflow-y: auto;
    }

    @keyframes fadeIn {
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* Progress Bar */
    .progress-bar {
        height: 8px;
        background-color: #2D2D2D;
        border-radius: var(--border-radius-sm);
        margin: var(--spacing-xl) 0;
        overflow: hidden;
    }

    .progress-bar-fill {
        height: 100%;
        background: var(--secondary-gradient);
        border-radius: var(--border-radius-sm);
        transition: width 0.5s ease;
    }

    /* Final Feedback */
    .final-feedback {
        background-color: #2D2D2D;
        border-radius: var(--border-radius-lg);
        padding: var(--spacing-xl);
        margin-top: var(--spacing-xl);
        position: relative;
        font-size: 1.1rem;
        line-height: 1.7;
        max-height: 70vh;
        overflow-y: auto;
        scroll-behavior: smooth;
    }

    /* Improved final feedback styling */
    .final-feedback h2 {
        color: #00FFC6;
        font-size: 1.6rem;
        margin: var(--spacing-lg) 0 var(--spacing-md) 0;
        padding-bottom: var(--spacing-sm);
        border-bottom: 2px solid rgba(154, 77, 255, 0.3);
    }

    .final-feedback h3 {
        color: #9A4DFF;
        font-size: 1.3rem;
        margin: var(--spacing-lg) 0 var(--spacing-sm) 0;
    }

    .final-feedback ul {
        margin-left: var(--spacing-xl);
        margin-bottom: var(--spacing-md);
    }

    .final-feedback li {
        margin-bottom: var(--spacing-sm);
        position: relative;
    }

    .final-feedback li:before {
        content: '•';
        color: #00C2FF;
        font-weight: bold;
        position: absolute;
        left: -20px;
    }

    .final-feedback p {
        margin-bottom: var(--spacing-md);
    }

    .final-feedback::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: var(--secondary-gradient);
        border-radius: var(--border-radius-lg) var(--border-radius-lg) 0 0;
    }

    /* Score Indicators */
    .score-indicator {
        display: inline-block;
        padding: var(--spacing-sm) var(--spacing-lg);
        border-radius: var(--border-radius-sm);
        font-weight: 600;
        margin-right: var(--spacing-md);
        margin-bottom: var(--spacing-md);
        background-color: rgba(0, 242, 198, 0.2);
        color: var(--accent-color);
    }

    /* Style for feedback sections */
    .feedback-section {
        background-color: rgba(30, 30, 30, 0.6);
        border-left: 4px solid #9A4DFF;
        padding: var(--spacing-lg);
        margin: var(--spacing-lg) 0;
        border-radius: 0 var(--border-radius-sm) var(--border-radius-sm) 0;
    }

    .strength-item {
        border-left: 3px solid var(--success-green);
        padding-left: var(--spacing-md);
        margin-bottom: var(--spacing-md);
    }

    .improvement-item {
        border-left: 3px solid var(--warning-yellow);
        padding-left: var(--spacing-md);
        margin-bottom: var(--spacing-md);
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .header h1 {
            font-size: 2.8rem;
        }

        .header h3 {
            font-size: 1.3rem;
        }

        .card {
            padding: var(--spacing-lg);
        }

        .setup-row {
            flex-direction: column;
        }

        .final-feedback {
            max-height: 50vh;
        }
    }

    /* Animated Background */
    .animated-bg {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1;
        opacity: 0.05;
        background: linear-gradient(125deg, #FF4A99, #9A4DFF, #00C2FF, #00F5A0);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }

    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Boss Type Description */
    .boss-type-list {
        margin-top: var(--spacing-lg);
        padding: var(--spacing-lg);
        background-color: rgba(30, 30, 30, 0.6);
        border-radius: var(--border-radius-md);
    }

    .boss-type-list p {
        margin: var(--spacing-md) 0;
        display: flex;
        align-items: center;
        font-size: 1.1rem;
    }

    .boss-type-list p span {
        margin-right: var(--spacing-md);
        font-size: 1.4rem;
    }

    /* Element positioning */
    .personality-selector, .job-input {
        margin-bottom: var(--spacing-xl);
    }

    /* Content centering improvements */
    .setup-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: var(--spacing-xl);
    }

    /* Section headers */
    .section-header {
        margin: var(--spacing-lg) 0;
        font-size: 1.4rem;
        font-weight: 600;
        color: var(--text-primary);
    }

    /* Button container */
    .button-container {
        display: flex;
        gap: var(--spacing-lg);
        margin: var(--spacing-xl) 0;
    }

    /* Auto scroll to bottom on content changes */
    .auto-scroll {
        scroll-behavior: smooth;
    }
""") as demo:
    # Animated background
    gr.HTML("""<div class="animated-bg"></div>""")

    with gr.Column(elem_classes="container") as main_column:
        with gr.Column(elem_classes="header") as header:
            gr.Markdown("""# 🚀 LEVEL UP! Interview Simulator
            ### Ace your next interview with AI-powered feedback""")

        with gr.Column(elem_classes="card") as setup_card:
            gr.Markdown("## 🎯 Choose Your Challenge")

            with gr.Row(elem_classes="setup-row") as setup_row:
                with gr.Column(scale=1):
                    boss_type = gr.Radio(
                        ["Calm", "Neutral", "Strict"],
                        label="Interviewer Vibe",
                        value="Neutral",
                        elem_classes="personality-selector"
                    )

                    job_role = gr.Textbox(
                        label="Dream Job Title",
                        placeholder="Software Engineer, Data Scientist, TikTok Creator...",
                        elem_classes="job-input"
                    )

                    start_button = gr.Button("START INTERVIEW", elem_classes="primary-button")

                with gr.Column(scale=1, elem_classes="avatar-wrapper"):
                    gr.Markdown("""## Your Interviewer""")
                    avatar_html = gr.HTML(elem_classes="avatar-container")

                    gr.HTML("""
                    <div class="boss-type-list">
                        <p><span>😌</span> <strong>Calm</strong> - Supportive and encouraging</p>
                        <p><span>😐</span> <strong>Neutral</strong> - Professional and balanced</p>
                        <p><span>😠</span> <strong>Strict</strong> - Challenging and demanding</p>
                    </div>
                    """)

        with gr.Column(visible=False, elem_classes="card") as interview_section:
            with gr.Column():
                gr.Markdown("## 💬 Interview in Progress", elem_classes="section-header")

                # Progress bar
                progress_bar = gr.HTML("""
                <div class="progress-bar">
                    <div class="progress-bar-fill" style="width: 0%"></div>
                </div>
                """)

                question_display = gr.Markdown(elem_classes="question-container")

                answer_input = gr.Textbox(
                    label="Your Response",
                    placeholder="Type your answer here... Be confident! ✨",
                    lines=5
                )

                with gr.Row(elem_classes="button-container"):
                    submit_button = gr.Button("SUBMIT ANSWER", elem_classes="primary-button")
                    next_button = gr.Button("NEXT QUESTION", elem_classes="secondary-button", visible=False)
                    clear_button = gr.Button("CLEAR", elem_classes="secondary-button")

                feedback_display = gr.Markdown(elem_classes="feedback-container")

        with gr.Column(visible=False, elem_classes="card") as final_section:
            with gr.Column():
                gr.Markdown("## 🏆 Interview Complete!", elem_classes="section-header")
                finish_button = gr.Button("GET FINAL FEEDBACK", elem_classes="primary-button")
                final_feedback = gr.Markdown(elem_classes="final-feedback")

                with gr.Row(elem_classes="button-container"):
                    restart_button = gr.Button("START NEW INTERVIEW", elem_classes="secondary-button")


    # Helper function to update progress bar
    def update_progress(question_number, total_questions):
        progress_percentage = int((question_number / total_questions) * 100)

        return f"""
        <div class="progress-bar">
            <div class="progress-bar-fill" style="width: {progress_percentage}%"></div>
        </div>
        """


    # Updated function to handle progress bar
    def start_interview_with_progress(boss_type, job_role):
        simulator.state["boss_type"] = boss_type
        simulator.state["job_role"] = job_role
        simulator.generate_questions(boss_type, job_role)
        progress_html = update_progress(1, len(simulator.state["questions"]))

        return (
            "Interview started! Ready for your first question.",
            simulator.get_current_question(),
            "",
            progress_html,
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(visible=True)
        )


    # Updated function to handle progress bar with next question
    def next_question_with_progress():
        simulator.next_question()
        current_q = simulator.state["current_question"] + 1
        total_q = len(simulator.state["questions"])
        progress_html = update_progress(current_q, total_q)

        return simulator.get_current_question(), "", gr.update(visible=False), progress_html


    # Enhanced function to format final feedback for better readability
    def finish_interview_enhanced():
        final_feedback_text = simulator.get_final_feedback()

        # Add custom HTML/CSS for better readability
        formatted_feedback = f"""
        <div class="auto-scroll">
            <h2>📊 Performance Summary</h2>
            {final_feedback_text}

        </div>
        """

        return formatted_feedback, gr.update(visible=True)


    # Event handlers
    boss_type.change(
        update_interviewer_avatar,
        inputs=boss_type,
        outputs=avatar_html
    )

    start_button.click(
        start_interview_with_progress,
        inputs=[boss_type, job_role],
        outputs=[
            gr.Markdown(),
            question_display,
            answer_input,
            progress_bar,
            interview_section,
            setup_card,
            final_section
        ]
    )

    submit_button.click(
        submit_answer,
        inputs=answer_input,
        outputs=[feedback_display, next_button]
    )

    next_button.click(
        next_question_with_progress,
        outputs=[
            question_display,
            answer_input,
            next_button,
            progress_bar
        ]
    )

    clear_button.click(
        clear_feedback_and_answer,
        outputs=[answer_input, feedback_display]
    )

    finish_button.click(
        finish_interview_enhanced,
        outputs=[final_feedback, restart_button]
    )

    restart_button.click(
        lambda: (
            "Interview Simulator Ready",
            "",
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(visible=False)
        ),
        outputs=[
            gr.Markdown(),
            job_role,
            setup_card,
            interview_section,
            final_section
        ]
    )

    # Add JavaScript to handle auto-scrolling
    demo.load(js="""
    function setupAutoScroll() {
        // Monitor for changes in content height
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList') {
                    const container = mutation.target.closest('.card');
                    if (container) {
                        container.scrollTop = container.scrollHeight;
                    }
                }
            });
        });

        // Apply observer to all cards
        document.querySelectorAll('.card').forEach(function(card) {
            observer.observe(card, { childList: true, subtree: true });
        });
    }

    // Call setup after a short delay to ensure DOM is loaded
    setTimeout(setupAutoScroll, 1000);
    """)

# Launch the app
if __name__ == "__main__":
    demo.launch(share=True)
