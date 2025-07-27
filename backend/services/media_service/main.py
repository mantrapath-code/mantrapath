"""
Media Service - File uploads, processing, and management
"""

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import os
import shutil
from pathlib import Path
from pydantic import BaseModel, UUID4
import magic
from PIL import Image
import io
import redis

# Import shared modules
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.database import get_db
from shared.auth import get_current_user, require_moderator
from shared.models import MediaFile, User

app = FastAPI(
    title="MantraPath Media Service",
    description="File uploads, processing, and management",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
MEDIA_ROOT = Path("/app/media")  # In Docker container
MEDIA_ROOT.mkdir(exist_ok=True)

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm", "video/quicktime"}
ALLOWED_AUDIO_TYPES = {"audio/mpeg", "audio/wav", "audio/ogg"}
ALLOWED_DOCUMENT_TYPES = {"application/pdf", "text/plain"}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB

# Redis for caching
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

# Pydantic models
class MediaResponse(BaseModel):
    id: UUID4
    filename: str
    file_path: str
    file_size: int
    content_type: str
    is_processed: bool
    is_approved: bool
    thumbnail_path: Optional[str]
    alt_text: Optional[str]
    caption: Optional[str]
    tags: List[str]
    created_at: datetime

class MediaUploadResponse(BaseModel):
    id: UUID4
    filename: str
    file_size: int
    content_type: str
    upload_url: str
    thumbnail_url: Optional[str]
    status: str

class ModerationRequest(BaseModel):
    action: str  # approve, reject
    reason: Optional[str] = None

# Utility functions
def get_file_type_category(content_type: str) -> str:
    """Categorize file by content type"""
    if content_type in ALLOWED_IMAGE_TYPES:
        return "image"
    elif content_type in ALLOWED_VIDEO_TYPES:
        return "video"
    elif content_type in ALLOWED_AUDIO_TYPES:
        return "audio"
    elif content_type in ALLOWED_DOCUMENT_TYPES:
        return "document"
    else:
        return "other"

def is_allowed_file_type(content_type: str) -> bool:
    """Check if file type is allowed"""
    allowed_types = (
        ALLOWED_IMAGE_TYPES | 
        ALLOWED_VIDEO_TYPES | 
        ALLOWED_AUDIO_TYPES | 
        ALLOWED_DOCUMENT_TYPES
    )
    return content_type in allowed_types

def get_safe_filename(filename: str, user_id: str) -> str:
    """Generate safe filename with user prefix"""
    # Remove path components and clean filename
    safe_name = os.path.basename(filename)
    name, ext = os.path.splitext(safe_name)
    
    # Create unique filename
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    unique_name = f"{user_id}_{timestamp}_{name}{ext}"
    
    return unique_name

def create_thumbnail(image_path: Path, thumbnail_path: Path, size: tuple = (300, 300)):
    """Create thumbnail for image"""
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary (for PNG with transparency)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            # Create thumbnail
            img.thumbnail(size, Image.Resampling.LANCZOS)
            img.save(thumbnail_path, "JPEG", quality=85, optimize=True)
            return True
    except Exception as e:
        print(f"Error creating thumbnail: {e}")
        return False

# Media upload endpoints
@app.post("/api/v1/media/upload", response_model=MediaUploadResponse)
async def upload_media(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    alt_text: Optional[str] = Form(None),
    caption: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),  # Comma-separated tags
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Upload media file"""
    
    # Validate file size
    file_content = await file.read()
    file_size = len(file_content)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413, 
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # Detect content type
    content_type = magic.from_buffer(file_content, mime=True)
    
    # Validate file type
    if not is_allowed_file_type(content_type):
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed: {content_type}"
        )
    
    # Additional validation for images
    if content_type in ALLOWED_IMAGE_TYPES and file_size > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Image too large. Maximum size: {MAX_IMAGE_SIZE / 1024 / 1024}MB"
        )
    
    # Generate safe filename and path
    safe_filename = get_safe_filename(file.filename, current_user["user_id"])
    file_category = get_file_type_category(content_type)
    
    # Create category directory
    category_dir = MEDIA_ROOT / file_category
    category_dir.mkdir(exist_ok=True)
    
    file_path = category_dir / safe_filename
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Parse tags
    tag_list = []
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
    
    # Create database record
    media_file = MediaFile(
        id=uuid.uuid4(),
        user_id=current_user["user_id"],
        filename=safe_filename,
        file_path=str(file_path),
        file_size=file_size,
        content_type=content_type,
        is_processed=False,
        is_approved=False,  # Requires moderation
        alt_text=alt_text,
        caption=caption,
        tags=tag_list
    )
    
    db.add(media_file)
    db.commit()
    db.refresh(media_file)
    
    # Process file in background
    background_tasks.add_task(
        process_media_file, 
        str(media_file.id), 
        str(file_path), 
        content_type
    )
    
    return MediaUploadResponse(
        id=media_file.id,
        filename=safe_filename,
        file_size=file_size,
        content_type=content_type,
        upload_url=f"/api/v1/media/{media_file.id}/file",
        thumbnail_url=None,  # Will be generated during processing
        status="uploaded_pending_approval"
    )

@app.get("/api/v1/media/", response_model=List[MediaResponse])
async def get_user_media(
    skip: int = 0,
    limit: int = 20,
    content_type: Optional[str] = None,
    approved_only: bool = True,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get user's uploaded media"""
    
    query = db.query(MediaFile).filter(
        MediaFile.user_id == current_user["user_id"]
    )
    
    if approved_only:
        query = query.filter(MediaFile.is_approved == True)
    
    if content_type:
        query = query.filter(MediaFile.content_type.like(f"{content_type}%"))
    
    media_files = query.order_by(
        desc(MediaFile.created_at)
    ).offset(skip).limit(limit).all()
    
    return [
        MediaResponse(
            id=media.id,
            filename=media.filename,
            file_path=media.file_path,
            file_size=media.file_size,
            content_type=media.content_type,
            is_processed=media.is_processed,
            is_approved=media.is_approved,
            thumbnail_path=media.thumbnail_path,
            alt_text=media.alt_text,
            caption=media.caption,
            tags=media.tags or [],
            created_at=media.created_at
        )
        for media in media_files
    ]

@app.get("/api/v1/media/{media_id}", response_model=MediaResponse)
async def get_media_details(
    media_id: UUID4,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get media file details"""
    
    media = db.query(MediaFile).filter(
        and_(
            MediaFile.id == media_id,
            MediaFile.user_id == current_user["user_id"]
        )
    ).first()
    
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    return MediaResponse(
        id=media.id,
        filename=media.filename,
        file_path=media.file_path,
        file_size=media.file_size,
        content_type=media.content_type,
        is_processed=media.is_processed,
        is_approved=media.is_approved,
        thumbnail_path=media.thumbnail_path,
        alt_text=media.alt_text,
        caption=media.caption,
        tags=media.tags or [],
        created_at=media.created_at
    )

@app.get("/api/v1/media/{media_id}/file")
async def get_media_file(
    media_id: UUID4,
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """Serve media file"""
    
    query = db.query(MediaFile).filter(MediaFile.id == media_id)
    
    # Allow access to approved media for any user
    # Restrict unapproved media to owner only
    if current_user:
        query = query.filter(
            or_(
                MediaFile.is_approved == True,
                MediaFile.user_id == current_user["user_id"]
            )
        )
    else:
        query = query.filter(MediaFile.is_approved == True)
    
    media = query.first()
    
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    file_path = Path(media.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return FileResponse(
        path=str(file_path),
        media_type=media.content_type,
        filename=media.filename
    )

@app.get("/api/v1/media/{media_id}/thumbnail")
async def get_media_thumbnail(
    media_id: UUID4,
    db: Session = Depends(get_db)
):
    """Serve media thumbnail"""
    
    media = db.query(MediaFile).filter(
        and_(
            MediaFile.id == media_id,
            MediaFile.is_approved == True
        )
    ).first()
    
    if not media or not media.thumbnail_path:
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    
    thumbnail_path = Path(media.thumbnail_path)
    if not thumbnail_path.exists():
        raise HTTPException(status_code=404, detail="Thumbnail file not found")
    
    return FileResponse(
        path=str(thumbnail_path),
        media_type="image/jpeg"
    )

@app.put("/api/v1/media/{media_id}")
async def update_media(
    media_id: UUID4,
    alt_text: Optional[str] = None,
    caption: Optional[str] = None,
    tags: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update media metadata"""
    
    media = db.query(MediaFile).filter(
        and_(
            MediaFile.id == media_id,
            MediaFile.user_id == current_user["user_id"]
        )
    ).first()
    
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    # Update fields
    if alt_text is not None:
        media.alt_text = alt_text
    if caption is not None:
        media.caption = caption
    if tags is not None:
        media.tags = [tag.strip() for tag in tags.split(",") if tag.strip()]
    
    db.commit()
    
    return {"message": "Media updated successfully"}

@app.delete("/api/v1/media/{media_id}")
async def delete_media(
    media_id: UUID4,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete media file"""
    
    media = db.query(MediaFile).filter(
        and_(
            MediaFile.id == media_id,
            MediaFile.user_id == current_user["user_id"]
        )
    ).first()
    
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    # Delete from database
    db.delete(media)
    db.commit()
    
    # Delete files in background
    background_tasks.add_task(
        cleanup_media_files, 
        media.file_path, 
        media.thumbnail_path
    )
    
    return {"message": "Media deleted successfully"}

# Moderation endpoints
@app.get("/api/v1/media/admin/pending")
async def get_pending_media(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_moderator)
):
    """Get media files pending approval (moderator only)"""
    
    media_files = db.query(MediaFile).filter(
        MediaFile.is_approved == False
    ).order_by(MediaFile.created_at).offset(skip).limit(limit).all()
    
    return [
        {
            "id": str(media.id),
            "filename": media.filename,
            "content_type": media.content_type,
            "file_size": media.file_size,
            "uploader_id": media.user_id,
            "alt_text": media.alt_text,
            "caption": media.caption,
            "tags": media.tags,
            "created_at": media.created_at.isoformat(),
            "thumbnail_url": f"/api/v1/media/{media.id}/thumbnail" if media.thumbnail_path else None
        }
        for media in media_files
    ]

@app.post("/api/v1/media/{media_id}/moderate")
async def moderate_media(
    media_id: UUID4,
    moderation: ModerationRequest,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_moderator)
):
    """Moderate media file (approve/reject)"""
    
    media = db.query(MediaFile).filter(MediaFile.id == media_id).first()
    
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    if moderation.action == "approve":
        media.is_approved = True
        message = "Media approved successfully"
    elif moderation.action == "reject":
        # Delete rejected media
        db.delete(media)
        # Clean up files in background would go here
        message = "Media rejected and deleted"
    else:
        raise HTTPException(status_code=400, detail="Invalid moderation action")
    
    db.commit()
    
    # TODO: Send notification to user about moderation decision
    
    return {"message": message, "action": moderation.action}

# Background processing functions
async def process_media_file(media_id: str, file_path: str, content_type: str):
    """Background task to process uploaded media"""
    
    try:
        # Create thumbnail for images
        if content_type in ALLOWED_IMAGE_TYPES:
            file_path_obj = Path(file_path)
            thumbnail_dir = file_path_obj.parent / "thumbnails"
            thumbnail_dir.mkdir(exist_ok=True)
            
            thumbnail_path = thumbnail_dir / f"thumb_{file_path_obj.name}"
            
            if create_thumbnail(file_path_obj, thumbnail_path):
                # Update database with thumbnail path
                # In a real implementation, you'd get a new DB session here
                print(f"✅ Thumbnail created for {media_id}: {thumbnail_path}")
            else:
                print(f"❌ Failed to create thumbnail for {media_id}")
        
        # Mark as processed
        # In a real implementation, update the database here
        print(f"✅ Media processing completed for {media_id}")
    
    except Exception as e:
        print(f"❌ Error processing media {media_id}: {e}")

async def cleanup_media_files(file_path: str, thumbnail_path: Optional[str] = None):
    """Background task to clean up deleted media files"""
    
    try:
        # Delete main file
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️ Deleted file: {file_path}")
        
        # Delete thumbnail
        if thumbnail_path and os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)
            print(f"🗑️ Deleted thumbnail: {thumbnail_path}")
    
    except Exception as e:
        print(f"❌ Error cleaning up files: {e}")

# Health check
@app.get("/health")
async def health_check():
    """Service health check"""
    
    # Check disk space
    disk_usage = shutil.disk_usage(MEDIA_ROOT)
    free_space_gb = disk_usage.free / (1024**3)
    
    return {
        "status": "healthy",
        "service": "media_service",
        "timestamp": datetime.utcnow().isoformat(),
        "media_root": str(MEDIA_ROOT),
        "free_space_gb": round(free_space_gb, 2)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8009)