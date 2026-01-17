import os
import shutil
import uuid
from typing import BinaryIO
from pathlib import Path
import aiofiles
import logging

logger = logging.getLogger(__name__)


class FileStorageService:
    """Service for handling file uploads and storage."""
    
    def __init__(self, upload_dir: str):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    async def save_file(
        self,
        file_content: BinaryIO,
        filename: str,
        patient_id: str
    ) -> tuple[str, int]:
        """
        Save an uploaded file to the uploads directory.
        
        Args:
            file_content: File content as binary stream
            filename: Original filename
            patient_id: Patient UUID for organizing files
            
        Returns:
            Tuple of (file_path, file_size)
        """
        try:
            # Create patient-specific directory
            patient_dir = self.upload_dir / str(patient_id)
            patient_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate unique filename
            file_extension = Path(filename).suffix
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = patient_dir / unique_filename
            
            # Save file
            file_size = 0
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file_content.read()
                file_size = len(content)
                await f.write(content)
            
            logger.info(f"Saved file: {file_path} ({file_size} bytes)")
            
            return str(file_path), file_size
            
        except Exception as e:
            logger.error(f"Error saving file {filename}: {str(e)}")
            raise
    
    def delete_file(self, file_path: str) -> bool:
        """Delete a file from storage."""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                logger.info(f"Deleted file: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {str(e)}")
            return False
    
    def file_exists(self, file_path: str) -> bool:
        """Check if a file exists."""
        return Path(file_path).exists()


def create_file_storage_service(upload_dir: str) -> FileStorageService:
    """Factory function to create file storage service."""
    return FileStorageService(upload_dir)
