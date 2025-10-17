from fastapi import APIRouter, HTTPException, Depends
from typing import Optional

from app.services.table_reader import TableReader, provide_table_reader

router = APIRouter()


@router.get("/read")
async def read_table(file_id: str, sheet_name: Optional[str] = None, reader: TableReader = Depends(provide_table_reader)):
	try:
		rows = await reader.read_table(file_id=file_id, sheet_name=sheet_name)
		return {"rows": rows}
	except FileNotFoundError:
		raise HTTPException(status_code=404, detail="File not found")
	except Exception as exc:
		raise HTTPException(status_code=400, detail=str(exc))


@router.get("/cell")
async def read_cell(file_id: str, cell: str, sheet_name: Optional[str] = None, reader: TableReader = Depends(provide_table_reader)):
	try:
		value = await reader.read_cell(file_id=file_id, cell=cell, sheet_name=sheet_name)
		if value is None:
			raise HTTPException(status_code=404, detail="Cell not found or empty")
		return {"cell": cell, "value": value}
	except FileNotFoundError:
		raise HTTPException(status_code=404, detail="File not found")
	except Exception as exc:
		raise HTTPException(status_code=400, detail=str(exc))




