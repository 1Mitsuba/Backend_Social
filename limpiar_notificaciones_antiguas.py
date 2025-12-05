import os
from dotenv import load_dotenv
from supabase import create_client

# Cargar variables de entorno
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    # Eliminar notificaciones de carpooling antiguas sin id_referencia válido
    result = supabase.table("notificacion")\
        .delete()\
        .eq("tipo", "solicitud_ruta")\
        .is_("id_referencia", "null")\
        .execute()
    
    print(f"✅ Eliminadas {len(result.data) if result.data else 0} notificaciones antiguas sin referencia")
    
    # También podemos eliminar todas las notificaciones de solicitud_ruta antiguas
    result2 = supabase.table("notificacion")\
        .delete()\
        .eq("tipo", "solicitud_ruta")\
        .execute()
    
    print(f"✅ Limpiadas todas las notificaciones de solicitud_ruta")
    
except Exception as e:
    print(f"❌ Error: {e}")
