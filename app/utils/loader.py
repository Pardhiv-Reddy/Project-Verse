from pathlib import Path
class Loader:
    from pathlib import Path
    base_dir = Path(__file__).resolve().parent.parent
    prompt_path = Path(base_dir/"prompts")
    @staticmethod
    def Load(filename:str):
        return (Loader.prompt_path/filename).read_text(encoding="utf-8")