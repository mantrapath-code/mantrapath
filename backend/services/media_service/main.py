"""
Media Service - File uploads, processing, and management
Enhanced Architecture Implementation
"""

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import os
import magic
from pathlib import Path

# Import our new architecture components
from config.settings import settings, get_file_category, is_allowed_mime_type, get_max_size_for_type
from models.media_models import MediaFile, MediaVariant, ContentAnalysis, MediaProcessingJob
from models.request_models import (
    MediaUploadRequest, MediaUploadResponse, MediaFileResponse, MediaListResponse,
    MediaUpdateRequest, MediaSearchRequest, MediaProcessingRequest, MediaProcessingResponse,
    HealthCheckResponse, ErrorResponse
)
from services.storage_service import storage_service
from services.image_processor import image_processor

# Import shared modules (keeping existing imports)
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.database import get_db
from shared.auth import get_current_user, require_moderator

# Initialize FastAPI app
app = FastAPI(
    title="MantraPath Media Service",
    description="Advanced media processing service with multi-provider storage, AI analysis, and CDN integration",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for local storage
if settings.primary_storage_provider == "local":
    static_path = Path(settings.local_storage_path)
    static_path.mkdir(exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


# Utility functions
def get_safe_filename(original_filename: str, user_id: str) -> str:
    """Generate safe filename with user and timestamp prefix"""
    file_ext = Path(original_filename).suffix.lower()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"{user_id}_{timestamp}_{unique_id}{file_ext}"


def detect_file_type(file_data: bytes, filename: str) -> tuple[str, str]:
    """Detect MIME type and file category"""
    try:
        mime_type = magic.from_buffer(file_data, mime=True)
    except Exception:
        # Fallback to filename extension
        ext = Path(filename).suffix.lower()
        mime_type_map = {
            '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png',
            '.gif': 'image/gif', '.webp': 'image/webp',
            '.mp4': 'video/mp4', '.webm': 'video/webm', '.mov': 'video/quicktime',
            '.mp3': 'audio/mpeg', '.wav': 'audio/wav', '.ogg': 'audio/ogg',
            '.pdf': 'application/pdf', '.txt': 'text/plain'
        }
        mime_type = mime_type_map.get(ext, 'application/octet-stream')
    
    file_category = get_file_category(mime_type)
    return mime_type, file_category


# Main upload endpoint
@app.post("/api/v1/media/upload", response_model=MediaUploadResponse)
async def upload_media(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    alt_text: Optional[str] = Form(None),
    caption: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    is_public: Optional[bool] = Form(False),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Upload media file with enhanced processing and storage"""
    
    try:
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Validate filename
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")
        
        # Detect file type and validate
        mime_type, file_category = detect_file_type(file_content, file.filename)
        
        if not is_allowed_mime_type(mime_type):
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed: {mime_type}"
            )
        
        # Check file size limits
        max_size = get_max_size_for_type(file_category)
        if file_size > max_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size for {file_category}: {max_size / 1024 / 1024:.1f}MB"
            )
        
        # Generate safe filename
        safe_filename = get_safe_filename(file.filename, str(current_user["user_id"]))
        
        # Upload to storage
        upload_result = await storage_service.upload_file(
            file_data=file_content,
            filename=safe_filename,
            content_type=mime_type,
            file_category=file_category
        )
        
        if not upload_result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Upload failed: {upload_result.get('error', 'Unknown error')}"
            )
        
        # Parse tags
        tag_list = []
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()][:20]
        
        # Create database record
        media_file = MediaFile(
            user_id=uuid.UUID(current_user["user_id"]),
            filename=safe_filename,
            original_filename=file.filename,
            file_type=file_category,
            file_size=file_size,
            mime_type=mime_type,
            storage_provider=upload_result.get("provider", settings.primary_storage_provider),
            storage_path=upload_result.get("file_path", ""),
            processing_status="pending",
            is_public=is_public or False,
            file_metadata={
                "original_filename": file.filename,
                "upload_timestamp": datetime.now().isoformat(),
                "tags": tag_list,
                "alt_text": alt_text,
                "caption": caption
            }
        )
        
        db.add(media_file)
        db.commit()
        db.refresh(media_file)
        
        # Create processing job
        processing_job = MediaProcessingJob(
            media_file_id=media_file.id,
            job_type="initial_processing",
            job_config={
                "file_category": file_category,
                "generate_thumbnail": True,
                "analyze_content": True
            },
            priority=5
        )
        
        db.add(processing_job)
        db.commit()
        db.refresh(processing_job)
        
        # Queue background processing
        background_tasks.add_task(
            process_media_file,
            str(media_file.id),
            file_content,
            file_category,
            mime_type
        )
        
        return MediaUploadResponse(
            id=media_file.id,
            filename=safe_filename,
            file_size=file_size,
            content_type=mime_type,
            file_type=file_category,
            upload_url=f"/api/v1/media/{media_file.id}",
            status="uploaded_processing",
            processing_job_id=processing_job.id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )


# Get media file
@app.get("/api/v1/media/{media_id}", response_model=MediaFileResponse)
async def get_media_file(
    media_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """Get media file details"""
    
    query = db.query(MediaFile).filter(MediaFile.id == media_id)
    
    # Access control
    if current_user:
        query = query.filter(
            or_(
                MediaFile.is_public == True,
                MediaFile.user_id == current_user["user_id"]
            )
        )
    else:
        query = query.filter(MediaFile.is_public == True)
    
    media = query.first()
    
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    return MediaFileResponse.model_validate(media)


# List media files
@app.get("/api/v1/media/", response_model=MediaListResponse)
async def list_media_files(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    file_type: Optional[str] = Query(None),
    is_public: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """List media files with pagination"""
    
    query = db.query(MediaFile)
    
    # Apply filters
    if current_user:
        if is_public is not None:
            query = query.filter(MediaFile.is_public == is_public)
        query = query.filter(
            or_(
                MediaFile.is_public == True,
                MediaFile.user_id == current_user["user_id"]
            )
        )
    else:
        query = query.filter(MediaFile.is_public == True)
    
    if file_type:
        query = query.filter(MediaFile.file_type == file_type)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * per_page
    media_files = query.order_by(desc(MediaFile.created_at)).offset(offset).limit(per_page).all()
    
    # Calculate pagination info
    pages = (total + per_page - 1) // per_page
    has_next = page < pages
    has_prev = page > 1
    
    return MediaListResponse(
        items=[MediaFileResponse.model_validate(media) for media in media_files],
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
        has_next=has_next,
        has_prev=has_prev
    )


# Serve media file content
@app.get("/api/v1/media/{media_id}/file")
async def serve_media_file(
    media_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """Serve media file content"""
    
    query = db.query(MediaFile).filter(MediaFile.id == media_id)
    
    # Access control
    if current_user:
        query = query.filter(
            or_(
                MediaFile.is_public == True,
                MediaFile.user_id == current_user["user_id"]
            )
        )
    else:
        query = query.filter(MediaFile.is_public == True)
    
    media = query.first()
    
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    try:
        # Get file URL from storage provider
        file_url = await storage_service.get_file_url(
            file_path=media.storage_path,
            provider_name=media.storage_provider
        )
        
        # For local storage, serve the file directly
        if media.storage_provider == "local":
            file_path = Path(settings.local_storage_path) / media.storage_path
            if file_path.exists():
                return FileResponse(
                    path=str(file_path),
                    media_type=media.mime_type,
                    filename=media.original_filename
                )
        
        # For other providers, redirect to the signed URL
        return JSONResponse(
            content={"redirect_url": file_url},
            status_code=302
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to serve file: {str(e)}"
        )


# Process media file (background task)
async def process_media_file(
    media_id: str,
    file_content: bytes,
    file_category: str,
    mime_type: str
):
    """Background task to process uploaded media"""
    
    try:
        # Update processing status
        # Note: In production, you'd get a new DB session here
        
        if file_category == "image":
            # Generate thumbnail
            thumbnail_result = await image_processor.process_image(
                image_data=file_content,
                operation="thumbnail",
                parameters={"size": settings.thumbnail_size}
            )
            
            if thumbnail_result["success"]:
                # Upload thumbnail to storage
                thumbnail_upload = await storage_service.upload_file(
                    file_data=thumbnail_result["data"],
                    filename=f"thumb_{media_id}.jpg",
                    content_type="image/jpeg",
                    file_category="thumbnails"
                )
                
                print(f"✅ Thumbnail generated for {media_id}")
            
            # Analyze image
            analysis_result = await image_processor.analyze_image(file_content)
            if analysis_result["success"]:
                print(f"✅ Image analysis completed for {media_id}")
        
        print(f"✅ Media processing completed for {media_id}")
    
    except Exception as e:
        print(f"❌ Error processing media {media_id}: {e}")


# Health check endpoint
@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Service health check"""
    
    try:
        # Check storage providers
        storage_health = storage_service.health_check()
        
        # Check disk space (for local storage)
        disk_space = {"free_gb": 0.0, "used_gb": 0.0}
        if settings.primary_storage_provider == "local":
            import shutil
            usage = shutil.disk_usage(settings.local_storage_path)
            disk_space = {
                "free_gb": round(usage.free / (1024**3), 2),
                "used_gb": round((usage.total - usage.free) / (1024**3), 2)
            }
        
        return HealthCheckResponse(
            status="healthy",
            service="media_service",
            timestamp=datetime.now(),
            storage_providers=storage_health,
            processing_queues={"background_tasks": 0},  # Placeholder
            database="connected",  # Placeholder
            disk_space=disk_space
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Health check failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=settings.service_host, 
        port=settings.service_port,
        reload=True if os.getenv("ENVIRONMENT") == "development" else False
    )