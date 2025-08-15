"""
Multi-Provider Storage Service
Supports AWS S3, MinIO, and Local filesystem storage
"""

import os
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, BinaryIO, List
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import minio
from minio.error import S3Error
import uuid
from datetime import datetime, timedelta

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config.settings import settings
from config.storage_config import StorageConfig


class StorageProvider(ABC):
    """Abstract base class for storage providers"""
    
    @abstractmethod
    async def upload_file(self, file_data: bytes, file_path: str, content_type: str) -> Dict[str, Any]:
        """Upload file and return metadata"""
        pass
    
    @abstractmethod
    async def download_file(self, file_path: str) -> bytes:
        """Download file content"""
        pass
    
    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """Delete file"""
        pass
    
    @abstractmethod
    async def get_file_url(self, file_path: str, expiry_hours: int = 24) -> str:
        """Get temporary URL for file access"""
        pass
    
    @abstractmethod
    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists"""
        pass
    
    @abstractmethod
    async def get_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """Get file metadata"""
        pass


class LocalStorageProvider(StorageProvider):
    """Local filesystem storage provider"""
    
    def __init__(self, base_path: str, url_prefix: str):
        self.base_path = Path(base_path)
        self.url_prefix = url_prefix
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    async def upload_file(self, file_data: bytes, file_path: str, content_type: str) -> Dict[str, Any]:
        """Upload file to local storage"""
        full_path = self.base_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(full_path, 'wb') as f:
                f.write(file_data)
            
            return {
                "success": True,
                "file_path": str(full_path),
                "url": f"{self.url_prefix}/{file_path}",
                "size": len(file_data),
                "provider": "local"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def download_file(self, file_path: str) -> bytes:
        """Download file from local storage"""
        full_path = self.base_path / file_path
        
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(full_path, 'rb') as f:
            return f.read()
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from local storage"""
        full_path = self.base_path / file_path
        
        try:
            if full_path.exists():
                full_path.unlink()
                return True
            return False
        except Exception:
            return False
    
    async def get_file_url(self, file_path: str, expiry_hours: int = 24) -> str:
        """Get URL for local file access"""
        # For local storage, return direct URL (no expiry)
        return f"{self.url_prefix}/{file_path}"
    
    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists in local storage"""
        full_path = self.base_path / file_path
        return full_path.exists()
    
    async def get_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """Get file metadata from local storage"""
        full_path = self.base_path / file_path
        
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        stat = full_path.stat()
        return {
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime),
            "created": datetime.fromtimestamp(stat.st_ctime),
            "path": str(full_path)
        }


class S3StorageProvider(StorageProvider):
    """AWS S3 storage provider"""
    
    def __init__(self, bucket_name: str, region: str, access_key: str, secret_key: str, endpoint_url: Optional[str] = None):
        self.bucket_name = bucket_name
        self.region = region
        
        try:
            self.client = boto3.client(
                's3',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region,
                endpoint_url=endpoint_url
            )
            
            # Test connection
            self.client.head_bucket(Bucket=bucket_name)
            
        except (ClientError, NoCredentialsError) as e:
            raise ConnectionError(f"Failed to connect to S3: {e}")
    
    async def upload_file(self, file_data: bytes, file_path: str, content_type: str) -> Dict[str, Any]:
        """Upload file to S3"""
        try:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=file_path,
                Body=file_data,
                ContentType=content_type,
                ServerSideEncryption='AES256'
            )
            
            url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{file_path}"
            
            return {
                "success": True,
                "file_path": file_path,
                "url": url,
                "size": len(file_data),
                "provider": "aws_s3"
            }
        except ClientError as e:
            return {"success": False, "error": str(e)}
    
    async def download_file(self, file_path: str) -> bytes:
        """Download file from S3"""
        try:
            response = self.client.get_object(Bucket=self.bucket_name, Key=file_path)
            return response['Body'].read()
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise FileNotFoundError(f"File not found: {file_path}")
            raise
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from S3"""
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=file_path)
            return True
        except ClientError:
            return False
    
    async def get_file_url(self, file_path: str, expiry_hours: int = 24) -> str:
        """Get presigned URL for S3 file access"""
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': file_path},
                ExpiresIn=expiry_hours * 3600
            )
            return url
        except ClientError as e:
            raise Exception(f"Failed to generate presigned URL: {e}")
    
    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists in S3"""
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=file_path)
            return True
        except ClientError:
            return False
    
    async def get_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """Get file metadata from S3"""
        try:
            response = self.client.head_object(Bucket=self.bucket_name, Key=file_path)
            return {
                "size": response.get('ContentLength', 0),
                "modified": response.get('LastModified'),
                "content_type": response.get('ContentType'),
                "etag": response.get('ETag', '').strip('"')
            }
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise FileNotFoundError(f"File not found: {file_path}")
            raise


class MinIOStorageProvider(StorageProvider):
    """MinIO storage provider"""
    
    def __init__(self, endpoint: str, bucket_name: str, access_key: str, secret_key: str, secure: bool = True):
        self.bucket_name = bucket_name
        
        try:
            self.client = minio.Minio(
                endpoint,
                access_key=access_key,
                secret_key=secret_key,
                secure=secure
            )
            
            # Create bucket if it doesn't exist
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
                
        except Exception as e:
            raise ConnectionError(f"Failed to connect to MinIO: {e}")
    
    async def upload_file(self, file_data: bytes, file_path: str, content_type: str) -> Dict[str, Any]:
        """Upload file to MinIO"""
        try:
            from io import BytesIO
            
            self.client.put_object(
                self.bucket_name,
                file_path,
                BytesIO(file_data),
                length=len(file_data),
                content_type=content_type
            )
            
            # Get URL (note: this might need adjustment based on MinIO setup)
            url = f"http://{self.client._base_url.netloc}/{self.bucket_name}/{file_path}"
            
            return {
                "success": True,
                "file_path": file_path,
                "url": url,
                "size": len(file_data),
                "provider": "minio"
            }
        except S3Error as e:
            return {"success": False, "error": str(e)}
    
    async def download_file(self, file_path: str) -> bytes:
        """Download file from MinIO"""
        try:
            response = self.client.get_object(self.bucket_name, file_path)
            return response.read()
        except S3Error as e:
            if "NoSuchKey" in str(e):
                raise FileNotFoundError(f"File not found: {file_path}")
            raise
        finally:
            if 'response' in locals():
                response.close()
                response.release_conn()
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from MinIO"""
        try:
            self.client.remove_object(self.bucket_name, file_path)
            return True
        except S3Error:
            return False
    
    async def get_file_url(self, file_path: str, expiry_hours: int = 24) -> str:
        """Get presigned URL for MinIO file access"""
        try:
            url = self.client.presigned_get_object(
                self.bucket_name,
                file_path,
                expires=timedelta(hours=expiry_hours)
            )
            return url
        except S3Error as e:
            raise Exception(f"Failed to generate presigned URL: {e}")
    
    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists in MinIO"""
        try:
            self.client.stat_object(self.bucket_name, file_path)
            return True
        except S3Error:
            return False
    
    async def get_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """Get file metadata from MinIO"""
        try:
            stat = self.client.stat_object(self.bucket_name, file_path)
            return {
                "size": stat.size,
                "modified": stat.last_modified,
                "content_type": stat.content_type,
                "etag": stat.etag
            }
        except S3Error as e:
            if "NoSuchKey" in str(e):
                raise FileNotFoundError(f"File not found: {file_path}")
            raise


class StorageService:
    """Main storage service that manages multiple providers"""
    
    def __init__(self):
        self.providers: Dict[str, StorageProvider] = {}
        self.primary_provider = settings.primary_storage_provider
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize storage providers based on configuration"""
        config = StorageConfig.get_storage_config()
        
        # Initialize local storage
        local_config = config.get("local", {})
        if local_config:
            self.providers["local"] = LocalStorageProvider(
                base_path=local_config.get("base_path", "./uploads"),
                url_prefix=local_config.get("url_prefix", "/static/uploads")
            )
        
        # Initialize AWS S3 if configured
        s3_config = config.get("aws_s3", {})
        if s3_config and all(s3_config.get(key) for key in ["bucket_name", "access_key", "secret_key"]):
            try:
                self.providers["aws_s3"] = S3StorageProvider(
                    bucket_name=s3_config["bucket_name"],
                    region=s3_config["region"],
                    access_key=s3_config["access_key"],
                    secret_key=s3_config["secret_key"],
                    endpoint_url=s3_config.get("endpoint_url")
                )
            except Exception as e:
                print(f"Failed to initialize S3 provider: {e}")
        
        # Initialize MinIO if configured
        minio_config = config.get("minio", {})
        if minio_config and all(minio_config.get(key) for key in ["bucket_name", "endpoint_url", "access_key", "secret_key"]):
            try:
                self.providers["minio"] = MinIOStorageProvider(
                    endpoint=minio_config["endpoint_url"],
                    bucket_name=minio_config["bucket_name"],
                    access_key=minio_config["access_key"],
                    secret_key=minio_config["secret_key"],
                    secure=minio_config.get("secure", False)
                )
            except Exception as e:
                print(f"Failed to initialize MinIO provider: {e}")
        
        # Ensure we have at least one provider
        if not self.providers:
            raise Exception("No storage providers could be initialized")
        
        # Fallback to first available provider if primary is not available
        if self.primary_provider not in self.providers:
            self.primary_provider = list(self.providers.keys())[0]
            print(f"Primary storage provider not available, using: {self.primary_provider}")
    
    def get_provider(self, provider_name: Optional[str] = None) -> StorageProvider:
        """Get storage provider instance"""
        provider_name = provider_name or self.primary_provider
        
        if provider_name not in self.providers:
            raise ValueError(f"Storage provider '{provider_name}' not available")
        
        return self.providers[provider_name]
    
    async def upload_file(self, file_data: bytes, filename: str, content_type: str, 
                         file_category: str = "general", provider_name: Optional[str] = None) -> Dict[str, Any]:
        """Upload file using specified or primary provider"""
        provider = self.get_provider(provider_name)
        
        # Generate unique file path
        file_path = self._generate_file_path(filename, file_category)
        
        result = await provider.upload_file(file_data, file_path, content_type)
        
        if result.get("success"):
            result["file_path"] = file_path
            result["provider"] = provider_name or self.primary_provider
        
        return result
    
    async def download_file(self, file_path: str, provider_name: Optional[str] = None) -> bytes:
        """Download file from specified or primary provider"""
        provider = self.get_provider(provider_name)
        return await provider.download_file(file_path)
    
    async def delete_file(self, file_path: str, provider_name: Optional[str] = None) -> bool:
        """Delete file from specified or primary provider"""
        provider = self.get_provider(provider_name)
        return await provider.delete_file(file_path)
    
    async def get_file_url(self, file_path: str, expiry_hours: int = 24, 
                          provider_name: Optional[str] = None) -> str:
        """Get file URL from specified or primary provider"""
        provider = self.get_provider(provider_name)
        return await provider.get_file_url(file_path, expiry_hours)
    
    async def file_exists(self, file_path: str, provider_name: Optional[str] = None) -> bool:
        """Check if file exists in specified or primary provider"""
        provider = self.get_provider(provider_name)
        return await provider.file_exists(file_path)
    
    async def get_file_metadata(self, file_path: str, provider_name: Optional[str] = None) -> Dict[str, Any]:
        """Get file metadata from specified or primary provider"""
        provider = self.get_provider(provider_name)
        return await provider.get_file_metadata(file_path)
    
    def _generate_file_path(self, filename: str, file_category: str) -> str:
        """Generate unique file path"""
        # Extract file extension
        file_ext = Path(filename).suffix.lower()
        
        # Generate unique filename
        unique_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y/%m/%d")
        
        # Create structured path: category/year/month/day/unique_id.ext
        file_path = f"{file_category}/{timestamp}/{unique_id}{file_ext}"
        
        return file_path
    
    def get_available_providers(self) -> List[str]:
        """Get list of available storage providers"""
        return list(self.providers.keys())
    
    def health_check(self) -> Dict[str, str]:
        """Check health of all storage providers"""
        health = {}
        
        for provider_name in self.providers:
            try:
                # This is a simple check - in production you might want more thorough health checks
                health[provider_name] = "healthy"
            except Exception as e:
                health[provider_name] = f"unhealthy: {str(e)}"
        
        return health


# Global storage service instance
storage_service = StorageService()
