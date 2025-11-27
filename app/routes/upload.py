"""
Rutas para manejo de uploads de archivos
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import List
from supabase import Client
import uuid
import os
from datetime import datetime

from app.database import get_db
from app.utils.dependencies import get_current_active_user

router = APIRouter(prefix="/upload")

# Configuración
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"]
ALLOWED_VIDEO_TYPES = ["video/mp4", "video/mpeg", "video/quicktime", "video/webm"]
ALLOWED_DOCUMENT_TYPES = ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@router.post("/files", status_code=status.HTTP_201_CREATED)
async def upload_files(
    files: List[UploadFile] = File(...),
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Subir uno o más archivos a Supabase Storage
    """
    if len(files) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Máximo 5 archivos por solicitud"
        )
    
    uploaded_urls = []
    
    try:
        for file in files:
            # Validar tipo de archivo
            content_type = file.content_type
            if content_type not in ALLOWED_IMAGE_TYPES + ALLOWED_VIDEO_TYPES + ALLOWED_DOCUMENT_TYPES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Tipo de archivo no permitido: {content_type}"
                )
            
            # Leer contenido del archivo
            contents = await file.read()
            
            # Validar tamaño
            if len(contents) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Archivo {file.filename} excede el tamaño máximo de 10MB"
                )
            
            # Generar nombre único para el archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{current_user['id_user']}_{timestamp}_{unique_id}{file_extension}"
            
            # Determinar carpeta según tipo de archivo
            if content_type in ALLOWED_IMAGE_TYPES:
                folder = "images"
            elif content_type in ALLOWED_VIDEO_TYPES:
                folder = "videos"
            else:
                folder = "documents"
            
            # Subir a Supabase Storage
            storage_path = f"{folder}/{unique_filename}"
            
            try:
                # Subir archivo
                result = db.storage.from_("media").upload(
                    path=storage_path,
                    file=contents,
                    file_options={"content-type": content_type}
                )
                
                # Obtener URL pública
                public_url = db.storage.from_("media").get_public_url(storage_path)
                
                uploaded_urls.append({
                    "url": public_url,
                    "filename": file.filename,
                    "content_type": content_type,
                    "size": len(contents)
                })
                
            except Exception as storage_error:
                print(f"Error de Supabase Storage: {str(storage_error)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error al subir archivo: {str(storage_error)}"
                )
        
        return {
            "message": f"Se subieron {len(uploaded_urls)} archivos exitosamente",
            "files": uploaded_urls
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error inesperado en upload: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(e)}"
        )


@router.delete("/files")
async def delete_file(
    file_url: str,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Eliminar un archivo de Supabase Storage
    """
    try:
        # Extraer el path del archivo de la URL
        # URL format: https://PROJECT.supabase.co/storage/v1/object/public/media/folder/filename
        parts = file_url.split("/media/")
        if len(parts) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="URL de archivo inválida"
            )
        
        file_path = parts[1]
        
        # Eliminar de Supabase Storage
        result = db.storage.from_("media").remove([file_path])
        
        return {"message": "Archivo eliminado exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar archivo: {str(e)}"
        )
