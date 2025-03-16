# AI-Powered Interview Simulator

## Overview
The **AI-Powered Interview Simulator** is designed to help job seekers prepare for interviews by simulating realistic scenarios. It leverages AI to generate tailored questions, evaluate responses, and provide actionable feedback to improve interview skills and boost confidence.

## Features
- **Custom Scenarios:** Select your desired interviewer type and job role for a personalized experience.
- **Dynamic Questions:** Generates both technical and behavioral questions using AI.
- **Answer Feedback:** Provides scored evaluations with detailed suggestions for improvement.
- **Final Summary:** Offers a comprehensive review of your overall performance.

## Technologies Used
- **Python:** Core backend logic.
- **Gradio:** Interactive user interface for seamless user interaction.
- **Google Generative AI:** Powers the generation of interview questions and feedback.

## How to Run
### Step 1: Install Dependencies
Run the following command to install required packages:
```bash
pip install gradio google-generativeai
```

### Step 2: Clone the Repository
```bash
git clone https://github.com/your-username/interview-simulator.git
cd interview-simulator
```

### Step 3: Add API Key
Add your **Google Generative AI API Key** to `main.py` as shown below:
```python
import os
os.environ["GEMINI_API_KEY"] = "YOUR_API_KEY_HERE"
```

### Step 4: Run the Application
```bash
python main.py
```

### Step 5: Access the Interface
Open your browser and visit:
```
http://127.0.0.1:7860/
```

## Contributing
We welcome contributions! Follow these steps:
1. Fork the repository.
2. Create a new branch: `git checkout -b feature-branch-name`.
3. Commit your changes: `git commit -m "Add feature/fix bug"`.
4. Push to your branch: `git push origin feature-branch-name`.
5. Open a Pull Request.

## License
This project is licensed under the **MIT License**. See the `LICENSE` file for more details.

