from typing import Dict, Optional
from .llm_manager import LLMManager
from .document_processor import DocumentProcessor

class TeachingMode:
    def __init__(self, llm_manager: LLMManager, document_processor: DocumentProcessor):
        self.llm_manager = llm_manager
        self.document_processor = document_processor
        self.user_badges = {}  # Track user badges per topic

    async def handle_request(self, topic: str, context: Optional[str] = None) -> Dict:
        """Handle a teaching request for a specific topic"""
        try:
            # Get relevant context from uploaded notes
            if not context:
                context = await self.document_processor.get_relevant_context(topic)

            # Generate teaching evaluation
            response = await self.llm_manager.generate_response(
                mode="teaching",
                topic=topic,
                context=context
            )

            # Update user badges
            self._update_badges(topic, response.get("badges", []))

            return {
                "status": "success",
                "content": response,
                "badges": self.user_badges.get(topic, [])
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def _update_badges(self, topic: str, new_badges: list):
        """Update user badges for a topic"""
        if topic not in self.user_badges:
            self.user_badges[topic] = []

        # Add new badges
        for badge in new_badges:
            if badge not in self.user_badges[topic]:
                self.user_badges[topic].append(badge)

    def get_badge_criteria(self) -> Dict:
        """Return the criteria for earning different badges"""
        return {
            "Master Explainer": "Demonstrates exceptional clarity and depth in explanations",
            "Concept Explorer": "Shows thorough understanding of related concepts",
            "Detail Dynamo": "Provides comprehensive coverage of important details",
            "Logic Legend": "Presents information in a clear, logical sequence",
            "Example Expert": "Uses relevant examples effectively",
            "Connection Creator": "Makes meaningful connections between concepts",
            "Clarity Champion": "Explains complex ideas in simple terms",
            "Structure Star": "Organizes information effectively",
            "Application Ace": "Demonstrates practical understanding",
            "Insight Innovator": "Offers unique perspectives or insights"
        } 