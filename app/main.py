from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.health import router as health_router
from app.routers.drive import router as drive_router
from app.routers.table import router as table_router
from app.routers.qa import router as qa_router


def create_app() -> FastAPI:
	app = FastAPI(title="AI Agent Google Drive Excel API", version="0.1.0")

	app.add_middleware(
		CORSMiddleware,
		allow_origins=["*"],
		allow_credentials=True,
		allow_methods=["*"],
		allow_headers=["*"],
	)

	app.include_router(health_router)
	app.include_router(drive_router, prefix="/drive", tags=["drive"])
	app.include_router(table_router, prefix="/table", tags=["table"])
	app.include_router(qa_router, prefix="/qa", tags=["qa"])

	return app


app = create_app()




