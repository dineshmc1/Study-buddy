from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from study_buddy.core.llm_manager import LLMManager
from study_buddy.core.document_processor import DocumentProcessor
from study_buddy.core.learning_mode import LearningMode
from study_buddy.core.teaching_mode import TeachingMode

app = FastAPI(title="LLM Study Buddy", description="Personalized Learning & Active Recall System")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize core components
llm_manager = LLMManager()
document_processor = DocumentProcessor()
learning_mode = LearningMode(llm_manager, document_processor)
teaching_mode = TeachingMode(llm_manager, document_processor)

class StudyRequest(BaseModel):
    topic: str
    mode: str  # "learning" or "teaching"
    context: Optional[str] = None

class UploadResponse(BaseModel):
    message: str
    topics: List[str]

@app.post("/upload", response_model=UploadResponse)
async def upload_notes(file: UploadFile = File(...)):
    """Upload study notes for processing"""
    try:
        topics = await document_processor.process_document(file)
        return UploadResponse(
            message="Document processed successfully",
            topics=topics
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/study")
async def study(request: StudyRequest):
    """Handle study requests in either learning or teaching mode"""
    try:
        if request.mode == "learning":
            response = await learning_mode.handle_request(request.topic, request.context)
        elif request.mode == "teaching":
            response = await teaching_mode.handle_request(request.topic, request.context)
        else:
            raise HTTPException(status_code=400, detail="Invalid mode specified")
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 