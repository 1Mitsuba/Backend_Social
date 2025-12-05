"""
Script para agregar columna id_referencia a la tabla notificacion
"""
from supabase import create_client
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

url = os.getenv("SUPABASE_URL")
service_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE") or os.getenv("SUPABASE_KEY")

supabase = create_client(url, service_key)

try:
    print("🔧 Agregando columna id_referencia a la tabla notificacion...")
    
    # Ejecutar SQL para agregar la columna
    result = supabase.rpc('exec_sql', {
        'sql': 'ALTER TABLE notificacion ADD COLUMN IF NOT EXISTS id_referencia TEXT;'
    }).execute()
    
    print("✅ Columna agregada exitosamente")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n⚠️ Necesitas agregar la columna manualmente.")
    print("Abre el SQL Editor en Supabase y ejecuta:\n")
    print("ALTER TABLE notificacion ADD COLUMN id_referencia TEXT;")
