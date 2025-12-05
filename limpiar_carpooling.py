"""
Script para limpiar solicitudes de pasajeros y notificaciones antiguas
"""
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
service_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE") or os.getenv("SUPABASE_KEY")

supabase = create_client(url, service_key)

try:
    print("🧹 Limpiando base de datos...")
    
    # 1. Eliminar todas las solicitudes de pasajeros
    print("\n1️⃣ Eliminando solicitudes de pasajeros...")
    result = supabase.table("pasajeroruta").delete().neq("id_pasajero_ruta", "").execute()
    print(f"   ✅ Solicitudes de pasajeros eliminadas")
    
    # 2. Eliminar notificaciones de carpooling
    print("\n2️⃣ Eliminando notificaciones de carpooling...")
    result = supabase.table("notificacion").delete().eq("tipo", "solicitud_ruta").execute()
    print(f"   ✅ Notificaciones de solicitud_ruta eliminadas")
    
    result = supabase.table("notificacion").delete().eq("tipo", "respuesta_ruta").execute()
    print(f"   ✅ Notificaciones de respuesta_ruta eliminadas")
    
    print("\n✅ ¡Base de datos limpia!")
    print("\n🎯 Ahora puedes:")
    print("   1. Reiniciar el backend")
    print("   2. Hacer una nueva solicitud de carpooling")
    print("   3. Todo funcionará correctamente con los botones")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
