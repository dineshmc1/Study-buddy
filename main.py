from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
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

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with HTML documentation"""
    return """
    <html>
        <head>
            <title>LLM Study Buddy API</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                h1 { color: #2c3e50; }
                .endpoint { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }
                .method { color: #e74c3c; font-weight: bold; }
                .url { color: #3498db; }
                .description { color: #7f8c8d; }
            </style>
        </head>
        <body>
            <h1>Welcome to LLM Study Buddy API</h1>
            <p>This API provides endpoints for personalized learning and teaching experiences.</p>
            
            <div class="endpoint">
                <h2>Available Endpoints:</h2>
                
                <div class="endpoint">
                    <p><span class="method">POST</span> <span class="url">/upload</span></p>
                    <p class="description">Upload study notes for processing. Accepts PDF, images (PNG, JPG), and text files.</p>
                </div>

                <div class="endpoint">
                    <p><span class="method">POST</span> <span class="url">/study</span></p>
                    <p class="description">Handle study requests in either learning or teaching mode.</p>
                </div>

                <div class="endpoint">
                    <p><span class="method">GET</span> <span class="url">/docs</span></p>
                    <p class="description">Interactive API documentation (Swagger UI)</p>
                </div>
            </div>

            <h2>Quick Start:</h2>
            <ol>
                <li>Visit <a href="/docs">/docs</a> for interactive API documentation</li>
                <li>Use the /upload endpoint to upload your study notes</li>
                <li>Use the /study endpoint to start learning or teaching sessions</li>
            </ol>
        </body>
    </html>
    """

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
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True) 