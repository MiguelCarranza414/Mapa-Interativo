"""Aplicación Streamlit para explorar el inventario anual."""

from __future__ import annotations

import io
import unicodedata
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
import xml.etree.ElementTree as ET

# === CONFIGURACIÓN ===
DEFAULT_EXCEL_PATH = Path(r"C:\Inventario\data\roles_areas.xlsx")
SVG_PATH = Path("data/mapa.svg")
EXPECTED_COLUMNS = {"Número", "Nombre"}

st.set_page_config(layout="wide")
st.title("📦 Inventario Anual 2025")
st.subheader("Mapa de áreas interactivas")

with st.sidebar:
    st.header("⚙️ Fuente de datos")
    st.caption("Carga un Excel personalizado o utiliza la ruta predeterminada del sistema.")
    uploaded_excel = st.file_uploader("Subir archivo Excel", type=["xlsx", "xlsm", "xls"])

    if DEFAULT_EXCEL_PATH.exists():
        timestamp = datetime.fromtimestamp(DEFAULT_EXCEL_PATH.stat().st_mtime)
        st.caption(
            f"Predeterminado: `{DEFAULT_EXCEL_PATH}` (última modificación: {timestamp:%d/%m/%Y %H:%M})"
        )
    else:
        st.caption(
            "Ruta predeterminada no encontrada. Sube un archivo para comenzar."
        )

# --- FUNCIONES DE AYUDA ---

@st.cache_data(show_spinner=False)
def load_excel_from_path(path: Path) -> pd.DataFrame:
    """Carga el DataFrame desde un archivo Excel en disco."""
    return pd.read_excel(path)


@st.cache_data(show_spinner=False)
def load_excel_from_bytes(content: bytes) -> pd.DataFrame:
    """Carga el DataFrame a partir del contenido de un Excel cargado por el usuario."""
    return pd.read_excel(io.BytesIO(content))

@st.cache_data(show_spinner=False)
def load_svg(path: Path) -> str:
    """Carga el contenido del archivo SVG."""
    return path.read_text(encoding="utf-8")

def build_display_columns(dataframe: pd.DataFrame, location_column: str) -> list[str]:
    """Devuelve la lista de columnas a mostrar respetando la disponibilidad en el DataFrame."""
    desired_order = ["Número", "Nombre", "Activity", location_column, "Oracle Location", "SVG_ID"]
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


def summarize_dataframe(df: pd.DataFrame) -> tuple[list[str], list[str]]:
    """Devuelve columnas faltantes y opcionales para informar al usuario."""
    available = set(df.columns)
    missing_required = sorted(EXPECTED_COLUMNS - available)
    optional = sorted(col for col in ("Activity", "Oracle Location", "SVG_ID") if col in available)
    return missing_required, optional

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

# 1. Carga Segura de Excel (desde subida o ruta local)
excel_source_label = ""
try:
    if uploaded_excel is not None:
        excel_bytes = uploaded_excel.getvalue()
        df = load_excel_from_bytes(excel_bytes)
        excel_source_label = uploaded_excel.name or "Archivo cargado"
    else:
        df = load_excel_from_path(DEFAULT_EXCEL_PATH)
        excel_source_label = DEFAULT_EXCEL_PATH.name
except FileNotFoundError:
    st.error(
        "❌ No se encontró el Excel. Verifica la ruta predeterminada o sube un archivo manualmente."
    )
    st.stop()
except Exception as e:
    st.error(f"❌ No pude cargar el Excel: {e}")
    st.stop()

missing_required, optional_columns = summarize_dataframe(df)
if missing_required:
    st.warning(
        "Faltan columnas obligatorias en el Excel: " + ", ".join(missing_required)
    )
    st.stop()
else:
    st.caption(f"Fuente de datos: **{excel_source_label}** ({len(df)} registros).")
    if optional_columns:
        st.caption(
            "Columnas disponibles para análisis adicional: " + ", ".join(optional_columns)
        )

with st.expander("📁 Información del Excel cargado", expanded=False):
    st.write("Columnas detectadas:", ", ".join(sorted(df.columns)))
    st.write(
        "Primeras filas de referencia:",
    )
    st.dataframe(df.head(5))

# 2. Carga Segura de SVG
if not SVG_PATH.exists():
    st.error(f"❌ No encontré el SVG en {SVG_PATH.resolve()}")
    st.stop()

svg_content = load_svg(SVG_PATH)

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

# === INTERFAZ DE USUARIO ===
st.markdown("### 📊 Resumen rápido del inventario")
col_total, col_names, col_locations = st.columns(3)
with col_total:
    st.metric("Registros en Excel", len(df))
with col_names:
    st.metric("Personas únicas", int(df["Nombre"].nunique(dropna=True)))
with col_locations:
    st.metric("Áreas registradas", int(df["_LOCATION_KEY_"].nunique(dropna=True)))
st.caption("Estos totales se calculan directamente desde el archivo Excel cargado.")

with st.sidebar:
    st.header("🔎 Filtros rápidos")
    st.caption("Aplica filtros para explorar el personal sin necesidad de hacer clic en el mapa.")
    search_query = st.text_input("Buscar por número o nombre")

    activity_options = []
    if "Activity" in df.columns:
        activity_options = sorted(df["Activity"].dropna().unique())

    if activity_options:
        selected_activities = st.multiselect("Filtrar por actividad", activity_options)
    else:
        selected_activities = []
        st.caption("El Excel no incluye una columna 'Activity' para filtrar.")

df_filtered = df.copy()

if search_query:
    token = normalize_search_text(search_query)
    if token:
        masks = []
        if "Número" in df_filtered.columns:
            masks.append(
                df_filtered["Número"].astype(str).fillna("").map(normalize_search_text).str.contains(token)
            )
        if "Nombre" in df_filtered.columns:
            masks.append(
                df_filtered["Nombre"].astype(str).fillna("").map(normalize_search_text).str.contains(token)
            )
        if masks:
            combined_mask = masks[0]
            for extra_mask in masks[1:]:
                combined_mask = combined_mask | extra_mask
            df_filtered = df_filtered[combined_mask]

if selected_activities:
    df_filtered = df_filtered[df_filtered["Activity"].isin(selected_activities)]

filters_applied = bool(search_query or selected_activities)

# === INCRUSTACIÓN DEL SVG INTERACTIVO ===

highlighted_svg = svg_content

# 1) Por defecto, todas las áreas quedan como "dimmed"
highlighted_svg = highlighted_svg.replace('class="area"', 'class="area dimmed"')

# 2) Determinar qué áreas tienen registros según los filtros actuales (df_filtered)
active_ids = set()

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
    </div>
    """,
    unsafe_allow_html=True
)


# --- VISUALIZACIÓN DE RESULTADOS ---
if clicked_area_key:
    # 1. Obtener la etiqueta amigable del SVG
    area_label = get_svg_title(svg_content, clicked_area_raw) or clicked_area_raw

    # Mostrar chip de área seleccionada
    st.markdown(
        f"""
        <div style="
          display:inline-block; padding:8px 12px; border-radius:999px;
          background:#1f2937; color:white; font-weight:600;
          border:1px solid #4b5563; margin:6px 0;
        ">
          Área clickeada (SVG): {area_label}
        </div>
        """,
        unsafe_allow_html=True
    )

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

        st.markdown("---")
        st.subheader(f"👥 Personal Asignado a: **{area_label}**")

        # Mostrar resumen de leaders si existen
        if len(leaders) > 0:
            # Chip resumen
            st.markdown(
                f"""
                <div style="
                  padding:8px 12px; border-radius:12px;
                  background:#0f172a; color:#e5e7eb;
                  border:1px solid #334155; margin:4px 0 8px 0;
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

    # --- Listado general de personas del área, con Activity ---
    if "Activity" in df_filtrado.columns:
        # Agrupar por nombre y juntar las activities únicas de cada persona
        personas = (
            df_filtrado[["Nombre", "Activity"]]
            .fillna({"Activity": ""})
            .groupby("Nombre")["Activity"]
            .unique()
            .reset_index()
        )
        total_personas = len(personas)

        if total_personas > 0:
            st.info(f"Se encontraron **{total_personas}** entradas de personal en esta área.")

            st.markdown("##### Lista de Nombres:")
            for _, row in personas.iterrows():
                nombre = row["Nombre"]
                acts = [a for a in row["Activity"] if a]  # quitar vacíos
                if acts:
                    # Si una persona tiene varias actividades, las juntamos con coma
                    activity_label = ", ".join(sorted(set(acts)))
                    st.markdown(f"- **{nombre}** — _{activity_label}_")
                else:
                    st.markdown(f"- **{nombre}**")
        else:
            st.warning(
                "El área está cliqueada, pero no se encontraron nombres asignados "
                "en el Excel para esa ubicación."
            )
    else:
        # Fallback por si algún día no existiera la columna Activity
        nombres = df_filtrado["Nombre"].unique()
        if len(nombres) > 0:
            st.info(f"Se encontraron **{len(nombres)}** entradas de personal en esta área.")
            st.markdown("##### Lista de Nombres:")
            for nombre in nombres:
                st.markdown(f"- **{nombre}**")
        else:
            st.warning(
                "El área está cliqueada, pero no se encontraron nombres asignados "
                "en el Excel para esa ubicación."
            )


else:
    st.info("Aún no has seleccionado un área (desde el SVG).")

st.markdown("---")
st.markdown("### 🔍 Explorador de registros filtrados")

if filters_applied:
    st.caption(f"Los filtros actuales devuelven {len(df_filtered)} registro(s) del Excel.")
else:
    st.caption("Muestra los datos completos del Excel. Usa los filtros de la barra lateral para acotar los resultados.")

if df_filtered.empty:
    st.warning("No se encontraron registros que coincidan con los filtros seleccionados.")
else:
    if display_columns:
        filtered_table = df_filtered[display_columns].rename(
            columns={location_col: "Ubicación Excel"}
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
