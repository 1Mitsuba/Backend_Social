import traceback
from supabase import create_client
from app.config import settings
k = settings.SUPABASE_SERVICE_ROLE or settings.SUPABASE_KEY or ''
try:
    c = create_client(settings.SUPABASE_URL, k)
    print('CLIENT_CREATED:', type(c))
except Exception as e:
    print('EXC_REPR=', repr(e))
    traceback.print_exc()
