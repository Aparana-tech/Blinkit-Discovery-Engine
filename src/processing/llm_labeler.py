import os
import json
import logging
from typing import List, Dict, Any
from groq import Groq

logger = logging.getLogger(__name__)

class LLMLabeler:
    """Uses Groq API to label a cluster of reviews with a Theme and Pillar."""
    
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key == "your_groq_api_key_here":
            logger.warning("GROQ_API_KEY not found in environment. LLM labeling will run in mock mode.")
            self.client = None
        else:
            self.client = Groq(api_key=api_key)
            
        self.model = "llama-3.1-8b-instant" # Fast and smart enough for extraction

    def _get_system_prompt(self) -> str:
        return """You are the Blinkit Discovery Engine AI. 
I will give you a list of user reviews that belong to the same cluster (they are complaining about the same thing).
Your job is to analyze them and output a JSON object with the following fields:
1. "theme_name": A short 3-6 word name for this problem (e.g. "Invisible Pet Food Inventory").
2. "pillar": MUST be exactly one of these four: ["Habit & Velocity", "Trust & Information", "UX Friction", "Segment Propensity"].
3. "best_quote": Pick the single most descriptive sentence from the provided reviews that proves this problem.
4. "actionable_insight": A 1-sentence recommendation on how the product team can fix this.

Respond ONLY with valid JSON. Do not include markdown formatting or any other text."""

    def label_cluster(self, cluster_id: int, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Takes a list of reviews in a cluster, samples them, and asks Groq to label the cluster."""
        # If it's the noise cluster (-1) or empty, skip
        if cluster_id == -1 or not records:
            return {"cluster_id": cluster_id, "theme_name": "Noise / Uncategorized"}

        # If no API key, return mock data
        if not self.client:
            return {
                "cluster_id": cluster_id,
                "theme_name": "Mock Theme (No API Key)",
                "pillar": "UX Friction",
                "best_quote": records[0].get('text', '')[:50] + "...",
                "actionable_insight": "Please add Groq API key to .env",
                "size": len(records),
                "reviews": records
            }

        # To save tokens, we only send the first 10 reviews of a cluster
        sample_texts = [r['text'] for r in records[:10]]
        prompt = "Here are the reviews in this cluster:\n"
        for i, text in enumerate(sample_texts):
            prompt += f"{i+1}. {text}\n"

        logger.info(f"Calling Groq to label cluster {cluster_id} ({len(records)} reviews)")
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            result_json = response.choices[0].message.content
            insight = json.loads(result_json)
            
            # Attach the original records
            insight["cluster_id"] = cluster_id
            insight["size"] = len(records)
            insight["reviews"] = records
            
            return insight
            
        except Exception as e:
            logger.error(f"Groq API error on cluster {cluster_id}: {e}")
            return {
                "cluster_id": cluster_id,
                "theme_name": f"Error: {str(e)}",
                "size": len(records),
                "reviews": records
            }
