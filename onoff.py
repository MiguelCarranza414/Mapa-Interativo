import subprocess
from pathlib import Path
from update_rol import update

REPO = Path(r"C:\Inventario")
MENSAJE = "On/Off mapa Streamlit"

update()

def run(cmd: list[str]) -> None:
    r = subprocess.run(cmd, cwd=REPO, text=True, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"Error ejecutando: {' '.join(cmd)}\n{r.stderr}")
    if r.stdout.strip():
        print(r.stdout.strip())

#py -m streamlit run app.py
run(["py", "-m","streamlit", "run", "app.py"])
