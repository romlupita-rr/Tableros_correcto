import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import DashboardPlantel from "../components/DashboardPlantel";
import DashboardEstado from "../components/DashboardEstado";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  CartesianGrid,
  LineChart,
  Line,
  LabelList
} from "recharts";
import {
  PieChart,
  Pie,
  Legend
} from "recharts";

export default function AdminDashboard() {
  const { logout } = useAuth();
  const location = useLocation();
  const [mensajeExito] = useState(
    Boolean(location.state?.loginExitoso)
  );
  // Estados independientes corregidos (sacados del objeto 'datos')
  const [periodos, setPeriodos] = useState([]);
  const [periodoSeleccionado, setPeriodoSeleccionado] = useState("");
  const [tabActiva, setTabActiva] = useState("Nacional");
  const [datos, setDatos] = useState({
    matricula_total: "Cargando...",
    regulares: "Cargando...",
    irregulares: "Cargando...",
    planteles: "Cargando...",
    promedio_nacional: "Cargando...",
    desempeno_estatal: [],
    regularidad_historica: [],
    proyeccion_aprovechamiento: [],
    regularidad_estatal: [],
    top_carreras: { mejores: [], peores: [] },
    top_planteles: { mejores: [], peores: [] },
    top_demanda_carreras_estado: []
  });

  useEffect(() => {
    const token = localStorage.getItem("token");
    fetch(
      `http://localhost:8001/api/v1/dashboard/nacional?periodo=${periodoSeleccionado}`,
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        }
      }
    )
      .then(res => res.json())
      .then(data => {
        // Inicializa los periodos solo la primera vez que se cargan
        if (data.periodos_escolares?.length && periodos.length === 0) {
          setPeriodos(data.periodos_escolares);
          setPeriodoSeleccionado(data.periodos_escolares[0]);
        }
        setDatos({
          matricula_total: data.matricula_total,
          regulares: data.regulares,
          irregulares: data.irregulares,
          planteles: data.planteles,
          promedio_nacional: data.promedio_nacional,
          desempeno_estatal: Array.isArray(data.desempeno_estatal)
            ? [...data.desempeno_estatal].sort((a, b) => b.promedio - a.promedio)
            : [],
          regularidad_historica: data.regularidad_historica || [],
          proyeccion_aprovechamiento: data.proyeccion_aprovechamiento || [],
          regularidad_estatal: data.regularidad_estatal || [],
          top_carreras: data.top_carreras || { mejores: [], peores: [] },
          top_planteles: data.top_planteles || { mejores: [], peores: [] },
          top_demanda_carreras_estado: data.top_demanda_carreras_estado || []
        });
      })
      .catch(err => console.error("ERROR API:", err));
  }, [periodoSeleccionado, periodos.length]);

  /* =========================
      HELPERS
  ========================= */
  const formatPieData = (arr) =>
    arr?.map(i => ({
      name: i.carrera,
      value: i.promedio
    })) || [];

  const colores = [
    "#2563eb", "#16a34a", "#dc2626", "#9333ea", "#ea580c",
    "#0891b2", "#ca8a04", "#be123c", "#0f766e", "#7c3aed"
  ];
  const coloresVerdes = ["#16a34a", "#6350cf", "#666ee2", "#a33b11", "#3184c7"];
  const coloresRojos = ["#bd2035", "#acf3ea", "#28107c", "#c8db17", "#278114"];
  const colorEstado = (index) => colores[index % colores.length];

  if (tabActiva === "Estado") {
    return <DashboardEstado />;
  }
  if (tabActiva === "Planteles") {
    return <DashboardPlantel />;
  }

  return (
    <div style={styles.container}>
      {/* SIDEBAR */}
      <div style={styles.sidebar}>
        <h2>CONALEP</h2>
        <button style={styles.navButton}>🌐 Nacional</button>
        <button onClick={logout} style={styles.logoutButton}>
          Cerrar Sesión
        </button>
      </div>
      {/* MAIN */}
      <div style={styles.mainContent}>
        <div style={styles.header}>
          <h1 style={styles.headerTitle}>Información General</h1>
          <p style={styles.headerSubtitle}>
            Visualización general del sistema CONALEP
          </p>
          <div style={styles.tabs}>
            <button
              onClick={() => setTabActiva("Nacional")}
              style={{
                ...styles.tab,
                ...(tabActiva === "Nacional" ? styles.tabActive : {})
              }}
            >
              Nacional
            </button>
            <button
              onClick={() => setTabActiva("Estado")}
              style={{
                ...styles.tab,
                ...(tabActiva === "Estado" ? styles.tabActive : {})
              }}
            >
              Estado
            </button>
            <button
              onClick={() => setTabActiva("Planteles")}
              style={{
                ...styles.tab,
                ...(tabActiva === "Planteles" ? styles.tabActive : {})
              }}
            >
              Planteles
            </button>
          </div>
          <div style={styles.periodoCard}>
            <label style={styles.periodoLabel}>
              Período escolar
            </label>
            <select
              value={periodoSeleccionado}
              onChange={(e) => setPeriodoSeleccionado(e.target.value)}
              style={styles.selectPeriodo}
            >
              {periodos.map((p) => (
                <option key={p} value={p}>
                  {p}
                </option>
              ))}
            </select>
          </div>
        </div>
        <h1>Dashboard Nacional</h1>
        {mensajeExito && (
          <div style={styles.bannerExito}>
            ¡Bienvenido Administrador!
          </div>
        )}
        {/* KPI */}
        <div style={styles.cardsGrid}>
          <Card titulo="Matrícula Total" valor={datos.matricula_total} />
          <Card titulo="Regulares" valor={datos.regulares} />
          <Card titulo="Irregulares" valor={datos.irregulares} />
          <Card titulo="Planteles" valor={datos.planteles} />
          <Card titulo="Promedio Nacional" valor={datos.promedio_nacional} />
        </div>
        {/* DESEMPEÑO ESTATAL */}
        <div style={styles.chartBox}>
          <h2>Desempeño por Estado</h2>
          <ResponsiveContainer
            width="100%"
            height={950}
          >
            <BarChart
              data={datos.desempeno_estatal}
              layout="vertical"
              margin={{
                top: 20,
                right: 60,
                left: 80,
                bottom: 20
              }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                type="number"
                domain={[0, 10]}
              />
              <YAxis
                type="category"
                dataKey="nombreentidad"
                width={230}
                tick={{
                  fontSize: 13
                }}
              />
              <Tooltip
                formatter={(value) => [
                  value,
                  "Promedio"
                ]}
                labelFormatter={(label, payload) => {
                  if (!payload?.length) return label;
                  return (
                    label +
                    " | Alumnos: " +
                    payload[0].payload.alumnos
                  );
                }}
              />
              <Bar
                dataKey="promedio"
                radius={[0, 8, 8, 0]}
              >
                <LabelList
                  dataKey="promedio"
                  position="right"
                  formatter={(v) => Number(v).toFixed(2)}
                />
                {datos.desempeno_estatal.map((estado, index) => (
                  <Cell
                    key={estado.cveentidad}
                    fill={colorEstado(index)}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
        {/* HISTÓRICO */}
        <div style={styles.chartBox}>
          <h2>Regularidad Histórica</h2>
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={datos.regularidad_historica}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="periodo" />
              <YAxis domain={[80, 100]} />
              <Tooltip />
              <Line type="monotone" dataKey="regularidad" stroke="#16a34a" strokeWidth={3} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        {/* PROYECCIÓN */}
        <div style={styles.chartBox}>
          <h2>Proyección Futura</h2>
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={datos.proyeccion_aprovechamiento}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="periodo" />
              <YAxis domain={[0, 10]} />
              <Tooltip />
              <Line type="monotone" dataKey="promedio" stroke="#2563eb" strokeWidth={3} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        {/* REGULARIDAD */}
        <div style={styles.chartBox}>
          <h2>Regularidad e Irregularidad por Estado</h2>
          <ResponsiveContainer width="100%" height={900}>
            <BarChart data={datos.regularidad_estatal} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" domain={[0, 100]} />
              <YAxis type="category" dataKey="nombreentidad" width={260} />
              <Tooltip />
              <Bar dataKey="regulares_pct" stackId="a" fill="#16a34a" />
              <Bar dataKey="irregulares_pct" stackId="a" fill="#dc2626" />
            </BarChart>
          </ResponsiveContainer>
        </div>
  {/* CARRERAS (BARRAS HORIZONTALES CON TEXTO EN NEGRO Y MÁS GRANDE) */}
        <div style={styles.pieGrid}>
          
          {/* TOP MEJOR DESEMPEÑO */}
          <div style={styles.chartBox}>
            <h2>Top 5 Carreras — Mejor Desempeño</h2>
            <ResponsiveContainer width="100%" height={380}>
              <BarChart
                layout="vertical"
                data={(datos?.top_carreras?.mejores || []).map(item => ({
                  name: item.carrera || item.cveplanestudio,
                  promedio: Number(item.promedio || item.calificacion || item.value || 0)
                }))}
                margin={{ top: 20, right: 30, left: 10, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e8f0" />
                <XAxis type="number" domain={[0, 10]} stroke="#64748b" fontSize={11} />
                
                {/* 📌 EJE Y MODIFICADO: Texto negro, más grande y con más espacio */}
                <YAxis 
                  type="category" 
                  dataKey="name" 
                  stroke="#64748b" // Mantiene la línea del eje sutil
                  tick={{ fill: '#000000', fontSize: 13, fontWeight: '500' }} // Letra negra y más grande
                  width={180} // Mayor ancho para que no se encime el texto grande
                  tickFormatter={(text) => text.length > 25 ? `${text.substring(0, 23)}...` : text}
                />
                
                <Tooltip 
                  cursor={{ fill: '#f8fafc' }}
                  formatter={(value) => [`${Number(value).toFixed(2)}`, 'Promedio General']}
                />
                <Legend />
                
                <Bar 
                  dataKey="promedio" 
                  name="Promedio General" 
                  fill="#0f766e" 
                  stackId="a"    
                  radius={[0, 4, 4, 0]} 
                  barSize={24}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* TOP MENOR DESEMPEÑO */}
          <div style={styles.chartBox}>
            <h2>Top 5 Carreras — Menor Desempeño</h2>
            <ResponsiveContainer width="100%" height={380}>
              <BarChart
                layout="vertical"
                data={(datos?.top_carreras?.peores || []).map(item => ({
                  name: item.carrera || item.cveplanestudio,
                  promedio: Number(item.promedio || item.calificacion || item.value || 0)
                }))}
                margin={{ top: 20, right: 30, left: 10, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e8f0" />
                <XAxis type="number" domain={[0, 10]} stroke="#64748b" fontSize={11} />
                
                {/* 📌 EJE Y MODIFICADO: Texto negro, más grande y con más espacio */}
                <YAxis 
                  type="category" 
                  dataKey="name" 
                  stroke="#64748b" 
                  tick={{ fill: '#000000', fontSize: 13, fontWeight: '500' }} 
                  width={180} 
                  tickFormatter={(text) => text.length > 25 ? `${text.substring(0, 23)}...` : text}
                />
                
                <Tooltip 
                  cursor={{ fill: '#f8fafc' }}
                  formatter={(value) => [`${Number(value).toFixed(2)}`, 'Promedio General']}
                />
                <Legend />
                
                <Bar 
                  dataKey="promedio" 
                  name="Promedio General" 
                  fill="#991b1b" 
                  stackId="a"
                  radius={[0, 4, 4, 0]} 
                  barSize={24}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>

        </div>
   {/* PLANTELES (CORREGIDO: SÓLO PROMEDIO) */}
        <div style={styles.pieGrid}>
          
          {/* MEJORES PLANTELES */}
          <div style={styles.chartBox}>
            <h2>🏆 Top Planteles</h2>
            {datos?.top_planteles?.mejores?.map((p, i) => (
              <div key={i} style={styles.rankCardGreen}>
                <div style={styles.rankCircleGreen}>{i + 1}</div>
                <div>
                  <div style={styles.rankTitle}>{p.descripcion}</div>
                  <div style={styles.rankSub}>
                    {/* 📌 Se removió el porcentaje de aprovechamiento */}
                    Estado: {p.estado || "Desconocido"} • Promedio: {p.promedio}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* PEORES PLANTELES */}
          <div style={styles.chartBox}>
            <h2>⚠️ Peores Planteles</h2>
            {datos?.top_planteles?.peores?.map((p, i) => (
              <div key={i} style={styles.rankCardRed}>
                <div style={styles.rankCircleRed}>{i + 1}</div>
                <div>
                  <div style={styles.rankTitle}>{p.descripcion}</div>
                  <div style={styles.rankSub}>
                    {/* 📌 Se removió el porcentaje de aprovechamiento */}
                    Estado: {p.estado || "Desconocido"} • Promedio: {p.promedio}
                  </div>
                </div>
              </div>
            ))}
          </div>

        </div>
      {/* 🔥 TOP 10 DEMANDA CON SEMÁFORO CORREGIDO (VERDE, AMARILLO, ROJO) */}
<div style={styles.chartBox}>
  <h2 style={{ marginBottom: "15px", color: "#334155" }}>
    🔥 Top 10 Puntos de Mayor Demanda en el País
  </h2>
  
  <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "14px" }}>
    <thead>
      <tr style={{ background: "#1e293b", color: "white" }}>
        <th style={{ padding: "12px", textAlign: "left" }}>Estado</th>
        <th style={{ padding: "12px", textAlign: "left" }}>Carrera Líder</th>
        <th style={{ padding: "12px", textAlign: "center" }}>Alumnos Inscritos</th>
        <th style={{ padding: "12px", textAlign: "center" }}>% Presencia Nacional</th>
      </tr>
    </thead>
    <tbody>
      {datos.top_demanda_carreras_estado && 
       datos.top_demanda_carreras_estado.slice(0, 10).map((item, i) => {
        
        // 🎨 Asignación del semáforo según la posición en el Top 10
        let badgeBgColor = "";
        let badgeTextColor = "white";

        if (i < 3) {
          // Puestos 1, 2 y 3: Los mejores en demanda
          badgeBgColor = "#008A45"; // Verde
          badgeTextColor = "white";
        } else if (i < 7) {
          // Puestos 4, 5, 6 y 7: Regulares / Medios
          badgeBgColor = "#f59e0b"; // Amarillo / Ámbar (da mejor contraste que el amarillo chillón)
          badgeTextColor = "white";
        } else {
          // Puestos 8, 9 y 10: Fatal / Los más bajos del top
          badgeBgColor = "#ef4444"; // Rojo
          badgeTextColor = "white";
        }

        return (
          <tr key={i} style={{ borderBottom: "1px solid #e2e8f0" }}>
            <td style={{ padding: "12px", fontWeight: "500" }}>{item.estado}</td>
            <td style={{ padding: "12px", color: "#475569" }}>{item.carrera}</td>
            <td style={{ padding: "12px", textAlign: "center", fontWeight: "bold" }}>
              {item.alumnos.toLocaleString()}
            </td>
            <td style={{ padding: "12px", textAlign: "center" }}>
              <span style={{
                background: badgeBgColor,
                color: badgeTextColor,
                padding: "6px 12px",
                borderRadius: "6px",
                fontWeight: "bold",
                display: "inline-block",
                minWidth: "65px",
                boxShadow: "0 1px 2px rgba(0,0,0,0.05)"
              }}>
                {item.indice_demanda}%
              </span>
            </td>
          </tr>
        );
      })}
    </tbody>
  </table>
</div>
        </div>
      </div>
  
  );
}

/* CARD */
function Card({ titulo, valor }) {
  return (
    <div style={styles.kpiCard}>
      <h3>{titulo}</h3>
      <h2>{valor}</h2>
    </div>
  );
}

/* ESTILOS */
const styles = {
  container: { display: "flex", minHeight: "100vh", background: "#f8fafc" },
  sidebar: { width: "260px", background: "#0f172a", color: "white", padding: "25px" },
  navButton: { padding: "12px", borderRadius: "8px", width: "100%", background: "#1e293b", color: "white", border: "none", textAlign: "left", cursor: "pointer" },
  logoutButton: { padding: "12px", borderRadius: "8px", background: "#ef4444", color: "white", width: "100%", border: "none", marginTop: "20px", cursor: "pointer" },
  mainContent: { flex: 1, padding: "30px" },
  bannerExito: { background: "#dcfce7", padding: "12px", borderRadius: "8px", marginBottom: "15px", color: "#166534", fontWeight: "bold" },
  cardsGrid: { display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: "15px" },
  kpiCard: { background: "white", padding: "18px", borderRadius: "12px", textAlign: "center", boxShadow: "0 1px 3px rgba(0,0,0,0.1)" },
  chartBox: { background: "white", padding: "20px", borderRadius: "12px", marginBottom: "20px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)" },
  pieGrid: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px", marginBottom: "20px" },
  rankCardGreen: { display: "flex", alignItems: "center", padding: "12px", marginBottom: "10px", borderRadius: "12px", background: "#ecfdf5" },
  rankCardRed: { display: "flex", alignItems: "center", padding: "12px", marginBottom: "10px", borderRadius: "12px", background: "#fef2f2" },
  rankCircleGreen: { width: "50px", height: "50px", borderRadius: "50%", background: "#22c55e", color: "white", display: "flex", alignItems: "center", justifyContent: "center", marginRight: "10px", fontWeight: "bold" },
  rankCircleRed: { width: "50px", height: "50px", borderRadius: "50%", background: "#ef4444", color: "white", display: "flex", alignItems: "center", justifyContent: "center", marginRight: "10px", fontWeight: "bold" },
  rankTitle: { fontWeight: "600", color: "#1e293b" },
  rankSub: { fontSize: "13px", color: "#64748b", marginTop: "4px" },
  header: { marginBottom: "25px" },
  headerTitle: { fontSize: "38px", fontWeight: "700", color: "#0f172a", marginBottom: "5px" },
  headerSubtitle: { color: "#64748b", marginBottom: "25px" },
  tabs: { display: "flex", gap: "10px", borderBottom: "1px solid #e5e7eb", marginBottom: "20px" },
  tab: { padding: "14px 28px", border: "none", background: "transparent", cursor: "pointer", fontWeight: "600", color: "#64748b", borderTopLeftRadius: "8px", borderTopRightRadius: "8px" },
  tabActive: { background: "#009245", color: "white" },
  periodoCard: { background: "white", padding: "20px", borderRadius: "12px", width: "320px", marginBottom: "20px", boxShadow: "0 2px 8px rgba(0,0,0,.08)" },
  periodoLabel: { display: "block", marginBottom: "8px", color: "#374151", fontWeight: "600" },
  selectPeriodo: { width: "100%", padding: "12px", borderRadius: "8px", border: "1px solid #cbd5e1", fontSize: "15px", outline: "none" },
  table: { width: "100%", borderCollapse: "collapse", marginTop: "15px" }
};