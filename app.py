import os
from pathlib import Path
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(page_title="Inventario 2025", layout="wide")
st.title("📦 Inventario Anual 2025")
st.subheader("Mapa de áreas interactivas")

# --- Rutas seguras relativas al archivo ---
BASE = Path(__file__).parent
EXCEL_PATH = BASE / "data" / "roles_areas.xlsx"
SVG_PATH   = BASE / "data" / "mapa.svg"

# --- Diagnóstico rápido si falta algo ---
missing = []
if not EXCEL_PATH.exists(): missing.append(str(EXCEL_PATH))
if not SVG_PATH.exists():   missing.append(str(SVG_PATH))
if missing:
    st.error("No se encontraron estos archivos en el servidor:")
    for m in missing: st.code(m)
    st.caption("Confirma que están subidos al repo en la carpeta data/ y vuelve a desplegar.")
    st.write("Contenido de la carpeta actual:", os.listdir(BASE))
    st.stop()

@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    return pd.read_excel(path)   # requiere openpyxl

df = load_data(EXCEL_PATH)

# --- Cargar SVG ---
svg_content = SVG_PATH.read_text(encoding="utf-8")

# Pequeño estilo de hover para que “se sienta” interactivo
svg_content = svg_content.replace(
    "<svg",
    '<svg><style>.area:hover{opacity:.9;stroke:#111827;stroke-width:2;cursor:pointer}</style>',
    1
) if "<style>" not in svg_content else svg_content

# Render (sin escuchar clicks aún)
components.html(f"<div id='svg-container'>{svg_content}</div>", height=520)

st.write("Datos cargados:", df.shape)
