import os
from typing import TypedDict, List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv

load_dotenv()
from langchain_groq import ChatGroq

groq_api_key = os.getenv("GROQ_API_KEY")

# Use Llama 3 for high-speed free extraction
llm = ChatGroq(
    model="llama-3.3-70b-versatile", 
    temperature=0,
    api_key=groq_api_key
)
# 1. Define the Schema for the extracted data
class ExtractedNeed(BaseModel):
    is_emergency: bool = Field(description="Is this a real request for help?")
    resource: Optional[str] = Field(description="e.g., Oxygen, Blood, Food")
    location: Optional[str] = Field(description="City or neighborhood")
    contact: Optional[str] = Field(description="Phone number or handle")
    urgency_score: int = Field(description="1 to 10 scale of urgency")

# 2. Define the State (The 'Memory' of our Graph)
class AgentState(TypedDict):
    raw_text: str
    structured_data: Optional[ExtractedNeed]

# 3. Initialize the LLM (Gemini 2.0 Flash)
# Make sure to set your API Key: export GOOGLE_API_KEY='your_key'
# llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

# 4. Define the Logic Node
def triage_node(state: AgentState):
    print(f"🧠 Triage Agent analyzing: {state['raw_text'][:50]}...")
    
    # We use 'with_structured_output' to force Gemini to return JSON
    structured_llm = llm.with_structured_output(ExtractedNeed)
    
    result = structured_llm.invoke(f"""
        Analyze this social media post from a disaster zone:
        '{state['raw_text']}'
        
        Extract the details. If it's a joke, spam, or news, set is_emergency=False.
    """)
    
    return {"structured_data": result}

# 5. Build the Graph
workflow = StateGraph(AgentState)
workflow.add_node("triage", triage_node)
workflow.set_entry_point("triage")
workflow.add_edge("triage", END)

# Compile
sentinel_brain = workflow.compile()

# Test Run logic
if __name__ == "__main__":
    test_text = "URGENT: Need 2 O2 cylinders in Indiranagar, Lucknow. Call 9876543210 immediately!!"
    result = sentinel_brain.invoke({"raw_text": test_text})
    print("\n✅ Structured Result:")
    print(result["structured_data"])