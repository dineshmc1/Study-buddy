from typing import Dict, Optional
from .llm_manager import LLMManager
from .document_processor import DocumentProcessor

class LearningMode:
    def __init__(self, llm_manager: LLMManager, document_processor: DocumentProcessor):
        self.llm_manager = llm_manager
        self.document_processor = document_processor
        self.user_progress = {}  # Track user progress per topic

    async def handle_request(self, topic: str, context: Optional[str] = None) -> Dict:
        """Handle a learning request for a specific topic"""
        try:
            # Get relevant context from uploaded notes
            if not context:
                context = await self.document_processor.get_relevant_context(topic)

            # Generate learning content
            response = await self.llm_manager.generate_response(
                mode="learning",
                topic=topic,
                context=context
            )

            # Update user progress
            self._update_progress(topic, response)

            return {
                "status": "success",
                "content": response,
                "progress": self.user_progress.get(topic, {
                    "questions_answered": 0,
                    "correct_answers": 0,
                    "difficulty_level": "beginner"
                })
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    async def evaluate_answer(self, topic: str, question: Dict, user_answer: str) -> Dict:
        """Evaluate a user's answer to a question"""
        try:
            # Get evaluation from LLM
            evaluation = await self.llm_manager.evaluate_answer(question, user_answer)

            # Update progress
            self._update_progress_after_answer(topic, evaluation["is_correct"])

            return {
                "status": "success",
                "evaluation": evaluation,
                "progress": self.user_progress.get(topic, {
                    "questions_answered": 0,
                    "correct_answers": 0,
                    "difficulty_level": "beginner"
                })
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def _update_progress(self, topic: str, response: Dict):
        """Update user progress based on the learning content"""
        if topic not in self.user_progress:
            self.user_progress[topic] = {
                "questions_answered": 0,
                "correct_answers": 0,
                "difficulty_level": response.get("difficulty_level", "beginner")
            }

    def _update_progress_after_answer(self, topic: str, is_correct: bool):
        """Update progress after answering a question"""
        if topic in self.user_progress:
            self.user_progress[topic]["questions_answered"] += 1
            if is_correct:
                self.user_progress[topic]["correct_answers"] += 1

            # Adjust difficulty based on performance
            correct_ratio = self.user_progress[topic]["correct_answers"] / self.user_progress[topic]["questions_answered"]
            if correct_ratio > 0.8:
                self.user_progress[topic]["difficulty_level"] = "advanced"
            elif correct_ratio > 0.6:
                self.user_progress[topic]["difficulty_level"] = "intermediate"
            else:
                self.user_progress[topic]["difficulty_level"] = "beginner" 