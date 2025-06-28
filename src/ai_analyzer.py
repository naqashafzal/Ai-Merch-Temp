# src/ai_analyzer.py

import os
import json
import google.generativeai as genai
from PIL import Image

class AIAnalyzer:
    """
    Handles Vision Analysis using Google Gemini to understand brand aesthetics.
    """
    def __init__(self):
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.vision_model = genai.GenerativeModel('gemini-pro-vision')
                print("AI Analyzer: Google API key found. Vision model ready.")
            except Exception as e:
                self.vision_model = None
                print(f"AI Analyzer: Error configuring Google AI. {e}")
        else:
            self.vision_model = None
            print("AI Analyzer: GOOGLE_API_KEY not set. Using mock analysis.")

    def get_structured_analysis(self, screenshot_path, colors):
        """
        Generates a structured analysis including aesthetics and recommendations.
        """
        if not self.vision_model:
            return self._get_mock_analysis(colors)
        try:
            img = Image.open(screenshot_path)
            prompt = """
            Analyze the visual style of this website screenshot. Based on your analysis, provide a JSON object with two keys:
            1. "brand_aesthetics": A 2-3 sentence paragraph describing the site's aesthetic (e.g., minimalist, corporate, playful), layout, and mood.
            2. "design_recommendations": A JSON array of 3 short, actionable design recommendations for creating branded merchandise.
            """
            prompt_parts = [prompt, img]
            response = self.vision_model.generate_content(prompt_parts)
            cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
            analysis_data = json.loads(cleaned_response)
            return analysis_data
        except Exception as e:
            print(f"Error calling or parsing Google Gemini API response: {e}")
            return self._get_mock_analysis(colors)

    def _get_mock_analysis(self, colors):
        """Provides a fallback structured analysis."""
        aesthetics = "Based on the visual analysis, the brand aesthetic appears to be modern and minimalist."
        recommendations = [
            f"Use the primary color ({colors[0]}) for main backgrounds.",
            "Keep the design simple, focusing on the logo.",
            "Ensure text elements use a high-contrast color for readability."
        ]
        return {
            "brand_aesthetics": aesthetics,
            "design_recommendations": recommendations
        }