from pathlib import Path
from fastapi import status, HTTPException, UploadFile
class FileService:
    def __init__(self):
        self.base_path = Path("storage/submissions")
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.allowed = {".pdf",".doc",".docx",".pptx",".ppt"}
        self.MAX_FILE_SIZE = 20 * 1024 * 1024
    async def save(self, team_id: str, file: UploadFile) -> str:
        team_path = self.base_path / team_id
        team_path.mkdir(parents=True, exist_ok=True)
        if not file.filename:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="No file provided.")
        extension = Path(file.filename).suffix.lower()
        if extension not in self.allowed:
            raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,detail=f"Allowed File Types are {self.allowed}")
        file_name = f"{team_id}-Abstract{extension}"
        file_path = team_path / file_name
        total_size = 0
        with file_path.open("wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                total_size += len(chunk)
                if total_size > self.MAX_FILE_SIZE:
                    file_path.unlink(missing_ok=True)
                    raise HTTPException(status_code=status.HTTP_413_CONTENT_TOO_LARGE,detail="File Size Exceeds 20MB.")
                buffer.write(chunk)
        return str(file_path)