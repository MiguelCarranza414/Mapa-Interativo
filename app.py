import unicodedata
import base64
from pathlib import Path
import pandas as pd
import streamlit as st
import xml.etree.ElementTree as ET

# === CONFIGURACIÓN ===
EXCEL_PATH = Path(r"C:\Inventario\data\roles_areas.xlsx")
SVG_PATH   = Path("data/mapa.svg")
HELP_IMAGE_PATH = Path(r"C:\Inventario\data\ayuda.png")
st.set_page_config(layout="wide")
with st.container():
    st.markdown(
        """
        <div>
            <h2 style='text-align: center;'>📦 Inventario Anual 2025. Mapa interactivo de actividades, áreas y turnos.</h1>
            <p style='text-align: center;'>Del 3 al 7 de enero del 2026<p>
            <h6 style='text-align: center;'><b>(Solo mesa de control del 2 al 7 de Enero del 2026)</b></h6>
        </div>
        """,
        unsafe_allow_html=True
    )

#st.subheader("📦 Inventario Anual 2025. Mapa interactivo de actividades, áreas y turnos.")
#st.markdown('''Del 3 al 7 de enero del 2026 :gray-background[(Solo mesa de control del 2 al 7 de Enero del 2026)]''')
#st.markdown('''
    #:red[Streamlit] :orange[can] :green[write] :blue[text] :violet[in]
    #:gray[pretty] :rainbow[colors] and :blue-background[highlight] text.''')

st.divider()
# === ESTILOS PERSONALIZADOS ===
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
  --navy-900: #ecf3ff;
  --navy-800: #e2edff;
  --navy-700: #d2e3ff;
  --graphite-900: #f7f9fc;
  --graphite-800: #f1f4fa;
  --graphite-700: #e6ebf5;
  --accent: #2563eb;
  --muted: #6b7280;
  --surface: #ffffff;
  --border: #d7deea;
  --shadow: 0 10px 30px rgba(15, 23, 42, 0.12);
}

html, body, [class*="css"], [data-testid="stAppViewContainer"] {
  font-family: 'Inter', sans-serif;
  background: radial-gradient(circle at 20% 20%, rgba(37, 99, 235, 0.08), transparent 26%),
              radial-gradient(circle at 80% 0%, rgba(37, 99, 235, 0.06), transparent 22%),
              var(--graphite-900);
  color: #111827;
}

[data-testid="stAppViewContainer"] > .main {
  padding-top: 1.5rem;
}

h1, h2, h3, h4, h5, h6 {
  font-weight: 700;
  letter-spacing: -0.01em;
  color: #0f172a;
}

/* Containers */
.block-container {
  padding: 1.5rem 2rem 2rem 2rem;
}

.hero {
  background: linear-gradient(120deg, rgba(37, 99, 235, 0.12), rgba(232, 240, 255, 0.8));
  border: 1px solid rgba(37, 99, 235, 0.18);
  border-radius: 18px;
  padding: 1rem 1.25rem;
  box-shadow: var(--shadow);
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.hero .emoji {
  font-size: 1.7rem;
}

.hero .text {
  color: #0f172a;
}

.hero .text h3 {
  margin: 0 0 0.1rem 0;
}

.pill {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: #eef2ff;
  border: 1px solid #d9e3ff;
  color: #1d4ed8;
  padding: 0.35rem 0.8rem;
  border-radius: 999px;
  font-weight: 600;
  font-size: 0.9rem;
}

[data-testid="stMarkdownContainer"] > p,
[data-testid="stMarkdownContainer"] > div {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.92), rgba(247, 250, 255, 0.96));
  border: 1px solid var(--border);
  box-shadow: var(--shadow);
  border-radius: 16px;
  padding: 1rem 1.25rem;
  color: #0f172a;
}

/* Metric cards */
[data-testid="metric-container"] {
  background: linear-gradient(145deg, var(--surface), var(--graphite-800));
  border-radius: 18px;
  padding: 1rem 1.25rem;
  border: 1px solid var(--border);
  box-shadow: var(--shadow);
}
[data-testid="metric-container"] .stMetric-label {
  color: #475569;
  font-weight: 600;
  letter-spacing: 0.01em;
}
[data-testid="metric-container"] .stMetric-value {
  color: #0b1b35;
  font-weight: 700;
}

/* Sidebar */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, var(--navy-900), #f8fbff);
  border-right: 1px solid var(--border);
  box-shadow: inset -1px 0 0 rgba(15, 23, 42, 0.04);
}
[data-testid="stSidebar"] * {
  color: #0f172a !important;
}
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stMultiSelect [data-baseweb="input"] {
  background: var(--surface);
  border-radius: 12px;
  border: 1px solid var(--border);
  box-shadow: inset 0 1px 0 rgba(15, 23, 42, 0.03);
}

/* Buttons */
.stButton > button,
button[kind="primary"] {
  background: linear-gradient(180deg, var(--navy-900), #f8fbff);
  color: black;
  border: none;
  border-radius: 14px;
  padding: 0.65rem 1.2rem;
  font-weight: 700;
  letter-spacing: 0.01em;
  box-shadow: 0 12px 25px rgba(59, 130, 246, 0.35);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.stButton > button:hover,
button[kind="primary"]:hover {
  transform: translateY(-1px);
  box-shadow: 0 14px 30px rgba(59, 130, 246, 0.45);
}
.stButton > button:active,
button[kind="primary"]:active {
  transform: translateY(0);
}

/* Tables */
div[data-testid="stDataFrame"],
div[data-testid="stTable"] {
  background: var(--surface);
  border-radius: 14px;
  border: 1px solid var(--border);
  box-shadow: var(--shadow);
  overflow: hidden;
}
div[data-testid="stDataFrame"] table,
div[data-testid="stTable"] table {
  color: #0f172a;
}
div[data-testid="stDataFrame"] tbody tr:hover,
div[data-testid="stTable"] tbody tr:hover {
  background: rgba(37, 99, 235, 0.08);
}

/* Tooltips */
[data-baseweb="tooltip"] {
  background: var(--surface) !important;
  color: #0f172a !important;
  border: 1px solid var(--border) !important;
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.15) !important;
  border-radius: 10px !important;
  font-weight: 600;
}

/* SVG container */
#svg-wrap {
  background: linear-gradient(145deg, rgba(232, 240, 255, 0.95), rgba(255, 255, 255, 0.96));
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 18px;
  padding: 1.25rem;
  box-shadow: var(--shadow);
}
#svg-wrap svg {
  width: 100%;
  height: auto;
}

.map-legend {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 0.6rem;
  margin-top: 0.75rem;
}

.map-legend .legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.65rem 0.75rem;
  border-radius: 14px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.92), rgba(240, 245, 255, 0.96));
  border: 1px solid var(--border);
  box-shadow: var(--shadow);
  font-weight: 600;
  color: #0f172a;
}

.legend-swatch {
  width: 14px;
  height: 14px;
  border-radius: 4px;
  border: 1px solid rgba(15, 23, 42, 0.2);
}

/* Chips & inline pills */
.stAlert, .stInfo, .stSuccess, .stWarning {
  border-radius: 14px;
  border: 1px solid rgba(15, 23, 42, 0.08);
  box-shadow: var(--shadow);
}

/* Links & captions */
a, .stCaption, .stMarkdown p {
  color: #1d4ed8;
}
/* Floating help button */
.help-widget {
  position: fixed;
  bottom: 18px;
  left: 18px;
  z-index: 1000;
}

/* Checkbox oculto que controla el modal */
.help-checkbox {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.help-btn {
  background: linear-gradient(180deg, var(--surface), var(--navy-900));
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 0.65rem 1rem;
  font-weight: 700;
  color: #0f172a;
  box-shadow: 0 10px 25px rgba(15, 23, 42, 0.15);
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  cursor: pointer;
}

.help-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.2);
}

/* Modal inicialmente oculto */
.help-modal {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(1px);
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  z-index: 1100;

  display: none;
}

/* Cuando el checkbox está marcado, mostramos el modal */
.help-checkbox:checked ~ .help-modal {
  display: flex;
}

.help-modal-content {
  position: relative;
  background: #ffffff;
  border-radius: 16px;
  border: 1px solid var(--border);
  box-shadow: 0 20px 50px rgba(15, 23, 42, 0.22);
  max-width: min(780px, 90vw);
  width: 100%;
  padding: 1rem 1rem 1.25rem 1rem;
}

.help-modal-content img {
  width: 100%;
  height: auto;
  display: block;
  border-radius: 12px;
}

/* El botón de cerrar es también un <label> que desmarca el checkbox */
.help-close {
  position: absolute;
  top: 10px;
  right: 10px;
  background: #f1f5f9;
  border: 1px solid var(--border);
  border-radius: 50%;
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  cursor: pointer;
  font-size: 1.1rem;
  box-shadow: 0 6px 15px rgba(15, 23, 42, 0.18);
}

.help-close:hover {
  background: #e2e8f0;
}
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# --- FUNCIONES DE AYUDA ---

@st.cache_data(show_spinner=False)
def load_excel(path: Path) -> pd.DataFrame:
    """Carga el DataFrame desde el archivo Excel."""
    return pd.read_excel(path)

@st.cache_data(show_spinner=False)
def load_svg(path: Path) -> str:
    """Carga el contenido del archivo SVG."""
    return path.read_text(encoding="utf-8")

@st.cache_data(show_spinner=False)
def load_help_image(path: Path) -> str:
    """Devuelve la imagen codificada en base64 para incrustarla en HTML."""
    return base64.b64encode(path.read_bytes()).decode("utf-8")

def build_display_columns(dataframe: pd.DataFrame, location_column: str) -> list[str]:
    """Devuelve la lista de columnas a mostrar respetando la disponibilidad en el DataFrame."""
    desired_order = ["Número", "Nombre", "Activity",location_column, "Turno"]
    return [col for col in desired_order if col in dataframe.columns]

def normalize_key(s: str) -> str:
    """Estandariza una cadena a MAYÚSCULAS sin acentos, con espacios a guiones bajos."""
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", str(s).strip())
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return s.replace(" ", "_").upper()

def normalize_search_text(value: str) -> str:
    """Normaliza texto para búsqueda flexible (sin acentos y en minúsculas)."""
    if not value:
        return ""
    normalized = unicodedata.normalize("NFKD", str(value).strip())
    normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return normalized.casefold()

def get_svg_title(svg_text: str, area_key: str) -> str:
    """Busca el título amigable (<title>) dentro de un elemento del SVG."""
    if not svg_text or not area_key:
        return area_key or ""
    try:
        root = ET.fromstring(svg_text)

        # Busca por data-area
        for el in root.findall(f'.//*[@data-area="{area_key}"]'):
            title_el = el.find('.//{http://www.w3.org/2000/svg}title')
            if title_el is None:
                title_el = el.find('title')
            if title_el is not None and (title_el.text or "").strip():
                return title_el.text.strip()

        # Fallback: buscar por id
        el_by_id = root.find(f'.//*[@id="{area_key}"]')
        if el_by_id is not None:
            title_el = el_by_id.find('.//{http://www.w3.org/2000/svg}title')
            if title_el is None:
                title_el = el_by_id.find('title')
            if title_el is not None and (title_el.text or "").strip():
                return title_el.text.strip()

    except Exception:
        pass
    return area_key


# --- CARGA Y PREPARACIÓN DE DATOS ---

# 1. Carga Segura de Excel
try:
    df = load_excel(EXCEL_PATH)
except FileNotFoundError:
    st.error(f"❌ Archivo Excel no encontrado en {EXCEL_PATH.resolve()}")
    st.stop()
except Exception as e:
    st.error(f"❌ No pude cargar el Excel: {e}")
    st.stop()
# Normalizar tipos problemáticos para Arrow/Streamlit
if "Turno" in df.columns:
    # La columna puede venir con mezclas de números y textos; la convertimos a str
    df["Turno"] = df["Turno"].map(lambda v: "" if pd.isna(v) else str(v))
header_col, back_col = st.columns([0.10, 0.90])
with header_col:
    if st.button("# Inicio"):
        st.query_params.clear()
        st.session_state.pop("last_area", None)
        st.rerun()
with back_col:
    filter_name_col, filter_activity_col = st.columns([0.6, 0.6])
    with filter_name_col:
        name_query = st.text_input("#### Buscar por Número")
    with filter_activity_col:
        activity_options = []
        if "Activity" in df.columns:
            activity_options = sorted(df["Activity"].dropna().unique())

        if activity_options:
            selected_activities = st.multiselect("#### Filtrar por actividad", activity_options)
        else:
            selected_activities = []
            st.caption("El Excel no incluye una columna 'Activity' para filtrar.")

# 2. Carga Segura de SVG
if not SVG_PATH.exists():
    st.error(f"❌ No encontré el SVG en {SVG_PATH.resolve()}")
    st.stop()

svg_content = load_svg(SVG_PATH)

# 2.1 Carga de imagen de ayuda para el botón flotante
help_image_base64 = None
try:
    if HELP_IMAGE_PATH.exists():
        help_image_base64 = load_help_image(HELP_IMAGE_PATH)
    else:
        st.warning(f"ℹ️ No se encontró la imagen de ayuda en {HELP_IMAGE_PATH.resolve()}")
except Exception as e:
    st.warning(f"ℹ️ No pude cargar la imagen de ayuda: {e}")


# 3. Detección de Columna 'Location'
normalized_cols = {normalize_key(c): c for c in df.columns}
target_key = "LOCATION"
location_col = normalized_cols.get(target_key)

svg_id_col = normalized_cols.get("SVG_ID")
oracle_location_col = normalized_cols.get("ORACLE_LOCATION")

if not location_col:
    st.error(
        f"❌ Tu Excel debe tener una columna de ubicación (ej. 'Location', 'Locación'). "
        f"No se encontró la columna con la clave '{target_key}'."
    )
    st.stop()

# 4. Creación de la Clave de Unión
df["_LOCATION_KEY_"] = df[location_col].map(normalize_key)

if svg_id_col:
    df["_SVG_ID_KEY_"] = df[svg_id_col].map(normalize_key)
else:
    df["_SVG_ID_KEY_"] = df["_LOCATION_KEY_"]

if oracle_location_col:
    df["_ORACLE_LOCATION_KEY_"] = df[oracle_location_col].map(normalize_key)

display_columns = build_display_columns(df, location_col)

# 5. Métricas generales para el tablero
total_registros = len(df)
total_areas = int(df[location_col].nunique()) if location_col in df.columns else 0
total_actividades = int(df["Activity"].nunique()) if "Activity" in df.columns else 0
leaders_total = 0
if "Activity" in df.columns and "Nombre" in df.columns:
    leaders_total = int(
        df[df["Activity"] == "Counting Leader"]["Nombre"].nunique()
    )

# 5. Leer ?area= desde la URL
def get_clicked_area_key():
    """Lee y normaliza el parámetro 'area' de la URL."""
    qp = st.query_params
    area_raw = None

    if "area" in qp:
        value = qp["area"]
        if isinstance(value, str):
            area_raw = value
        elif isinstance(value, list) and value:
            area_raw = value[0]

    return area_raw, normalize_key(area_raw) if area_raw else None

clicked_area_raw, clicked_area_key = get_clicked_area_key()
# --- Toggle de área seleccionada (click dos veces para deseleccionar) ---
last_area = st.session_state.get("last_area")

if clicked_area_raw:
    if last_area == clicked_area_raw:
        # Si se volvió a hacer click sobre la misma área => deseleccionar
        clicked_area_raw = None
        clicked_area_key = None
        st.query_params.clear()           # limpia ?area= de la barra de direcciones
        st.session_state["last_area"] = None
    else:
        # Nueva área seleccionada
        st.session_state["last_area"] = clicked_area_raw
else:
    # No hay área seleccionada en esta ejecución
    st.session_state["last_area"] = None

df_filtered = df.copy()

if name_query:
    num_token = normalize_search_text(name_query)
    if num_token:
        df_filtered = df_filtered[
            df_filtered["Número"].astype(str).fillna("").map(normalize_search_text).str.contains(num_token)
        ]

if selected_activities:
    df_filtered = df_filtered[df_filtered["Activity"].isin(selected_activities)]

table_filtered = df_filtered.copy()

if clicked_area_key:
    key_columns = [
        col for col in ["_SVG_ID_KEY_", "_LOCATION_KEY_", "_ORACLE_LOCATION_KEY_"]
        if col in table_filtered.columns
    ]

    if key_columns:
        mask = pd.Series(False, index=table_filtered.index)
        for col in key_columns:
            mask = mask | (table_filtered[col] == clicked_area_key)
        table_filtered = table_filtered[mask]
    else:
        table_filtered = table_filtered[table_filtered["_LOCATION_KEY_"] == clicked_area_key]

filters_applied = bool(name_query or selected_activities or clicked_area_key)
# Si existe la location ALL en el filtro, queremos iluminar todo el mapa
has_all_location = False
if "_LOCATION_KEY_" in df_filtered.columns:
    has_all_location = df_filtered["_LOCATION_KEY_"].eq("ALL").any()


# === INCRUSTACIÓN DEL SVG INTERACTIVO ===

highlighted_svg = svg_content

# Sólo aplicamos dimmed/active si HAY filtros y NO está la location ALL
if filters_applied and not has_all_location:
    # 1) Por defecto, todas las áreas quedan como "dimmed"
    highlighted_svg = highlighted_svg.replace('class="area"', 'class="area dimmed"')

    # 2) Determinar qué áreas tienen registros según los filtros actuales (df_filtered)
    active_ids = set()

    if svg_id_col and svg_id_col in df_filtered.columns:
        active_ids = set(df_filtered[svg_id_col].dropna().astype(str).unique())
    elif location_col in df_filtered.columns:
        active_ids = set(df_filtered[location_col].dropna().astype(str).unique())

    # 3) Marcar esas áreas como "active" (quita dimmed)
    for area_id in active_ids:
        highlighted_svg = highlighted_svg.replace(
            f'class="area dimmed" data-area="{area_id}"',
            f'class="area active" data-area="{area_id}"'
        )
# Si hay filtros PERO hay ALL, el mapa se queda sin dimmed: todo encendido.

# 4) Si hay un área clickeada, marcarla como "selected"
if clicked_area_raw:
    if filters_applied and not has_all_location:
        # Caso con filtros (sin ALL): puede venir como active o dimmed
        highlighted_svg = highlighted_svg.replace(
            f'class="area active" data-area="{clicked_area_raw}"',
            f'class="area selected" data-area="{clicked_area_raw}"'
        )
        highlighted_svg = highlighted_svg.replace(
            f'class="area dimmed" data-area="{clicked_area_raw}"',
            f'class="area selected" data-area="{clicked_area_raw}"'
        )
    else:
        # Caso sin filtros o con ALL: la clase original es sólo "area"
        highlighted_svg = highlighted_svg.replace(
            f'class="area" data-area="{clicked_area_raw}"',
            f'class="area selected" data-area="{clicked_area_raw}"'
        )


if svg_id_col and svg_id_col in df_filtered.columns:
    # Usamos SVG_ID como referencia principal
    active_ids = set(
        df_filtered[svg_id_col].dropna().astype(str).unique()
    )
elif location_col in df_filtered.columns:
    # Fallback: usamos Location si no hay SVG_ID
    active_ids = set(
        df_filtered[location_col].dropna().astype(str).unique()
    )

# 3) Marcar esas áreas como "active" (quita dimmed)
for area_id in active_ids:
    highlighted_svg = highlighted_svg.replace(
        f'class="area dimmed" data-area="{area_id}"',
        f'class="area active" data-area="{area_id}"'
    )

# 4) Si hay un área clickeada, marcarla como "selected"
if clicked_area_raw:
    # Si estaba como active, pasa a selected
    highlighted_svg = highlighted_svg.replace(
        f'class="area active" data-area="{clicked_area_raw}"',
        f'class="area selected" data-area="{clicked_area_raw}"'
    )
    # Por si alguna quedara aún dimmed (sin registros pero clickeada)
    highlighted_svg = highlighted_svg.replace(
        f'class="area dimmed" data-area="{clicked_area_raw}"',
        f'class="area selected" data-area="{clicked_area_raw}"'
    )

# 5) Renderizar el SVG resultante

st.markdown(
    f"""
<div id="svg-wrap" style="position:relative;">
    {highlighted_svg}
    """,
    unsafe_allow_html=True,
)

legend_html = """
<div class="map-legend">
    <div class="legend-item">
    <span class="legend-swatch" style="background:#FC9801;"></span>
    Area seleccionada/ Filtrada
    </div>
    <div class="legend-item">
    <span class="legend-swatch" style="background:#e5e7eb;"></span>
    Sin coincidencias actuales
    </div>
</div>
"""
st.markdown(legend_html, unsafe_allow_html=True)

# --- VISUALIZACIÓN DE RESULTADOS ---
if clicked_area_key:
    # 1. Obtener la etiqueta amigable del SVG
    area_label = get_svg_title(svg_content, clicked_area_raw) or clicked_area_raw

    # 2. Filtrar DataFrame
    key_columns = [
        col for col in ["_SVG_ID_KEY_", "_LOCATION_KEY_", "_ORACLE_LOCATION_KEY_"]
        if col in df_filtered.columns
    ]

    if key_columns:
        mask = pd.Series(False, index=df_filtered.index)
        for col in key_columns:
            mask = mask | (df_filtered[col] == clicked_area_key)
        df_filtrado = df_filtered[mask]
    else:
        df_filtrado = df_filtered[df_filtered["_LOCATION_KEY_"] == clicked_area_key]

    if not df_filtrado.empty:
        # Si hay registros, toma la etiqueta desde el Excel como nombre legible
        if location_col in df_filtrado.columns:
            excel_label = df_filtrado[location_col].dropna().astype(str)
            if not excel_label.empty:
                area_label = excel_label.iloc[0]

        # --- NUEVO: detectar leaders y contadores en esta área ---
        leaders_df = df_filtrado[df_filtrado["Activity"] == "Counting Leader"]
        counters_df = df_filtrado[df_filtrado["Activity"] == "Counting"]

        leaders = leaders_df["Nombre"].unique()
        num_counters = int(counters_df["Nombre"].nunique()) if not counters_df.empty else 0
        st.subheader(f"👥 Personal Asignado a: **{area_label}**")

        # Mostrar resumen de leaders si existen
        if len(leaders) > 0:
            # Chip resumen
            st.markdown(
                f"""
                <div style="
                padding:8px 12px; border-radius:12px;
                background:#eef2ff; color:#0f172a;
                border:1px solid #cbd5f5; margin:4px 0 8px 0;
                font-size:0.9rem;
                ">
                <strong>Counting Leaders asignados:</strong> {", ".join(leaders)}
                {"&nbsp;·&nbsp;("+str(num_counters)+" contadores)" if num_counters else ""}
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            # Si no hay leaders, puedes dejarlo callado o mostrar un aviso suave
            st.caption("No se encontraron registros con Activity = 'Counting Leader' para esta área.")

        # --- Listado general de personas del área (como antes) ---
        nombres = df_filtrado["Nombre"].unique()

    


else:
    """"""
st.markdown("##### 🔍 Explorador de registros filtrados")

if filters_applied:
    st.caption(f"Los filtros actuales devuelven {len(table_filtered)} registro(s) del Excel.")
else:
    """"""""

if table_filtered.empty:
    st.warning("No se encontraron registros que coincidan con los filtros seleccionados.")
else:
    if display_columns:
        filtered_table = table_filtered[display_columns].rename(
            columns={location_col: "Location"}
        )
        st.dataframe(filtered_table, width="stretch")

        csv_data = filtered_table.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ Descargar resultados filtrados (CSV)",
            data=csv_data,
            file_name="inventario_filtrado.csv",
            mime="text/csv",
        )
    else:
        st.info("No hay columnas disponibles para mostrar o exportar desde el Excel.")
# --- BOTÓN DE AYUDA FLOTANTE (SIN JS) ---
if help_image_base64:
    help_button_html = f"""
<div class="help-widget">
  <!-- Checkbox oculto que controla abrir/cerrar -->
  <input type="checkbox" id="help-toggle" class="help-checkbox" />

  <!-- Botón flotante: en realidad es un label vinculado al checkbox -->
  <label for="help-toggle" class="help-btn" aria-label="Ver ayuda">
    ❔ <span>Ayuda</span>
  </label>

  <!-- Modal de ayuda -->
  <div class="help-modal" role="dialog" aria-modal="true">
    <div class="help-modal-content">
      <!-- Botón cerrar: otro label que desmarca el checkbox -->
      <label for="help-toggle" class="help-close" aria-label="Cerrar ayuda">&times;</label>
      <img src="data:image/png;base64,{help_image_base64}" alt="Imagen de ayuda" />
    </div>
  </div>
</div>
"""

    st.markdown(help_button_html, unsafe_allow_html=True)

