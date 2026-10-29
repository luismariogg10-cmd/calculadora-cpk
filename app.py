import streamlit as st

st.set_page_config(page_title="Simulador de CPK", layout="centered")

st.title("Simulador de CPK")
st.caption("Simulador financiero: cálculo de costo por kilómetro y TCO.")

st.subheader("Datos de Operación")
km_anuales = st.number_input("Kilómetros al año", value=120000, step=5000)
rendimiento = st.number_input("Rendimiento (km/L)", value=2.80, step=0.1)
precio_diesel = st.number_input("Precio del diésel (MXN/L)", value=24.50, step=0.5)
km_vacios_pct = st.number_input("Kilómetros vacíos (%)", value=15.0, step=1.0)

st.subheader("Costos Anuales")
col1, col2 = st.columns(2)
with col1:
    mantenimiento = st.number_input("Mantenimiento anual ($)", value=35000.0, step=1000.0)
    sueldo_operador_mes = st.number_input("Salario operador mensual ($)", value=16000.0, step=1000.0)
    seguros = st.number_input("Seguros anuales ($)", value=28000.0, step=1000.0)
with col2:
    refacciones = st.number_input("Refacciones anuales ($)", value=18000.0, step=1000.0)
    otros_fijos = st.number_input("Otros fijos anuales ($)", value=20000.0, step=1000.0)
    depreciacion = st.number_input("Depreciación anual ($)", value=160000.0, step=5000.0)

if st.button("Calcular CPK y TCO", type="primary"):
    litros = km_anuales / rendimiento if rendimiento > 0 else 0
    combustible = litros * precio_diesel
    sueldo_anual = sueldo_operador_mes * 12
    tco_anual = combustible + mantenimiento + refacciones + seguros + otros_fijos + sueldo_anual + depreciacion

    cpk_total = tco_anual / km_anuales if km_anuales > 0 else 0
    km_cargados = km_anuales * (1 - (km_vacios_pct / 100))
    cpk_cargado = tco_anual / km_cargados if km_cargados > 0 else 0

    st.markdown("---")
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("CPK Total", f"${cpk_total:,.2f} MXN")
    kpi2.metric("CPK Cargado", f"${cpk_cargado:,.2f} MXN")
    kpi3.metric("TCO Anual", f"${tco_anual:,.2f} MXN")