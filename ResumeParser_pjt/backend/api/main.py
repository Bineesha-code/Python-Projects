"""
FastAPI main application
"""
import os
import uuid
import tempfile
import time
from pathlib import Path
from typing import Optional
import traceback  # add at top if missing


from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import aiofiles

from ..models.resume_models import ResumeUploadResponse, ErrorResponse, ParsedResume
from ..core.resume_parser import ResumeParser
from config import MAX_FILE_SIZE, ALLOWED_EXTENSIONS, SUPPORTED_FORMATS

# Initialize FastAPI app
app = FastAPI(
    title="Smart Resume Parser API",
    description="An intelligent API for parsing resume documents and extracting structured information",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize resume parser
resume_parser = ResumeParser()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Smart Resume Parser API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "upload": "/upload-resume",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "resume-parser-api"
    }


@app.post("/upload-resume", response_model=ResumeUploadResponse)
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload and parse a resume file
    
    Args:
        file: Resume file (PDF or DOCX)
        
    Returns:
        Parsed resume data
    """
    try:
        # Validate file
        validation_error = await _validate_file(file)
        if validation_error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=validation_error
            )
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Determine file type
        file_extension = Path(file.filename).suffix.lower()
        file_type = file_extension[1:]  # Remove the dot
        
        # Save uploaded file temporarily
        temp_file_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                temp_file_path = temp_file.name

                # Read and save file content
                content = await file.read()
                async with aiofiles.open(temp_file_path, 'wb') as f:
                    await f.write(content)
            
            # Parse the resume
            start_time = time.time()
            parsed_data = resume_parser.parse_resume(temp_file_path, file_type)
            processing_time = time.time() - start_time
            print("🔍 Parsed Experience Entries:")
            print(parsed_data.experience)


            # Debug log: print experience count
            experience_count = len(parsed_data.experience or [])
            print(f"[DEBUG] Experience entries parsed: {experience_count}")

            if not parsed_data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to parse resume. Please check if the file is valid and contains readable text."
                )
            
            return ResumeUploadResponse(
                success=True,
                message="Resume parsed successfully",
                file_id=file_id,
                parsed_data=parsed_data,
                processing_time=processing_time
            )
            
        finally:
            # Clean up temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/parse-stats/{file_id}")
async def get_parsing_stats(file_id: str):
    """
    Get parsing statistics for a processed resume
    Note: This is a placeholder - in a real app, you'd store results in a database
    """
    return {
        "message": "Statistics endpoint - would retrieve stats for file_id in a real implementation",
        "file_id": file_id
    }


async def _validate_file(file: UploadFile) -> Optional[str]:
    """
    Validate uploaded file
    
    Args:
        file: Uploaded file
        
    Returns:
        Error message if validation fails, None otherwise
    """
    # Check if file is provided
    if not file or not file.filename:
        return "No file provided"
    
    # Check file size
    if file.size and file.size > MAX_FILE_SIZE:
        return f"File size exceeds maximum allowed size of {MAX_FILE_SIZE / (1024*1024):.1f}MB"
    
    # Check file extension
    file_extension = Path(file.filename).suffix.lower()
    if file_extension[1:] not in ALLOWED_EXTENSIONS:
        return f"File type not supported. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
    
    # Check MIME type
    if file.content_type not in SUPPORTED_FORMATS:
        return f"Invalid file format. Expected: {', '.join(SUPPORTED_FORMATS.keys())}"
    
    return None


@app.exception_handler(HTTPException)
async def general_exception_handler(request, exc):
    traceback.print_exc()  # 🔥 PRINT FULL ERROR TO TERMINAL
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            success=False,
            message="Internal server error",
            error_code="500",
            details={"error": str(exc)}
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            success=False,
            message="Internal server error",
            error_code="500",
            details={"error": str(exc)}
        ).dict()
    )


if __name__ == "__main__":
    import uvicorn
    from config import HOST, PORT
    
    uvicorn.run(
        "backend.api.main:app",
        host=HOST,
        port=PORT,
        reload=True
    )
