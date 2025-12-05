"""
Script para agregar columna id_referencia y limpiar notificaciones antiguas
"""
from supabase import create_client
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Crear cliente de Supabase con service role (tiene permisos completos)
url = os.getenv("SUPABASE_URL")
# Intentar con diferentes keys
service_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE") or os.getenv("SUPABASE_KEY")

print(f"🔗 Conectando a Supabase...")
print(f"   URL: {url}")
print(f"   Key encontrada: {'✅ Sí' if service_key else '❌ No'}")

supabase = create_client(url, service_key)

try:
    # Paso 1: Ver estructura actual de notificaciones
    print("\n📋 Consultando notificaciones existentes...")
    notifs = supabase.table("notificacion").select("*").eq("tipo", "solicitud_ruta").limit(5).execute()
    
    if notifs.data:
        print(f"✅ Encontradas {len(notifs.data)} notificaciones de tipo 'solicitud_ruta'")
        print(f"📝 Columnas actuales: {list(notifs.data[0].keys())}")
        
        # Verificar si id_referencia existe
        tiene_id_referencia = 'id_referencia' in notifs.data[0]
        print(f"{'✅' if tiene_id_referencia else '❌'} Columna 'id_referencia': {'existe' if tiene_id_referencia else 'NO existe'}")
    else:
        print("ℹ️ No hay notificaciones de carpooling todavía")
    
    # Paso 2: Eliminar todas las notificaciones de solicitud_ruta antiguas
    print("\n🗑️ Eliminando notificaciones antiguas de carpooling...")
    result = supabase.table("notificacion").delete().eq("tipo", "solicitud_ruta").execute()
    print(f"✅ Notificaciones eliminadas")
    
    print("\n✅ ¡Listo! Ahora:")
    print("   1. Reinicia el backend (Ctrl+C y 'python run.py')")
    print("   2. Haz una nueva solicitud de carpooling")
    print("   3. Los botones deberían aparecer y funcionar")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print(f"\nℹ️ Si el error persiste, ejecuta esto en Supabase SQL Editor:")
    print("""
    -- Agregar columna si no existe
    ALTER TABLE notificacion 
    ADD COLUMN IF NOT EXISTS id_referencia TEXT;
    
    -- Limpiar notificaciones viejas
    DELETE FROM notificacion WHERE tipo = 'solicitud_ruta';
    """)
