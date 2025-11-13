import unicodedata
from pathlib import Path
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# === RUTAS ===
EXCEL_PATH = r"C:\Inventario\data\roles_areas.xlsx"   # <- tu ruta
SVG_PATH   = Path("data/mapa.svg")                    # <- tu ruta

st.set_page_config(layout="wide")
st.title("📦 Inventario Anual 2025")
st.subheader("Mapa de áreas interactivas")

# === Helpers ===
@st.cache_data(show_spinner=False)
def load_excel(path: str) -> pd.DataFrame:
    return pd.read_excel(path)

@st.cache_data(show_spinner=False)
def load_svg(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def normalize_key(s: str) -> str:
    if s is None:
        return ""
    s = str(s).strip()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.replace(" ", "_")
    return s.upper()

# === Carga datos ===
try:
    df = load_excel(EXCEL_PATH)
except Exception as e:
    st.error(f"❌ No pude cargar el Excel: {e}")
    st.stop()

if not SVG_PATH.exists():
    st.error(f"❌ No encontré el SVG en {SVG_PATH.resolve()}")
    st.stop()

svg_content = load_svg(SVG_PATH)

# Detectar columna Location (case/acentos-insensible)
location_col = None
for c in df.columns:
    if normalize_key(c) == "LOCATION":
        location_col = c
        break
if not location_col:
    st.error("❌ Tu Excel debe tener una columna llamada exactamente **Location**.")
    st.stop()

df["_LOCATION_KEY_"] = df[location_col].map(normalize_key)

# Leer ?area=
def get_clicked():
    try:
        qp = st.query_params
        val = qp.get("area")
        return val[0] if isinstance(val, list) else val
    except Exception:
        qp = st.experimental_get_query_params()
        return qp.get("area", [None])[0]

clicked_area_raw = get_clicked()
clicked_area_key = normalize_key(clicked_area_raw) if clicked_area_raw else None

# === HTML + JS robusto ===
html = f"""
<div id="svg-wrap" style="position:relative;">
  {svg_content}
  <div id="last-click" style="
    position:absolute; right:8px; bottom:8px;
    background:#111827; color:#fff; border:1px solid #374151;
    padding:6px 10px; border-radius:999px; font-size:12px; display:none;">
  </div>
</div>

<script>
(function() {{
  function ready(fn) {{
    if (document.readyState !== 'loading') fn();
    else document.addEventListener('DOMContentLoaded', fn);
  }}

  function setTopLocation(url) {{
    try {{
      // Intento 1: navegar el padre directamente
      window.parent.location.href = url;
      return true;
    }} catch (e) {{}}
    try {{
      // Intento 2: usar un <a target="_top">
      const a = document.createElement('a');
      a.href = url;
      a.target = '_top';
      document.body.appendChild(a);
      a.click();
      a.remove();
      return true;
    }} catch (e) {{}}
    return false;
  }}

  function markClickable(el) {{
    try {{ el.style.cursor = 'pointer'; }} catch (e) {{}}
    el.addEventListener('click', function(ev) {{
      ev.stopPropagation();
      const key = el.getAttribute('data-area') || el.id || '';
      if (!key) return;

      // Muestra feedback local inmediato dentro del iframe (debug)
      const chip = document.getElementById('last-click');
      if (chip) {{
        chip.textContent = 'Click: ' + key;
        chip.style.display = 'inline-block';
      }}

      // Actualiza ?area= en la URL del documento padre
      const topUrl = new URL(window.parent.location.href);
      topUrl.searchParams.set('area', key);
      const ok = setTopLocation(topUrl.toString());
      if (!ok) {{
        console.log('No se pudo navegar el documento padre.');
      }}
    }});
  }}

  function init() {{
    const svg = document.querySelector('#svg-wrap svg');
    if (!svg) {{ setTimeout(init, 60); return; }}

    let clickable = svg.querySelectorAll('[data-area], .area');
    if (!clickable || clickable.length === 0) {{
      // Modo compatibilidad: prueba con cualquier [id] visible que no sea el fondo
      clickable = Array.from(svg.querySelectorAll('[id]'))
        .filter(el => el.tagName.toLowerCase() !== 'svg')
        .filter(el => !(el.getAttribute('class')||'').includes('bg'))
        .filter(el => (el.getBoundingClientRect().width > 0 && el.getBoundingClientRect().height > 0));
    }}
    clickable.forEach(markClickable);
  }}

  ready(init);
}})();
</script>
"""


components.html(html, height=700, scrolling=False)
st.caption("👉 Haz clic en un área. (Si no ves la “manita”, este bloque fuerza el cursor por JS)")
# --- MOSTRAR NOMBRE DEL ÁREA (desde el SVG) ---
import xml.etree.ElementTree as ET

def get_svg_title(svg_text: str, area_key: str) -> str:
    """Busca <g data-area="..."><title>...</title></g> y devuelve el texto del title si existe."""
    if not svg_text or not area_key:
        return area_key or ""
    try:
        # Manejo de namespace SVG
        ns = {"svg": "http://www.w3.org/2000/svg"}
        root = ET.fromstring(svg_text)

        # Busca cualquier elemento con data-area == area_key
        # (normalmente será un <g>, pero dejamos genérico)
        for el in root.iter():
            if el.attrib.get("data-area") == area_key:
                # Busca un hijo <title>
                for child in el:
                    # Tag sin o con namespace
                    tag = child.tag.split('}')[-1]
                    if tag == "title" and (child.text or "").strip():
                        return child.text.strip()
                # Si no hay <title>, devolvemos la clave
                return area_key
    except Exception:
        pass
    return area_key

# Muestra lo cliqueado (aunque no haya Excel):
if clicked_area_raw:
    # Título amigable desde el SVG (si existe), si no, usa la clave tal cual
    area_label = get_svg_title(svg_content, clicked_area_raw) or clicked_area_raw

    st.markdown(
        f"""
        <div style="
          display:inline-block;
          padding:8px 12px;
          border-radius:999px;
          background:#1f2937;
          color:white;
          font-weight:600;
          border:1px solid #4b5563;
          margin:6px 0;
        ">
          Área clickeada (SVG): {area_label}
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.info("Aún no has seleccionado un área (desde el SVG).")

# --- FILTRADO DE DATOS Y VISUALIZACIÓN ---

if clicked_area_key:
    # 1. Encontrar todas las filas que coincidan con la clave del área (normalizada)
    #    La columna a buscar es la '_LOCATION_KEY_' que creaste anteriormente.
    df_filtrado = df[df["_LOCATION_KEY_"] == clicked_area_key]

    if not df_filtrado.empty:
        st.markdown("---")
        st.subheader(f"👥 Personal Asignado a: **{area_label}**")

        # Asumiendo que el nombre de la persona está en la columna 'Nombre' (según tu imagen 2)
        # 2. Extraer la lista de nombres
        nombres = df_filtrado['Nombre'].unique()
        
        # 3. Mostrar los nombres como una lista o tabla
        if len(nombres) > 0:
            st.info(f"Se encontraron **{len(nombres)}** entradas de personal.")
            
            # Opción A: Mostrar como una lista de viñetas (más limpio para una lista de nombres)
            st.markdown("##### Lista de Nombres:")
            for nombre in nombres:
                st.markdown(f"- **{nombre}**")
            
            # Opción B: Mostrar toda la tabla filtrada (útil para ver todos los detalles)
            with st.expander("Ver tabla completa de registros filtrados"):
                 # Solo mostrar las columnas relevantes que has indicado en las imágenes:
                columnas_a_mostrar = ['Número', 'Nombre', 'Activity', location_col, 'Oracle Location']
                st.dataframe(df_filtrado[columnas_a_mostrar].rename(columns={location_col: "Ubicación Excel"}), 
                             use_container_width=True)

        else:
            st.warning("El área está cliqueada, pero no se encontraron nombres asignados en el Excel para esa ubicación.")
    
    else:
        st.warning(f"❌ No se encontraron datos en el Excel para el área **{area_label}**.")
