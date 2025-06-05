import ollama
from typing import Dict, List, Optional
import json

class LLMManager:
    def __init__(self):
        self.model = "llama2:8b"
        self.context_window = 4096
        self.temperature = 0.7
        self.system_prompts = {
            "learning": """You are an expert tutor helping a student learn. Your goal is to:
1. Explain concepts clearly and concisely
2. Ask targeted questions to test understanding
3. Provide detailed feedback
4. Adapt difficulty based on performance
5. Encourage active recall

Current topic: {topic}
Context from notes: {context}

Respond in JSON format with the following structure:
{
    "explanation": "Clear explanation of the concept",
    "questions": [
        {
            "type": "multiple_choice|true_false|short_answer|conceptual",
            "question": "The question text",
            "options": ["option1", "option2", ...],  # Only for multiple choice
            "correct_answer": "The correct answer",
            "explanation": "Why this is correct"
        }
    ],
    "active_recall_prompt": "A prompt to encourage active recall",
    "difficulty_level": "beginner|intermediate|advanced"
}""",
            "teaching": """You are evaluating a student's explanation of a concept. Your goal is to:
1. Listen carefully to their explanation
2. Identify gaps in understanding
3. Provide constructive feedback
4. Suggest areas for improvement
5. Award appropriate badges

Current topic: {topic}
Context from notes: {context}

Respond in JSON format with the following structure:
{
    "missing_concepts": ["List of missing or unclear concepts"],
    "gaps": ["List of identified gaps in understanding"],
    "feedback": "Detailed constructive feedback",
    "suggested_readings": ["Specific sections to review"],
    "rating": "excellent|good|needs_improvement",
    "badges": ["List of earned badges"]
}"""
        }

    async def generate_response(self, mode: str, topic: str, context: Optional[str] = None) -> Dict:
        """Generate a response using the LLM based on the specified mode and context"""
        prompt = self.system_prompts[mode].format(
            topic=topic,
            context=context or "No additional context provided"
        )
        
        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                temperature=self.temperature
            )
            
            # Parse the JSON response
            return json.loads(response['response'])
        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")

    async def evaluate_answer(self, question: Dict, user_answer: str) -> Dict:
        """Evaluate a user's answer to a question"""
        prompt = f"""Evaluate the following answer to a question:

Question: {question['question']}
Correct Answer: {question['correct_answer']}
User's Answer: {user_answer}

Provide feedback in JSON format:
{{
    "is_correct": true/false,
    "feedback": "Detailed feedback on the answer",
    "suggested_improvements": ["List of suggestions"]
}}"""

        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                temperature=0.3  # Lower temperature for more consistent evaluation
            )
            
            return json.loads(response['response'])
        except Exception as e:
            raise Exception(f"Error evaluating answer: {str(e)}") 