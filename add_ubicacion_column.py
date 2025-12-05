import os
from dotenv import load_dotenv
from supabase import create_client

# Cargar variables de entorno
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    # Ejecutar SQL para agregar columna ubicacion_recogida
    sql = """
    ALTER TABLE pasajeroruta 
    ADD COLUMN IF NOT EXISTS ubicacion_recogida VARCHAR(200);
    """
    
    # Usar RPC para ejecutar SQL directamente
    result = supabase.rpc('exec_sql', {'query': sql}).execute()
    print("✅ Columna ubicacion_recogida agregada exitosamente")
    print(result)
except Exception as e:
    print(f"⚠️ Error al ejecutar SQL via Python: {e}")
    print("\n📋 Ejecuta este SQL directamente en Supabase Dashboard > SQL Editor:")
    print("\nALTER TABLE pasajeroruta ADD COLUMN IF NOT EXISTS ubicacion_recogida VARCHAR(200);")
    print("\n🔗 Ve a: https://supabase.com/dashboard/project/_/sql")
