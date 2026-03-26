from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI()

class SocialMessage(BaseModel):
    source: str
    user: str
    text: str

@app.post("/ingest")
async def receive_message(msg: SocialMessage):
    print(f"\n📥 NEW SIGNAL RECEIVED from {msg.source}")
    print(f"👤 User: {msg.user}")
    print(f"💬 Text: {msg.text}")
    print("-" * 30)
    
    # NEXT STEP: Trigger LangGraph Agent here
    return {"status": "received", "id": "processed_123"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)