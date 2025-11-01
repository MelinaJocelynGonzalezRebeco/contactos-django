from django.conf import settings
from datetime import datetime
from pathlib import Path
import secrets
try:
    from supabase import create_client
except Exception:
    create_client = None

def can_use_supabase():
    return bool(settings.SUPABASE_URL and settings.SUPABASE_KEY and create_client is not None)

def upload_to_supabase(file_obj):
    if not can_use_supabase():
        return None
    url = settings.SUPABASE_URL
    key = settings.SUPABASE_KEY
    bucket = settings.SUPABASE_STORAGE_BUCKET or "contactos"
    folder = settings.SUPABASE_STORAGE_FOLDER or "avatars"
    try:
        client = create_client(url, key)
        ext = Path(file_obj.name).suffix or ".bin"
        filename = f"{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}-{secrets.token_hex(6)}{ext}"
        path = f"{folder}/{filename}"
        content = file_obj.read()
        file_obj.seek(0)
        client.storage.from_(bucket).upload(path=path, file=content, file_options={"upsert": True})
        return client.storage.from_(bucket).get_public_url(path)
    except Exception:
        return None
