"""
Script para agregar la columna 'editado' a la tabla mensaje
"""
import os
from supabase import create_client

# Configurar cliente de Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://qhscsxvwxupokmlhxnse.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFoc2NzeHZ3eHVwb2ttbGh4bnNlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzMyNjgyNTAsImV4cCI6MjA0ODg0NDI1MH0.5V3BfJ_MJtk3Sf7Shs3v1WFdFxEsQq5PYwvv1EVS6pM")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# SQL para agregar la columna editado
sql_query = """
-- Agregar columna editado a la tabla mensaje si no existe
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name='mensaje' AND column_name='editado'
    ) THEN
        ALTER TABLE mensaje ADD COLUMN editado BOOLEAN DEFAULT FALSE;
    END IF;
END $$;
"""

print("🔄 Ejecutando migración para agregar columna 'editado'...")
print(f"📋 SQL:\n{sql_query}")

try:
    # Ejecutar usando RPC o directamente en Supabase SQL Editor
    print("\n⚠️  Este script muestra el SQL necesario.")
    print("Por favor, ejecuta este SQL en el SQL Editor de Supabase:")
    print("\n" + "="*60)
    print(sql_query)
    print("="*60)
    print("\n✅ Una vez ejecutado, la columna 'editado' estará disponible en la tabla mensaje")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    print("\nPor favor, ejecuta el SQL manualmente en Supabase SQL Editor")
