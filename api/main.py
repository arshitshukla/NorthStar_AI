from fastapi import FastAPI, Request
from pydantic import BaseModel
from services.agents import sentinel_brain

app = FastAPI()

class Tweet(BaseModel):
    text: str
    user: str

@app.post("/ingest")
async def ingest_tweet(tweet: Tweet):
    print(f"📥 Received from {tweet.user}: {tweet.text[:50]}...")
    
    # Run the LangGraph Agent
    result = sentinel_brain.invoke({"raw_text": tweet.text})
    data = result["structured_data"]

    if data.is_emergency:
        print(f"🚨 EMERGENCY DETECTED!")
        print(f"📍 Location: {data.location} | 📦 Resource: {data.resource}")
        # Next step: Save to Supabase / Notify Volunteers
    else:
        print("ℹ️ Info/Spam - Ignoring.")

    return {"status": "processed", "is_emergency": data.is_emergency}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)