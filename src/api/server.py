import logging
import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import groq
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Blinkit Discovery Engine API")

# Setup Groq Client
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    logger.warning("GROQ_API_KEY not found in environment. Chatbot will fail.")
else:
    client = groq.AsyncGroq(api_key=api_key)

class ChatMessage(BaseModel):
    message: str

def get_ai_context():
    """Load the clusters JSON to inject real Blinkit context into the AI."""
    try:
        # Load up to the top 15 clusters to save tokens
        with open("data/processed/clusters_2026-07.json", "r") as f:
            raw_data = json.load(f)
            
            # Filter noise
            filtered = [d for d in raw_data if d.get("cluster_id") != -1]
            # Sort by size
            filtered.sort(key=lambda x: x.get("size", 0), reverse=True)
            
            # Strip out the massive 'reviews' array from each cluster to save 90% of tokens
            clean_context = []
            for d in filtered[:15]:
                clean_context.append({
                    "theme": d.get("theme_name"),
                    "pillar": d.get("pillar"),
                    "insight": d.get("actionable_insight"),
                    "mentions": d.get("size"),
                    "quote": d.get("best_quote")
                })
                
            return json.dumps(clean_context)
    except Exception as e:
        logger.error(f"Could not load context data: {e}")
        return "No specific data context loaded."

@app.post("/api/chat")
async def chat_endpoint(msg: ChatMessage):
    if not api_key:
        raise HTTPException(status_code=500, detail="Groq API key missing. Please configure .env")
        
    context_data = get_ai_context()
    
    system_prompt = f"""You are the internal 'Blinkit Discovery Engine AI'. You are an expert product analyst.
Your job is to answer strategic questions about Blinkit based strictly on the user feedback data we have gathered.

Here is the exact data you must base your answers on (Top 15 Problem Clusters):
{context_data}

If the user asks one of the core 8 strategic questions, you must directly relate your answer to the Discovery Pillars (Habit & Velocity, UX Friction, Trust & Information Gap, Segment Propensity). 
Be extremely professional, concise, and insightful. Format your response cleanly."""

    try:
        completion = await client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": msg.message}
            ],
            temperature=0.7,
            max_tokens=800
        )
        return {"response": completion.choices[0].message.content}
    except Exception as e:
        logger.error(f"Chat API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Mount Data directory for frontend charts
app.mount("/data", StaticFiles(directory="data"), name="data")

# Mount static frontend
app.mount("/", StaticFiles(directory="src/frontend", html=True), name="frontend")
