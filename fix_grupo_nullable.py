import os
from dotenv import load_dotenv
from supabase import create_client

# Cargar variables de entorno
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    # Ejecutar SQL para hacer gestion_grupo nullable
    sql = """
    ALTER TABLE grupo 
    ALTER COLUMN gestion_grupo DROP NOT NULL;
    """
    
    result = supabase.rpc('exec_sql', {'query': sql}).execute()
    print("✅ Columna gestion_grupo ahora permite NULL")
    print(result)
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n⚠️ Necesitas ejecutar este SQL directamente en Supabase Dashboard:")
    print("\nALTER TABLE grupo ALTER COLUMN gestion_grupo DROP NOT NULL;")
