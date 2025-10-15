from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.services.table_reader import read_table_from_gdrive, read_cell_from_gdrive

router = APIRouter()


@router.get("/read")
async def read_table(file_id: str, sheet_name: Optional[str] = None):
	try:
		rows = await read_table_from_gdrive(file_id=file_id, sheet_name=sheet_name)
		return {"rows": rows}
	except FileNotFoundError:
		raise HTTPException(status_code=404, detail="File not found")
	except Exception as exc:
		raise HTTPException(status_code=400, detail=str(exc))


@router.get("/cell")
async def read_cell(file_id: str, cell: str, sheet_name: Optional[str] = None):
	try:
		value = await read_cell_from_gdrive(file_id=file_id, cell=cell, sheet_name=sheet_name)
		if value is None:
			raise HTTPException(status_code=404, detail="Cell not found or empty")
		return {"cell": cell, "value": value}
	except FileNotFoundError:
		raise HTTPException(status_code=404, detail="File not found")
	except Exception as exc:
		raise HTTPException(status_code=400, detail=str(exc))




