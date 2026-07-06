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
        {/* CARRERAS */}
        <div style={styles.pieGrid}>
          <div style={styles.chartBox}>
            <h2>Top 5 Carreras — Mejor Desempeño</h2>
            <ResponsiveContainer width="100%" height={350}>
              <PieChart>
                <Pie
                  data={formatPieData(datos.top_carreras.mejores)}
                  dataKey="value"
                  nameKey="name"
                  outerRadius={120}
                  label
                >
                  {formatPieData(datos.top_carreras.mejores).map((_, index) => (
                    <Cell key={index} fill={coloresVerdes[index % coloresVerdes.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div style={styles.chartBox}>
            <h2>Top 5 Carreras — Menor Desempeño</h2>
            <ResponsiveContainer width="100%" height={350}>
              <PieChart>
                <Pie
                  data={formatPieData(datos.top_carreras.peores)}
                  dataKey="value"
                  nameKey="name"
                  outerRadius={120}
                  label
                >
                  {formatPieData(datos.top_carreras.peores).map((_, index) => (
                    <Cell key={index} fill={coloresRojos[index % coloresRojos.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
        {/* PLANTELES */}
        <div style={styles.pieGrid}>
          <div style={styles.chartBox}>
            <h2>🏆 Top Planteles</h2>
            {datos.top_planteles.mejores.map((p, i) => (
              <div key={i} style={styles.rankCardGreen}>
                <div style={styles.rankCircleGreen}>{i + 1}</div>
                <div>
                  <div style={styles.rankTitle}>{p.descripcion}</div>
                  <div style={styles.rankSub}>
                    Estado: {p.estado || "Desconocido"} • Promedio: {p.promedio} • {p.aprovechamiento}%
                  </div>
                </div>
              </div>
            ))}
          </div>
          <div style={styles.chartBox}>
            <h2>⚠️ Peores Planteles</h2>
            {datos.top_planteles.peores.map((p, i) => (
              <div key={i} style={styles.rankCardRed}>
                <div style={styles.rankCircleRed}>{i + 1}</div>
                <div>
                  <div style={styles.rankTitle}>{p.descripcion}</div>
                  <div style={styles.rankSub}>
                    Estado: {p.estado || "Desconocido"} • Promedio: {p.promedio} • {p.aprovechamiento}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
        {/* TOP 10 DEMANDA */}
        <div style={styles.chartBox}>
          <h2>🔥 Top 10 Carreras con Mayor Demanda por Estado</h2>
          <table style={styles.table}>
            <thead>
              <tr style={{ background: "#008A45", color: "white" }}>
                <th style={{ padding: "10px", textAlign: "left" }}>Estado</th>
                <th style={{ padding: "10px", textAlign: "left" }}>Carrera</th>
                <th style={{ padding: "10px", textAlign: "center" }}>Índice de Demanda</th>
              </tr>
            </thead>
            <tbody>
              {datos.top_demanda_carreras_estado.slice(0, 10).map((item, i) => {
                const pct = Math.round(item.indice_demanda);
                const color =
                  pct >= 85 ? "#16a34a" :
                  pct >= 75 ? "#f59e0b" :
                  "#ef4444";
                return (
                  <tr key={i} style={{ borderBottom: "1px solid #e2e8f0" }}>
                    <td style={{ padding: "10px" }}>{item.nombreentidad}</td>
                    <td style={{ padding: "10px" }}>{item.cveplanestudio}</td>
                    <td style={{
                      padding: "10px",
                      textAlign: "center",
                      background: color,
                      color: "white",
                      fontWeight: "bold"
                    }}>
                      {pct}%
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