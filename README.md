# AI-Powered CAPTCHA Security Tool

## Overview
This project is an excellent demonstration of **Cybersecurity intersecting with Artificial Intelligence (AI)**. It explores the modern offensive-defensive paradigm of CAPTCHA systems by employing AI logic on both sides of the application:
1. **Defensive AI (Generation):** Utilizes Google's Gemini LLM to generate truly random, non-dictionary, non-repetitive alphanumeric strings for CAPTCHA challenges, increasing entropy and resisting basic dictionary attacks.
2. **Offensive AI (Breaking/Decoding):** Implements an automated capability using Gemini Vision to analyze and decode the generated CAPTCHA images, simulating modern automated bypass attacks. It includes a fallback mechanism to traditional Optical Character Recognition (OCR) via Tesseract if the AI model fails.
3. **Model Context Protocol (MCP):** Exposes CAPTCHA generation, verification, and breaking functionalities as structured tools over MCP, allowing any AI Agent (like the included LangGraph client) to autonomously interact with the CAPTCHA system.

This project perfectly fits as an **AI-driven Application Security Research Project**.

## Features
- **FastMCP Server**: Provides three core tools (`generate_captcha`, `verify_captcha`, `break_captcha`) over standard input/output.
- **Flask Web Application**: Provides a browser interface (`index.html`) to visually generate, solve, and break CAPTCHAs, seamlessly wrapping the local MCP server.
- **Interactive LangGraph Agent**: An interactive command-line LLM client that acts as a cybersecurity analyst, capable of reasoning and using the MCP tools to automatically bypass or generate CAPTCHAs on the fly.
- **Dynamic Image Obfuscation**: Generates CAPTCHAs with noise (lines, scatter points) and character rotation to simulate real-world anti-automation hurdles.

## Prerequisites
- **Python 3.8+**
- **Google Gemini API Key**: Set in the `.env` file (`GOOGLE_API_KEY=your_key_here`).
- **Tesseract OCR (Optional but recommended)**: Used as a fallback if Gemini fails to break the CAPTCHA.

## Setup & Installation

1. **Clone the repository and enter the directory.**
2. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Ensure you have packages like `fastmcp`, `flask`, `pillow`, `pytesseract`, `google-generativeai`, `langchain-google-genai`, `langgraph`, and `python-dotenv` installed)*
3. **Configure Environment Variables:**
   Create a `.env` file in the root directory and add your API key:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

## Getting Started

### 1. Web Application Mode (Interactive UI)
Run the Flask server which provides a web interface:
```bash
python web_app.py
```
- Navigate to `http://127.0.0.1:5000` in your browser.
- You can manually test generating CAPTCHAs, or click "Break" to have the server's Gemini model attempt to solve it.

### 2. Autonomous Agent Mode (CLI)
Run the LangGraph client to interact with the system using an AI agent:
```bash
python mcp_client.py
```
- A prompt will appear: `💬 Ask me something:`
- Example commands you can type:
  - *"Generate a new captcha and show me the ID."*
  - *"Can you break the CAPTCHA image I just generated?"*
  - *"Verify if 'ABCD12' is the correct sequence for my CAPTCHA."*

### 3. Standalone MCP Server Mode
If you want to attach the MCP server to Claude Desktop or another MCP client:
```bash
python mcp_server.py
```

## Potential Enhancements
While this is a strong conceptual project, several enhancements can be made for production readiness or advanced research:

1. **Persistent/Secure State Management**: The `CAPTCHA_STORE` currently uses an in-memory Python dictionary. Implementing a Redis or database backend with Time-To-Live (TTL) expiration would prevent memory leaks and replay attacks.
2. **Cross-Platform Compatibility**: The font loading mechanism has a hardcoded Linux path (`/usr/share/fonts/...`). Use dynamic font loading or include a `.ttf` file in the repository to ensure high-quality text rendering across Windows/Mac/Linux.
3. **Advanced Obfuscation Algorithms**: Enhance the image generator with variable font sizing, sine-wave text warping, color inversion tricks, and 3D overlaps.
4. **Rate Limiting**: Implement rate limiters on the endpoints (e.g., using `Flask-Limiter`) to prevent brute-forcing of the `/verify` and `/break` endpoints.
5. **Adversarial Noise Generation**: Dynamically calculate noise lines that perfectly intersect characters at natural human-reading boundaries to specifically target AI vision model weaknesses.