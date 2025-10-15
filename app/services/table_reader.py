import pandas as pd
import io
from typing import List, Optional, Any

from app.services.gdrive import get_file_content


async def read_table_from_gdrive(file_id: str, sheet_name: Optional[str] = None) -> List[dict]:
	content = await get_file_content(file_id)
	if content is None:
		raise FileNotFoundError("File not found")
	bio = io.BytesIO(content)
	df = pd.read_excel(bio, sheet_name=sheet_name)
	# Normalize to two columns: tool_name, url
	if isinstance(df, dict):
		# If multiple sheets returned, take the first
		first_key = list(df.keys())[0]
		df = df[first_key]
	# Try to infer columns
	columns = list(df.columns)
	if len(columns) < 2:
		raise ValueError("The Excel sheet must contain at least two columns: tool name and URL")
	df = df.rename(columns={columns[0]: 'tool_name', columns[1]: 'url'})
	rows = [
		{"tool_name": str(row['tool_name']).strip(), "url": str(row['url']).strip()}
		for _, row in df.iterrows()
		if not pd.isna(row[columns[0]]) and not pd.isna(row[columns[1]])
	]
	return rows


async def read_cell_from_gdrive(file_id: str, cell: str, sheet_name: Optional[str] = None) -> Optional[Any]:
	content = await get_file_content(file_id)
	if content is None:
		raise FileNotFoundError("File not found")
	bio = io.BytesIO(content)
	df = pd.read_excel(bio, sheet_name=sheet_name, header=None)
	# Convert cell like "B3" to indexes
	column_letters = ''.join([c for c in cell if c.isalpha()]).upper()
	row_numbers = ''.join([c for c in cell if c.isdigit()])
	if not column_letters or not row_numbers:
		raise ValueError("Invalid cell address, use like A1, B2")
	col_index = 0
	for ch in column_letters:
		col_index = col_index * 26 + (ord(ch) - ord('A') + 1)
	col_index -= 1
	row_index = int(row_numbers) - 1
	try:
		value = df.iat[row_index, col_index]
		return None if pd.isna(value) else value
	except Exception:
		return None




