import io
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Simulador Avanzado de CPK & TCO",
    page_icon="🚛",
    layout="wide"
)

st.title("🚛 Simulador Financiero de Transporte (CPK & TCO)")
st.caption("Herramienta de diagnóstico operativo: análisis de costo por kilómetro, estructura de costos y sensibilidad.")

# Pestañas de captura y parametrización
tab_unidad, tab_operacion, tab_costos, tab_sensibilidad = st.tabs([
    "📋 1. Unidad & Identificación",
    "🛣️ 2. Operación & Rutas",
    "💼 3. Estructura de Costos",
    "⚡ 4. Análisis de Sensibilidad"
])

with tab_unidad:
    st.subheader("Identificación del Activo")
    col_u1, col_u2 = st.columns(2)
    with col_u1:
        unidad = st.text_input("Identificador de la unidad (ej. Económico / Modelo)", value="Tractocamión 6x4 (Económico 01)")
    with col_u2:
        anio = st.number_input("Año modelo", min_value=1995, max_value=2030, value=2023)

with tab_operacion:
    st.subheader("Parámetros de Rutas y Combustible")
    col_op1, col_op2, col_op3 = st.columns(3)
    with col_op1:
        km_anuales = st.number_input("Kilómetros totales al año", min_value=1000, value=120000, step=5000)
    with col_op2:
        rendimiento_base = st.number_input("Rendimiento promedio (km/L)", min_value=0.5, value=2.80, step=0.05, format="%.2f")
    with col_op3:
        precio_diesel_base = st.number_input("Precio base del diésel ($ MXN/L)", min_value=1.0, value=24.50, step=0.20, format="%.2f")

    km_vacios_base_pct = st.slider("Porcentaje de kilómetros en vacío (%)", min_value=0.0, max_value=50.0, value=15.0, step=0.5)

with tab_costos:
    st.subheader("Desglose Financiero Anual")
    c_fijos, c_variables = st.columns(2)

    with c_variables:
        st.markdown("**Costos Variables Directos**")
        mantenimiento_anual = st.number_input("Mantenimiento preventivo/correctivo ($ MXN)", value=38000.0, step=1000.0)
        refacciones_anual = st.number_input("Desgaste de llantas y refacciones ($ MXN)", value=22000.0, step=1000.0)
        peajes_anual = st.number_input("Casetas / Peajes anuales ($ MXN)", value=45000.0, step=2500.0)
        viaticos_km = st.number_input("Comisiones / Viáticos por km ($ MXN/km)", value=1.20, step=0.10, format="%.2f")

    with c_fijos:
        st.markdown("**Costos Fijos y Financiamiento**")
        sueldo_operador_mes = st.number_input("Sueldo mensual operador ($ MXN)", value=18000.0, step=1000.0)
        seguro_anual = st.number_input("Póliza de seguro anual ($ MXN)", value=32000.0, step=1000.0)
        otros_fijos_anual = st.number_input("GPS, verificación, administración ($ MXN)", value=24000.0, step=1000.0)
        depreciacion_anual = st.number_input("Depreciación / Costo financiero anual ($ MXN)", value=160000.0, step=5000.0)

with tab_sensibilidad:
    st.subheader("Ajuste de Escenario en Tiempo Real")
    st.info("Modifica estas variables para comprobar la volatilidad del costo operativo frente al mercado.")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        precio_diesel = st.slider("Escenario de Diésel ($ MXN/L)", min_value=20.0, max_value=32.0, value=float(precio_diesel_base), step=0.10)
    with col_s2:
        km_vacios_pct = st.slider("Escenario de Vacíos (%)", min_value=0.0, max_value=40.0, value=float(km_vacios_base_pct), step=0.5)

# --- MOTOR DE CÁLCULO FINANCIERO ---
litros_diesel = km_anuales / rendimiento_base if rendimiento_base > 0 else 0
costo_diesel = litros_diesel * precio_diesel
costo_viaticos_total = km_anuales * viaticos_km

# Costos Variables
total_variables = costo_diesel + mantenimiento_anual + refacciones_anual + peajes_anual + costo_viaticos_total

# Costos Fijos
sueldo_anual = sueldo_operador_mes * 12
total_fijos = sueldo_anual + seguro_anual + otros_fijos_anual + depreciacion_anual

# TCO y CPK
tco_anual = total_variables + total_fijos
cpk_total = tco_anual / km_anuales if km_anuales > 0 else 0

km_cargados = km_anuales * (1 - (km_vacios_pct / 100))
cpk_cargado = tco_anual / km_cargados if km_cargados > 0 else 0

cpk_variable = total_variables / km_anuales if km_anuales > 0 else 0
cpk_fijo = total_fijos / km_anuales if km_anuales > 0 else 0

# --- SECCIÓN DE RESULTADOS ---
st.markdown("---")
st.subheader("Resultados Consolidados")

m1, m2, m3, m4 = st.columns(4)
m1.metric("CPK Total", f"${cpk_total:,.2f} MXN", help="Costo por kilómetro considerando todos los km recorridos.")
m2.metric("CPK Cargado", f"${cpk_cargado:,.2f} MXN", delta=f"{((cpk_cargado/cpk_total)-1)*100:.1f}% vs base", delta_color="inverse", help="Costo por km que debe cobrar la unidad para absorber los tramos vacíos.")
m3.metric("TCO Anual", f"${tco_anual:,.2f} MXN")
m4.metric("Diésel Anual", f"${costo_diesel:,.2f} MXN", f"{(costo_diesel/tco_anual)*100:.1f}% del TCO")

# Gráficos
g1, g2 = st.columns(2)

with g1:
    df_costos = pd.DataFrame({
        "Concepto": ["Combustible", "Operador", "Mantenimiento & Llantas", "Peajes", "Seguros & Fijos", "Depreciación / Financiamiento"],
        "Monto": [costo_diesel, sueldo_anual, mantenimiento_anual + refacciones_anual, peajes_anual, seguro_anual + otros_fijos_anual, depreciacion_anual]
    })
    fig_pie = px.pie(
        df_costos,
        names="Concepto",
        values="Monto",
        title="Distribución del Costo Total de Operación (TCO)",
        hole=0.45,
        color_discrete_sequence=px.colors.sequential.Blues_r
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)

with g2:
    df_cpk = pd.DataFrame({
        "Métrica": ["CPK Variable", "CPK Fijo", "CPK Total", "CPK Cargado"],
        "Costo_por_KM": [cpk_variable, cpk_fijo, cpk_total, cpk_cargado]
    })
    fig_bar = px.bar(
        df_cpk,
        x="Métrica",
        y="Costo_por_KM",
        text_auto=".2f",
        title="Estructura de CPK (MXN / km)",
        color="Métrica",
        color_discrete_sequence=["#93c5fd", "#60a5fa", "#2563eb", "#1e3a8a"]
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# --- EXPORTACIÓN DE RESULTADOS A EXCEL ---
st.markdown("### Exportar Diagnóstico")

output = io.BytesIO()
with pd.ExcelWriter(output, engine="openpyxl") as writer:
    resumen_data = {
        "Parámetro / Métrica": [
            "Unidad", "Año", "Kilómetros Anuales", "Rendimiento (km/L)",
            "Precio Diésel ($/L)", "Km Vacíos (%)", "Km Cargados Reales",
            "Costo Diésel Total", "Total Costos Variables", "Total Costos Fijos",
            "TCO Anual", "CPK Variable", "CPK Fijo", "CPK Total", "CPK Cargado"
        ],
        "Valor": [
            unidad, anio, km_anuales, rendimiento_base,
            precio_diesel, km_vacios_pct, km_cargados,
            costo_diesel, total_variables, total_fijos,
            tco_anual, cpk_variable, cpk_fijo, cpk_total, cpk_cargado
        ]
    }
    pd.DataFrame(resumen_data).to_excel(writer, index=False, sheet_name="Resumen CPK")
    df_costos.to_excel(writer, index=False, sheet_name="Desglose Costos")

st.download_button(
    label="📥 Descargar Diagnóstico en Excel (.xlsx)",
    data=output.getvalue(),
    file_name=f"Diagnostico_CPK_{unidad.replace(' ', '_')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    type="secondary"
)
