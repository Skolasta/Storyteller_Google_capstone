import os
import uuid
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.adk.tools import preload_memory
from google.genai import types
from dotenv import load_dotenv
import pathlib

# Load environment variables from .env file in the same directory
env_path = pathlib.Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

# Get API Key from environment
if "GOOGLE_API_KEY" not in os.environ:
    raise ValueError("GOOGLE_API_KEY environment variable is not set. Please set it before running.")

LANGUAGE_LEVELS = {
    "A1": "Beginner - Very simple words and sentences",
    "A2": "Elementary - Simple daily conversations",
    "B1": "Intermediate - Daily life and travel topics",
    "B2": "Upper Intermediate - Complex texts and discussions",
    "C1": "Advanced - Academic and professional language",
    "C2": "Expert - Native language level"
}

class StoryAgentManager:
    def __init__(self):
        self.session_service = InMemorySessionService()
        self.memory_service = InMemoryMemoryService()
        # We will store runners for both agents
        self.story_runners = {} 
        self.pedagogue_runners = {}

    def get_storyteller(self, target_language, level, native_language="English"):
        """Agent 1: The Creative Storyteller"""
        key = (target_language, level, native_language)
        if key in self.story_runners:
            return self.story_runners[key]

        instruction = f"""
You are a creative Storyteller.
Your goal is to create immersive, interactive adventures.

CONTEXT:
- Target Language to teach: {target_language}
- User's Native Language: {native_language}
- User's Level: {level}

INSTRUCTIONS:
1. Create a short, engaging story segment (2-3 paragraphs).
2. The story should be written primarily in {native_language} so the user understands the plot.
3. End the segment with 2-3 distinct choices for the user to continue the story.
4. Do NOT worry about teaching vocabulary or formatting. Just tell a great story.
"""
        retry_config = types.HttpRetryOptions(attempts=3)
        
        agent = LlmAgent(
            model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
            name=f"storyteller_{target_language}_{level}",
            instruction=instruction
        )

        runner = Runner(
            agent=agent,
            app_name=f"Storyteller_{target_language}",
            session_service=self.session_service,
            memory_service=self.memory_service,
        )
        self.story_runners[key] = runner
        return runner

    def get_pedagogue(self, target_language, level, native_language="English"):
        """Agent 2: The Language Teacher (Pedagogue)"""
        key = (target_language, level, native_language)
        if key in self.pedagogue_runners:
            return self.pedagogue_runners[key]

        instruction = f"""
You are an expert Language Pedagogue.
You work with a Storyteller to teach {target_language} to a {native_language} speaker (Level: {level}).

INPUT:
You will receive a story segment and choices from the Storyteller.

YOUR MISSION:
1. **Review & Refine:** Ensure the story text is simple enough for a {level} student.
2. **Inject Vocabulary:** Identify key words in the story. Rewrite them in this format: `NativeWord (**TargetWord**)`.
   - Example: "You see a house (**ev**)."
   - Ensure the TargetWord is in {target_language}.
3. **Format Choices:** Ensure the choices are in {native_language}, but add the {target_language} translation in parentheses.
4. **Memory:** Use the `preload_memory` tool to check what the user already knows. Reinforce those words.

ALWAYS:
- Keep the story flow intact.
- Be encouraging.
- NEVER show internal debug info.
"""
        retry_config = types.HttpRetryOptions(attempts=3)

        agent = LlmAgent(
            model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
            name=f"pedagogue_{target_language}_{level}",
            instruction=instruction,
            tools=[preload_memory]
        )

        runner = Runner(
            agent=agent,
            app_name=f"Pedagogue_{target_language}",
            session_service=self.session_service,
            memory_service=self.memory_service,
        )
        self.pedagogue_runners[key] = runner
        return runner

    async def create_session(self, target_language, level, native_language="English", user_id="web_user"):
        # We need sessions for both agents, but we can link them by ID pattern or just manage them here.
        # Let's use the same session ID suffix for simplicity.
        base_id = uuid.uuid4().hex[:6]
        session_id = f"session_{base_id}"
        
        # Initialize sessions for both runners
        story_runner = self.get_storyteller(target_language, level, native_language)
        pedagogue_runner = self.get_pedagogue(target_language, level, native_language)

        await story_runner.session_service.create_session(session_id=f"story_{session_id}", app_name=story_runner.app_name, user_id=user_id)
        await pedagogue_runner.session_service.create_session(session_id=f"pedag_{session_id}", app_name=pedagogue_runner.app_name, user_id=user_id)
        
        return session_id

    async def send_message(self, session_id, message_text, target_language, level, native_language="English", user_id="web_user"):
        story_runner = self.get_storyteller(target_language, level, native_language)
        pedagogue_runner = self.get_pedagogue(target_language, level, native_language)

        # Step 1: User -> Storyteller
        # The user's input (choice or text) goes to the storyteller to advance the plot.
        story_input = types.Content(role="user", parts=[types.Part(text=message_text)])
        
        story_response_text = ""
        async for event in story_runner.run_async(
            session_id=f"story_{session_id}",
            user_id=user_id,
            new_message=story_input
        ):
            if hasattr(event, 'content') and hasattr(event.content, 'parts'):
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        story_response_text = part.text

        # Step 2: Storyteller Output -> Pedagogue
        # The raw story goes to the pedagogue to be "taught".
        pedagogue_input_text = f"""
[STORYTELLER OUTPUT START]
{story_response_text}
[STORYTELLER OUTPUT END]

Please refine this for the student.
"""
        pedagogue_input = types.Content(role="user", parts=[types.Part(text=pedagogue_input_text)])

        final_response_text = ""
        async for event in pedagogue_runner.run_async(
            session_id=f"pedag_{session_id}",
            user_id=user_id,
            new_message=pedagogue_input
        ):
            if hasattr(event, 'content') and hasattr(event.content, 'parts'):
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        final_response_text = part.text
        
        return final_response_text

# Singleton instance
manager = StoryAgentManager()
