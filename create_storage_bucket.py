"""
Script para crear el bucket de almacenamiento en Supabase
Ejecutar una sola vez para configurar el storage
"""
import os
from dotenv import load_dotenv
from supabase import create_client

# Cargar variables de entorno
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE")

def create_media_bucket():
    """Crea el bucket 'media' en Supabase Storage"""
    try:
        print("🔗 Conectando a Supabase...")
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        
        print("📦 Creando bucket 'media'...")
        
        # Intentar crear el bucket
        result = supabase.storage.create_bucket(
            "media",
            options={
                "public": True,  # Bucket público para acceso directo a URLs
                "file_size_limit": 10485760,  # 10MB en bytes
                "allowed_mime_types": [
                    # Imágenes
                    "image/jpeg",
                    "image/png", 
                    "image/gif",
                    "image/webp",
                    # Videos
                    "video/mp4",
                    "video/mpeg",
                    "video/quicktime",
                    "video/webm",
                    # Documentos
                    "application/pdf",
                    "application/msword",
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                ]
            }
        )
        
        print("✅ Bucket 'media' creado exitosamente")
        print(f"   Resultado: {result}")
        
        # Crear las carpetas dentro del bucket
        print("\n📁 Creando estructura de carpetas...")
        
        # Subir archivos vacíos para crear las carpetas
        folders = ["images", "videos", "documents"]
        for folder in folders:
            try:
                # Crear un archivo .gitkeep para mantener la carpeta
                supabase.storage.from_("media").upload(
                    f"{folder}/.gitkeep",
                    b"",
                    {"content-type": "text/plain"}
                )
                print(f"   ✅ Carpeta '{folder}/' creada")
            except Exception as e:
                print(f"   ℹ️ Carpeta '{folder}/' ya existe o error: {e}")
        
        print("\n🎉 Configuración de almacenamiento completada")
        print("   Ahora puedes subir archivos a /api/v1/upload/files")
        
    except Exception as e:
        error_str = str(e)
        if "already exists" in error_str.lower() or "duplicate" in error_str.lower():
            print("ℹ️ El bucket 'media' ya existe")
            print("   No es necesario crearlo nuevamente")
        else:
            print(f"❌ Error al crear bucket: {e}")
            print("\n💡 Si el error persiste, crea el bucket manualmente:")
            print("   1. Ve a https://supabase.com/dashboard")
            print("   2. Selecciona tu proyecto")
            print("   3. Ve a Storage → Buckets")
            print("   4. Clic en 'New bucket'")
            print("   5. Nombre: media")
            print("   6. Marca 'Public bucket'")
            print("   7. Clic en 'Create bucket'")

if __name__ == "__main__":
    create_media_bucket()
