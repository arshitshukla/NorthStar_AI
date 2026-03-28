import os
from fastapi import FastAPI
from pydantic import BaseModel
from supabase import create_client, Client
from services.agents import sentinel_brain
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Supabase Setup
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

class Tweet(BaseModel):
    text: str
    user: str

@app.post("/ingest")
async def ingest_tweet(tweet: Tweet):
    # 1. Run the AI Brain
    result = sentinel_brain.invoke({"raw_text": tweet.text})
    data = result["structured_data"]

    # 2. If it's a real emergency, save it to the DB!
    if data.is_emergency:
        print(f"🚨 ACTIONABLE SIGNAL: Saving {tweet.user}'s report...")
        
        db_entry = {
            "user_handle": tweet.user,
            "content": tweet.text,
            "resource": data.resource,
            "location": data.location,
            "urgency_score": data.urgency_score
        }
        
        supabase.table("emergency_reports").insert(db_entry).execute()

    return {"status": "processed", "is_emergency": data.is_emergency}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)