# Storyteller_Google_capstone: Polyglot Dungeon Master

> **Capstone Track:** Agents for Good (Education) / Freestyle
> **Powered by:** Google Gemini 2.5 Flash & Agent Development Kit (ADK)

## 🎯 Executive Summary
**Polyglot Dungeon Master** is an AI agent that transforms language learning from boring flashcards into a living, breathing adventure. Users become the protagonist of a dynamic story led by a "Dungeon Master", while a "Pedagogue Agent" (Language Tutor) adapts the story to the user's language level and builds vocabulary in the background.

This project uses Google ADK's **Multi-Agent**, **Long-Term Memory**, and **Human-in-the-Loop (HITL)** capabilities to provide a personalized educational experience.

---

## 💡 Why Agents?
Traditional language learning apps are static and repetitive. Why does "Polyglot Dungeon Master" need AI Agents to solve this problem?

1.  **Dynamic Storytelling (Non-Deterministic):** Instead of a static script, a **Gemini**-powered agent creates a unique story every time. The user never experiences the same adventure twice.
2.  **Contextual Memory (Memory Bank):** The agent remembers words learned in previous sessions and items in the inventory (`VertexAIMemoryBank`). If you've learned a word, the agent knows and shapes the story accordingly.
3.  **Adaptive Teaching:** As the user's level (A1, B2, etc.) changes, the agent instantly adjusts the language and challenges used. This is not possible with pre-coded software.

---

## 1. The Pitch (Sunum)

### Concept & Value
**Story Agent** is an AI-powered interactive storytelling platform designed to make language learning immersive and fun. Instead of memorizing flashcards, users become the protagonist of a dynamic story tailored to their proficiency level.

**Why it matters:**
- **Contextual Learning:** Vocabulary is learned in the context of a narrative, improving retention.
- **Personalized:** The story adapts to the user's choices and level (A1-C2).
- **Interactive:** Users aren't passive readers; they drive the plot.

### The Problem
Traditional language learning apps often feel repetitive and disconnected from real-world usage. Learners struggle to bridge the gap between memorizing words and using them in sentences.

### The Solution
A **Multi-Agent AI System** that acts as both a creative Dungeon Master and a patient Language Tutor. It generates infinite unique stories while seamlessly integrating vocabulary lessons.

---

## 2. The Implementation (Uygulama)

### Technical Architecture
The project is built using a **Multi-Agent System** to separate concerns and ensure high-quality output.

**Stack:**
- **Backend:** Python (FastAPI)
- **AI Model:** Google Gemini Pro (via Google GenAI SDK)
- **Agent Framework:** Google Agent Development Kit (ADK)
- **Frontend:** HTML/CSS/JS (Glassmorphism UI)

### Core Concepts Applied (The "Big 3")

1.  **Multi-Agent Architecture:**
    - **Agent 1 (The Storyteller):** A creative agent focused purely on narrative generation, plot consistency, and creating engaging choices. It writes in the user's native language to ensure plot comprehension.
    - **Agent 2 (The Pedagogue):** An educational agent that acts as a filter. It takes the raw story, injects target language vocabulary `Native (**Target**)`, simplifies grammar for the specific level (e.g., A1), and manages the educational reinforcement.
    - *Why?* Separating these roles prevents the "confused agent" problem where an AI tries to be too creative and forgets to teach, or teaches too much and ruins the story flow.

2.  **Tools & Function Calling:**
    - The Pedagogue agent utilizes the `preload_memory` tool to access the user's learning history. This allows it to "remember" which words the user has struggled with or learned previously, enabling **Spaced Repetition**.

3.  **Memory Management:**
    - We use `InMemorySessionService` and `InMemoryMemoryService` to maintain state across the conversation. The agents remember the plot twists (Storyteller memory) and the user's vocabulary progress (Pedagogue memory) independently but cohesively.

### Setup & Run

1.  **Prerequisites:** Python 3.9+ installed.
2.  **Clone & Install:**
    ```bash
    cd Storyteller_Google_capstone/backend
    pip install -r requirements.txt
    ```
3.  **Environment:**
    - Create a `.env` file in `Storyteller_Google_capstone/backend/` with your API key:
      ```
      GOOGLE_API_KEY=your_api_key_here
      ```
4.  **Run Backend:**
    ```bash
    python main.py
    ```
5.  **Run Frontend:**
    - Open `Storyteller_Google_capstone/frontend/index.html` in your browser.

---

## Project Journey
Started as a simple Jupyter notebook to test prompts, evolved into a robust web application with a split-brain multi-agent architecture to handle the delicate balance between entertainment and education.
