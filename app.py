import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from pathlib import Path

st.set_page_config(layout="wide")
st.title("📦 Inventario Anual 2025")
st.subheader("Mapa de áreas interactivas")

# --- Cache helpers ---
@st.cache_data(show_spinner=False)
def load_excel(path: str) -> pd.DataFrame:
    return pd.read_excel(path)

@st.cache_data(show_spinner=False)
def load_svg(path: Path) -> str:
    return path.read_text(encoding="utf-8")

# --- Cargar datos ---
EXCEL_URL = "C:/Inventario/data/roles_areas.xlsx"
df = None
try:
    df = load_excel(EXCEL_URL)
except Exception as e:
    st.warning(f"No pude cargar el Excel en {EXCEL_URL}. Detalle: {e}")

# --- Cargar SVG ---
SVG_PATH = Path("data/mapa.svg")
if not SVG_PATH.exists():
    st.error(f"No se encontró el archivo SVG en {SVG_PATH.resolve()}")
    st.stop()

svg_content = load_svg(SVG_PATH)

# --- Leer parámetro de URL (Streamlit 1.30+: st.query_params; en versiones anteriores usa experimental_) ---
try:
    qp = st.query_params  # >= 1.30
    clicked_area = qp.get("area", [None])[0] if isinstance(qp.get("area"), list) else qp.get("area")
except Exception:
    qp = st.experimental_get_query_params()  # fallback
    clicked_area = qp.get("area", [None])[0]

# --- HTML + JS: al hacer click, actualizar ?area=ID ---
html_code = f"""
<div id="svg-container">{svg_content}</div>
<script>
(function() {{
  function init() {{
    const svg = document.querySelector('#svg-container svg');
    if (!svg) {{
       setTimeout(init, 50);
       return;
    }}

    // Hacer "clicables" todos los elementos con atributo id
    svg.querySelectorAll('[id]').forEach(el => {{
      try {{ el.style.cursor = 'pointer'; }} catch (e) {{}}
      el.addEventListener('click', (ev) => {{
        ev.stopPropagation();
        const clickedId = el.id || null;
        if (!clickedId) return;
        const url = new URL(window.location.href);
        url.searchParams.set('area', clickedId);
        // Navega (recarga la app con el query param)
        window.location.href = url.toString();
      }});
    }});
  }}
  init();
}})();
</script>
"""

components.html(html_code, height=600, scrolling=False)

st.write("👉 Haz clic en un área del mapa (cualquier elemento con atributo `id`).")

# --- Mostrar selección y filtrar Excel ---
if clicked_area:
    st.success(f"Área seleccionada: **{clicked_area}**")

    if df is not None:
        # Buscar la columna "Location" sin sensibilidad a mayúsculas/minúsculas
        col_name = next((c for c in df.columns if str(c).strip().lower() == "location"), None)

        if col_name:
            filtered = df[df[col_name].astype(str) == str(clicked_area)]
            if filtered.empty:
                st.info("No hay coincidencias para el área seleccionada.")
            else:
                st.caption("Filtrado por área seleccionada:")
                st.dataframe(filtered, use_container_width=True)

                csv = filtered.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Descargar filtrado (CSV)",
                    csv,
                    file_name=f"inventario_{clicked_area}.csv",
                    mime="text/csv"
                )
        else:
            st.info(
                "El Excel no tiene una columna llamada 'Location'. "
                "Renómbrala exactamente a 'Location' para que funcione el filtro."
            )
else:
    st.info("Aún no has seleccionado un área.")
