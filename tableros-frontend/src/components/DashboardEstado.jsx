import React, { useEffect, useState } from "react";
import axios from "axios";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, Legend, PieChart, Pie
} from "recharts";

export default function DashboardEstado() {
  const [periodos, setPeriodos] = useState([]);
  const [periodoSeleccionado, setPeriodoSeleccionado] = useState("");
  const [catalogoEstados, setCatalogoEstados] = useState([]);

  const [estadoSeleccionadoE1, setEstadoSeleccionadoE1] = useState("");
  const [estadoSeleccionadoE2, setEstadoSeleccionadoE2] = useState("");

  const [dataRegularidad, setDataRegularidad] = useState([]);
  const [pieE1, setPieE1] = useState([]);
  const [pieE2, setPieE2] = useState([]);
  const [topPlantelesE1, setTopPlantelesE1] = useState([]);
  const [topPlantelesE2, setTopPlantelesE2] = useState([]);

  const COLORES_PIE = ["#dc2626", "#f59e0b", "#3b82f6", "#10b981"];

  // 1. Carga inicial de Dropdowns y Catálogo
  useEffect(() => {
    axios.get("http://127.0.0.1:8001/api/v1/dashboard/periodos")
      .then((res) => {
        if (Array.isArray(res.data) && res.data.length > 0) {
          setPeriodos(res.data);
          setPeriodoSeleccionado(res.data[0]);
        }
      }).catch((err) => console.error("Error periodos:", err));

    axios.get("http://127.0.0.1:8001/api/v1/dashboard/catalogo-estados")
      .then((res) => {
        const lista = res.data?.data || res.data;
        if (Array.isArray(lista) && lista.length > 0) {
          setCatalogoEstados(lista);
          setEstadoSeleccionadoE1(lista[0]);
          setEstadoSeleccionadoE2(lista[1] || lista[0]);
        }
      }).catch((err) => console.error("Error catálogo estados:", err));
  }, []);

  // 2. Consumo de Endpoints con extracción tolerante
  useEffect(() => {
    if (estadoSeleccionadoE1 && estadoSeleccionadoE2) {
      
      const queryUrl = `estados=${encodeURIComponent(estadoSeleccionadoE1)}&estados=${encodeURIComponent(estadoSeleccionadoE2)}&lista_estados=${encodeURIComponent(estadoSeleccionadoE1)},${encodeURIComponent(estadoSeleccionadoE2)}`;

      // B. Mapeo de Barras de Regularidad
      axios.get(`http://127.0.0.1:8001/api/v1/dashboard/estados/regularidad?${queryUrl}`)
        .then((res) => {
          if (Array.isArray(res.data)) {
            setDataRegularidad(res.data.map(d => ({
              estado: d.estado,
              "Regularidad %": d.regular !== undefined ? d.regular : (d.regularidad || 0),
              "Irregularidad %": d.irregular !== undefined ? d.irregular : (d.irregularidad || 0)
            })));
          }
        }).catch((err) => console.error("Error en regularidad:", err));

      // C. Mapeo de Niveles de Desempeño (Pays)
      axios.get(`http://127.0.0.1:8001/api/v1/dashboard/estados/desempeno?${queryUrl}`)
        .then((res) => {
          if (Array.isArray(res.data) && res.data.length > 0) {
            const e1 = res.data.find(d => String(d.estado).toUpperCase().trim() === String(estadoSeleccionadoE1).toUpperCase().trim()) || res.data[0];
            const e2 = res.data.find(d => String(d.estado).toUpperCase().trim() === String(estadoSeleccionadoE2).toUpperCase().trim()) || res.data[1] || res.data[0];
            if (e1) setPieE1([
              { name: "Deficiente (<7)", value: e1.bajo || 0 },
              { name: "Regular (7-7.9)", value: e1.medio || 0 },
              { name: "Bueno (8-8.9)", value: e1.alto || 0 },
              { name: "Excelente (9-10)", value: e1.excelente || 0 }
            ]);
            if (e2) setPieE2([
              { name: "Deficiente (<7)", value: e2.bajo || 0 },
              { name: "Regular (7-7.9)", value: e2.medio || 0 },
              { name: "Bueno (8-8.9)", value: e2.alto || 0 },
              { name: "Excelente (9-10)", value: e2.excelente || 0 }
            ]);
          }
        }).catch((err) => console.error("Error en desempeño:", err));

      // D. Mapeo de Top 3 Planteles
      axios.get(`http://127.0.0.1:8001/api/v1/dashboard/estados/top-planteles?${queryUrl}`)
        .then((res) => {
          if (Array.isArray(res.data)) {
            const t1 = res.data.filter(d => String(d.nombreentidad || d.estado).toUpperCase().trim() === String(estadoSeleccionadoE1).toUpperCase().trim());
            const t2 = res.data.filter(d => String(d.nombreentidad || d.estado).toUpperCase().trim() === String(estadoSeleccionadoE2).toUpperCase().trim());
            setTopPlantelesE1(t1.length ? t1 : res.data.slice(0, 3));
            setTopPlantelesE2(t2.length ? t2 : res.data.slice(3, 6));
          }
        }).catch((err) => console.error("Error en top-planteles:", err));
    }
  }, [estadoSeleccionadoE1, estadoSeleccionadoE2, periodoSeleccionado]);

  return (
    <div style={styles.container}>
      {/* CARD PERIODO ESCOLAR */}
      <div style={styles.periodoCard}>
        <label style={styles.periodoLabel}>Período escolar</label>
        <select value={periodoSeleccionado} onChange={(e) => setPeriodoSeleccionado(e.target.value)} style={styles.select}>
          {periodos.map((p, i) => <option key={i} value={p}>{p}</option>)}
        </select>
      </div>

      {/* BARRA VERDE SUPERIOR DE SELECCIÓN */}
      <div style={styles.barraComparacion}>
        <span style={styles.barraTitulo}>Selección de estados:</span>
        <select value={estadoSeleccionadoE1} onChange={(e) => setEstadoSeleccionadoE1(e.target.value)} style={styles.selectBarra}>
          {catalogoEstados.map((edo, idx) => <option key={idx} value={edo}>{edo}</option>)}
        </select>
        <span style={styles.vsLabel}>vs</span>
        <select value={estadoSeleccionadoE2} onChange={(e) => setEstadoSeleccionadoE2(e.target.value)} style={styles.selectBarra}>
          {catalogoEstados.map((edo, idx) => <option key={idx} value={edo}>{edo}</option>)}
        </select>
      </div>

      <p style={{ color: "#64748b", fontSize: "13px", marginTop: "12px" }}>Comparativa detallada de indicadores académicos entre estados seleccionados</p>

      {/* BARRAS APILADAS REGULARIDAD */}
      <div style={styles.graficaCard}>
        <h3 style={styles.graficaTitle}>📈 Regularidad e Irregularidad por Estado</h3>
        <div style={{ width: "100%", height: 150, marginTop: "15px" }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart layout="vertical" data={dataRegularidad}>
              <CartesianGrid strokeDasharray="3 3" horizontal={false} />
              <XAxis type="number" domain={[0, 100]} />
              <YAxis type="category" dataKey="estado" width={140} />
              <Tooltip />
              <Legend />
              <Bar dataKey="Regularidad %" stackId="stack" fill="#009444" />
              <Bar dataKey="Irregularidad %" stackId="stack" fill="#dc2626" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* GRÁFICAS CIRCULARES LADO A LADO */}
      <div style={{ display: "flex", gap: "20px", marginTop: "16px", flexWrap: "wrap" }}>
        {/* PASTEL ESTADO 1 */}
        <div style={{ ...styles.graficaCard, flex: 1, minWidth: "300px" }}>
          <h4 style={styles.graficaTitle}>Nivel de Desempeño: {estadoSeleccionadoE1}</h4>
          <div style={{ height: 200, display: "flex", justifyContent: "center", marginTop: "10px" }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pieE1} cx="50%" cy="50%" outerRadius={70} dataKey="value" label={(e) => `${e.value}%`}>
                  {pieE1.map((entry, index) => <Cell key={index} fill={COLORES_PIE[index % COLORES_PIE.length]} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          
          {/* LEYENDA AGREGADA DEBAJO DEL PASTEL 1 */}
          <div style={styles.customLegendContainer}>
            {pieE1.map((item, idx) => (
              <div key={idx} style={styles.legendRow}>
                <span style={{ ...styles.legendDot, backgroundColor: COLORES_PIE[idx] }}></span>
                <span style={styles.legendText}>{item.name}: <strong>{item.value}%</strong></span>
              </div>
            ))}
          </div>
        </div>

        {/* PASTEL ESTADO 2 */}
        <div style={{ ...styles.graficaCard, flex: 1, minWidth: "300px" }}>
          <h4 style={styles.graficaTitle}>Nivel de Desempeño: {estadoSeleccionadoE2}</h4>
          <div style={{ height: 200, display: "flex", justifyContent: "center", marginTop: "10px" }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pieE2} cx="50%" cy="50%" outerRadius={70} dataKey="value" label={(e) => `${e.value}%`}>
                  {pieE2.map((entry, index) => <Cell key={index} fill={COLORES_PIE[index % COLORES_PIE.length]} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* LEYENDA AGREGADA DEBAJO DEL PASTEL 2 */}
          <div style={styles.customLegendContainer}>
            {pieE2.map((item, idx) => (
              <div key={idx} style={styles.legendRow}>
                <span style={{ ...styles.legendDot, backgroundColor: COLORES_PIE[idx] }}></span>
                <span style={styles.legendText}>{item.name}: <strong>{item.value}%</strong></span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* TOP PLANTELES */}
      <div style={styles.graficaCard}>
        <h3 style={styles.graficaTitle}>Mejores Promedios de Planteles (Top 3 de cada Estado)</h3>
        <div style={{ display: "flex", gap: "20px", marginTop: "15px", flexWrap: "wrap" }}>
          <div style={{ flex: 1, minWidth: "280px", height: 180 }}>
            <p style={{ fontSize: "12px", color: "#009444", fontWeight: "bold" }}>{estadoSeleccionadoE1}</p>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={topPlantelesE1}>
                <XAxis dataKey="nombre_plantel" tick={{ fontSize: 9 }} />
                <YAxis domain={[0, 10]} />
                <Tooltip />
                <Bar dataKey="promg" fill="#009444" barSize={40} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div style={{ flex: 1, minWidth: "280px", height: 180 }}>
            <p style={{ fontSize: "12px", color: "#0071bc", fontWeight: "bold" }}>{estadoSeleccionadoE2}</p>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={topPlantelesE2}>
                <XAxis dataKey="nombre_plantel" tick={{ fontSize: 9 }} />
                <YAxis domain={[0, 10]} />
                <Tooltip />
                <Bar dataKey="promg" fill="#0071bc" barSize={40} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: { minHeight: "100vh", background: "#f8fafc", padding: "24px", fontFamily: "sans-serif" },
  periodoCard: { background: "#fff", width: "240px", padding: "12px", borderRadius: "8px", boxShadow: "0 1px 3px rgba(0,0,0,0.05)", marginBottom: "16px" },
  periodoLabel: { display: "block", fontWeight: "600", color: "#334155", fontSize: "13px", marginBottom: "4px" },
  select: { width: "100%", padding: "6px", borderRadius: "6px", border: "1px solid #cbd5e1" },
  barraComparacion: { display: "flex", alignItems: "center", backgroundColor: "#009444", padding: "10px 16px", borderRadius: "6px", gap: "12px", color: "#fff" },
  barraTitulo: { fontWeight: "bold", fontSize: "14px" },
  vsLabel: { fontWeight: "bold", color: "#a3e635" },
  selectBarra: { backgroundColor: "#00b359", color: "#fff", border: "1px solid #00c864", padding: "6px 12px", borderRadius: "4px", minWidth: "180px", outline: "none" },
  graficaCard: { backgroundColor: "#ffffff", borderRadius: "8px", padding: "20px", marginTop: "16px", boxShadow: "0 1px 3px rgba(0,0,0,0.05)", border: "1px solid #e2e8f0" },
  graficaTitle: { fontSize: "15px", fontWeight: "700", color: "#0f172a", margin: 0 },
  graficaSubtitle: { fontSize: "12px", color: "#64748b", marginTop: "2px" },
  
  // ESTILOS DE LEYENDA ADICIONALES
  customLegendContainer: { marginTop: "15px", display: "flex", flexDirection: "column", gap: "6px", paddingLeft: "10px" },
  legendRow: { display: "flex", alignItems: "center", gap: "10px" },
  legendDot: { width: "11px", height: "11px", borderRadius: "50%", display: "inline-block" },
  legendText: { fontSize: "13px", color: "#334155" }
};