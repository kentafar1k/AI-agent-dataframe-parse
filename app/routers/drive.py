from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from app.services.gdrive import list_excel_files, get_file_content

router = APIRouter()


@router.get("/files")
async def list_files(q: Optional[str] = Query(default=None, description="Query to filter file names")):
	files = await list_excel_files(query=q)
	return {"files": files}


@router.get("/files/{file_id}")
async def get_file(file_id: str):
	content = await get_file_content(file_id)
	if content is None:
		raise HTTPException(status_code=404, detail="File not found or not accessible")
	return {"file_id": file_id, "size_bytes": len(content)}
