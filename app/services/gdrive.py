import os
from typing import List, Optional
import io
import asyncio

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

GOOGLE_SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "/app/credentials.json")


class GoogleDriveClient:
	"""Обёртка над Google Drive API с асинхронными методами.

	Лениво инициализирую клиент Drive по GOOGLE_APPLICATION_CREDENTIALS.
	"""

	def __init__(self, credentials_path: Optional[str] = None, scopes: Optional[List[str]] = None):
		self._credentials_path = credentials_path or CREDENTIALS_PATH
		self._scopes = scopes or GOOGLE_SCOPES
		self._service = None

	def _ensure_service(self):
		if self._service is not None:
			return
		if not os.path.exists(self._credentials_path):
			raise FileNotFoundError("credentials.json not found. Mount it and set GOOGLE_APPLICATION_CREDENTIALS.")
		creds = service_account.Credentials.from_service_account_file(self._credentials_path, scopes=self._scopes)
		self._service = build('drive', 'v3', credentials=creds, cache_discovery=False)

	def _list_excel_files_sync(self, query: Optional[str]) -> List[dict]:
		self._ensure_service()
		mimes = [
			"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
			"application/vnd.ms-excel",
		]
		q_parts = [f"mimeType='{m}'" for m in mimes]
		q = f"({ ' OR '.join(q_parts) }) and trashed=false"
		if query:
			q += f" and name contains '{query}'"
		resp = self._service.files().list(q=q, fields="files(id, name, mimeType)").execute()
		return resp.get('files', [])

	def _download_file_sync(self, file_id: str) -> Optional[bytes]:
		self._ensure_service()
		request = self._service.files().get_media(fileId=file_id)
		fh = io.BytesIO()
		downloader = MediaIoBaseDownload(fh, request)
		done = False
		while not done:
			status, done = downloader.next_chunk()
		return fh.getvalue()

	async def list_excel_files(self, query: Optional[str]) -> List[dict]:
		return await asyncio.to_thread(self._list_excel_files_sync, query)

	async def get_file_content(self, file_id: str) -> Optional[bytes]:
		return await asyncio.to_thread(self._download_file_sync, file_id)


_gdrive_singleton: Optional[GoogleDriveClient] = None


def provide_gdrive_client() -> GoogleDriveClient:
	"""Один экземпляр GoogleDriveClient для зависимостей."""
	global _gdrive_singleton
	if _gdrive_singleton is None:
		_gdrive_singleton = GoogleDriveClient()
	return _gdrive_singleton




