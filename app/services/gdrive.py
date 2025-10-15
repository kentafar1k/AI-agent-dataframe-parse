import os
from typing import List, Optional
from functools import lru_cache
import io
import asyncio

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

GOOGLE_SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "/app/credentials.json")


@lru_cache(maxsize=1)
def _get_drive_service():
	if not os.path.exists(CREDENTIALS_PATH):
		raise FileNotFoundError("credentials.json not found. Mount it and set GOOGLE_APPLICATION_CREDENTIALS.")
	creds = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=GOOGLE_SCOPES)
	service = build('drive', 'v3', credentials=creds, cache_discovery=False)
	return service


def _list_excel_files_sync(query: Optional[str]) -> List[dict]:
	service = _get_drive_service()
	# MIME types for Excel
	mimes = [
		"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
		"application/vnd.ms-excel",
	]
	q_parts = [f"mimeType='{m}'" for m in mimes]
	q = f"({ ' OR '.join(q_parts) }) and trashed=false"
	if query:
		q += f" and name contains '{query}'"
	resp = service.files().list(q=q, fields="files(id, name, mimeType)").execute()
	return resp.get('files', [])


def _download_file_sync(file_id: str) -> Optional[bytes]:
	service = _get_drive_service()
	request = service.files().get_media(fileId=file_id)
	fh = io.BytesIO()
	downloader = MediaIoBaseDownload(fh, request)
	done = False
	while not done:
		status, done = downloader.next_chunk()
	return fh.getvalue()


async def list_excel_files(query: Optional[str]) -> List[dict]:
	return await asyncio.to_thread(_list_excel_files_sync, query)


async def get_file_content(file_id: str) -> Optional[bytes]:
	return await asyncio.to_thread(_download_file_sync, file_id)




