import { useEffect, useState } from "react";
import axios from "axios";
// 📊 Importación de componentes para la gráfica de Recharts
import {
  BarChart,
  Bar,
 XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  LabelList,
  Legend
} from "recharts";

export default function DashboardPlantel() {
  const [tabActiva, setTabActiva] = useState("Planteles");
  const [periodos, setPeriodos] = useState([]);
  const [periodoSeleccionado, setPeriodoSeleccionado] = useState("");
  const [catalogo, setCatalogo] = useState([]);

  // --- SELECCIONES DE BARRA VERDE ---
  const [estadoP1, setEstadoP1] = useState("");
  const [plantelesP1, setPlantelesP1] = useState([]);
  const [plantelSeleccionadoP1, setPlantelSeleccionadoP1] = useState("");
  const [nombrePlantelP1, setNombrePlantelP1] = useState("");

  const [estadoP2, setEstadoP2] = useState("");
  const [plantelesP2, setPlantelesP2] = useState([]);
  const [plantelSeleccionadoP2, setPlantelSeleccionadoP2] = useState("");
  const [nombrePlantelP2, setNombrePlantelP2] = useState("");

  // --- DATOS COMPARTIDOS DE LAS TARJETAS ---
  const [datosComparativos, setDatosComparativos] = useState({
    p1: { matricula: 0, promedio: 0, regulares: 0, regulares_pct: 0, irregulares: 0, irregulares_pct: 0 },
    p2: { matricula: 0, promedio: 0, regulares: 0, regulares_pct: 0, irregulares: 0, irregulares_pct: 0 }
  });

  // =====================================================
  // 📁 CONFIGURACIÓN E INICIALIZACIÓN
  // =====================================================
  useEffect(() => {
    axios
      .get("http://127.0.0.1:8001/api/v1/dashboard/plantel")
      .then((res) => {
        const lista = res?.data?.periodos_escolares;
        if (Array.isArray(lista) && lista.length > 0) {
          setPeriodos(lista);
          setPeriodoSeleccionado(lista[0]);
        }

        const cat = res?.data?.catalogo_estructura;
        if (Array.isArray(cat) && cat.length > 0) {
          setCatalogo(cat);

          // Inicializar Plantel 1
          const pEst = cat[0];
          setEstadoP1(pEst.cveentidad);
          setPlantelesP1(pEst.planteles || []);
          if (pEst.planteles?.length > 0) {
            setPlantelSeleccionadoP1(pEst.planteles[0].cveunidadmin);
            setNombrePlantelP1(pEst.planteles[0].descripcion);
          }

          // Inicializar Plantel 2 (Estado 2 o duplicado del 1)
          const sEst = cat[1] ? cat[1] : cat[0];
          setEstadoP2(sEst.cveentidad);
          setPlantelesP2(sEst.planteles || []);
          if (sEst.planteles?.length > 0) {
            setPlantelSeleccionadoP2(sEst.planteles[0].cveunidadmin);
            setNombrePlantelP2(sEst.planteles[0].descripcion);
          }
        }
      })
      .catch((err) => console.error("Error inicial:", err));
  }, []);

  // =====================================================
  // ⚡ CONSULTA DINÁMICA CUANDO ALGO CAMBIE
  // =====================================================
  useEffect(() => {
    if (plantelSeleccionadoP1 && plantelSeleccionadoP2) {
      axios
        .get(`http://127.0.0.1:8001/api/v1/dashboard/comparar`, {
          params: {
            p1: plantelSeleccionadoP1,
            p2: plantelSeleccionadoP2,
            periodo: periodoSeleccionado
          }
        })
        .then((res) => {
          if (res.data?.p1 && res.data?.p2) {
            setDatosComparativos(res.data);
          }
        })
        .catch((err) => console.error("Error al traer comparación real:", err));
    }
  }, [plantelSeleccionadoP1, plantelSeleccionadoP2, periodoSeleccionado]);

  // =====================================================
  // 🔄 INTERACCIONES INDEPENDIENTES
  // =====================================================
  const handleEstadoP1Change = (cveentidad) => {
    setEstadoP1(cveentidad);
    const ent = catalogo.find(e => String(e.cveentidad) === String(cveentidad));
    const list = ent ? ent.planteles : [];
    setPlantelesP1(list);
    if (list.length > 0) {
      setPlantelSeleccionadoP1(list[0].cveunidadmin);
      setNombrePlantelP1(list[0].descripcion);
    } else {
      setPlantelSeleccionadoP1("");
      setNombrePlantelP1("Sin Plantel");
    }
  };

  const handleEstadoP2Change = (cveentidad) => {
    setEstadoP2(cveentidad);
    const ent = catalogo.find(e => String(e.cveentidad) === String(cveentidad));
    const list = ent ? ent.planteles : [];
    setPlantelesP2(list);
    if (list.length > 0) {
      setPlantelSeleccionadoP2(list[0].cveunidadmin);
      setNombrePlantelP2(list[0].descripcion);
    } else {
      setPlantelSeleccionadoP2("");
      setNombrePlantelP2("Sin Plantel");
    }
  };

  // =====================================================
  // 📉 ESTRUCTURA DE DATOS Y LÓGICA DE LA GRÁFICA
  // =====================================================
  const dataGrafica = [
    { name: nombrePlantelP1 || "Plantel 1", promedio: datosComparativos.p1.promedio, color: "#009444" },
    { name: nombrePlantelP2 || "Plantel 2", promedio: datosComparativos.p2.promedio, color: "#0071bc" }
  ];



  const dataRegularidad = [
  {
    plantel: nombrePlantelP1,
    Regulares: Number(datosComparativos.p1.regulares_pct),
    Irregulares: Number(datosComparativos.p1.irregulares_pct)
  },
  {
    plantel: nombrePlantelP2,
    Regulares: Number(datosComparativos.p2.regulares_pct),
    Irregulares: Number(datosComparativos.p2.irregulares_pct)
  }
];
  const diferencia = Math.abs(datosComparativos.p1.promedio - datosComparativos.p2.promedio).toFixed(2);

  // Tooltip flotante estilizado como el de la captura de pantalla
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div style={{
          backgroundColor: "#fff",
          border: "1px solid #cbd5e1",
          padding: "10px 15px",
          borderRadius: "4px",
          boxShadow: "0 2px 10px rgba(0,0,0,0.1)"
        }}>
          <p style={{ margin: 0, fontWeight: "bold", color: "#1e293b", fontSize: "14px" }}>{payload[0].payload.name}</p>
          <p style={{ margin: "4px 0 0 0", color: "#64748b", fontSize: "13px" }}>
            Promedio : <strong style={{ color: "#0f172a" }}>{payload[0].value}</strong>
          </p>
        </div>
      );
    }
    return null;
  };

 const BarraApilada = ({ datos }) => (
  <div style={{ marginTop: "15px", width: "100%" }}>
    <div style={styles.track}>
      <div style={{...styles.barra, width: `${datos.regulares_pct}%`, backgroundColor: '#009444'}} />
      <div style={{...styles.barra, width: `${datos.irregulares_pct}%`, backgroundColor: '#dc2626'}} />
    </div>
    <div style={styles.leyenda}>
      <span style={{color: '#009444', fontSize: '11px', fontWeight: 'bold'}}>{datos.regulares_pct}% Regulares</span>
      <span style={{color: '#dc2626', fontSize: '11px', fontWeight: 'bold'}}>{datos.irregulares_pct}% Irregulares</span>
    </div>
  </div>
);




  return (
    <div style={styles.container}>
      <div style={styles.mainContent}>
        
        <h1 style={styles.headerTitle}>Información General</h1>
        <p style={styles.headerSubtitle}>Visualización general del sistema CONALEP</p>

        {/* TABS */}
        <div style={styles.tabs}>
          {["Nacional", "Estado", "Planteles"].map((tab) => (
            <button
              key={tab}
              onClick={() => setTabActiva(tab)}
              style={{ ...styles.tab, ...(tabActiva === tab ? styles.tabActive : {}) }}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* SELECT PERIODO */}
        <div style={styles.periodoCard}>
          <label style={styles.periodoLabel}>Período escolar</label>
          <select
            value={periodoSeleccionado}
            onChange={(e) => setPeriodoSeleccionado(e.target.value)}
            style={styles.select}
          >
            {periodos.map((p, i) => <option key={i} value={p}>{p}</option>)}
          </select>
        </div>

        {/* BARRA VERDE DE SELECCIÓN */}
        <div style={styles.barraComparacion}>
          <span style={styles.barraTitulo}>Selección de planteles:</span>
          
          <span style={styles.badgeP1}>P1</span>
          <select value={estadoP1} onChange={(e) => handleEstadoP1Change(e.target.value)} style={styles.selectBarra}>
            {catalogo.map(e => <option key={e.cveentidad} value={e.cveentidad}>{e.nombreentidad}</option>)}
          </select>
          <select 
            value={plantelSeleccionadoP1} 
            onChange={(e) => {
              setPlantelSeleccionadoP1(e.target.value);
              const p = plantelesP1.find(pl => String(pl.cveunidadmin) === String(e.target.value));
              if (p) setNombrePlantelP1(p.descripcion);
            }} 
            style={styles.selectBarra}
          >
            {plantelesP1.map(p => <option key={p.cveunidadmin} value={p.cveunidadmin}>{p.descripcion}</option>)}
          </select>

          <span style={styles.vsLabel}>vs</span>

          <span style={styles.badgeP2}>P2</span>
          <select value={estadoP2} onChange={(e) => handleEstadoP2Change(e.target.value)} style={styles.selectBarra}>
            {catalogo.map(e => <option key={e.cveentidad} value={e.cveentidad}>{e.nombreentidad}</option>)}
          </select>
          <select 
            value={plantelSeleccionadoP2} 
            onChange={(e) => {
              setPlantelSeleccionadoP2(e.target.value);
              const p = plantelesP2.find(pl => String(pl.cveunidadmin) === String(e.target.value));
              if (p) setNombrePlantelP2(p.descripcion);
            }} 
            style={styles.selectBarra}
          >
            {plantelesP2.map(p => <option key={p.cveunidadmin} value={p.cveunidadmin}>{p.descripcion}</option>)}
          </select>
        </div>

        {/* =====================================================
            📊 VISTA COMPARATIVA DE PLANTEL COMPLETO
        ===================================================== */}
        <div style={{ marginTop: "30px" }}>
          <h2 style={{ fontSize: "22px", fontWeight: "700", color: "#0f172a", marginBottom: "4px" }}>Comparación de Planteles</h2>
          <p style={{ fontSize: "14px", color: "#64748b", marginBottom: "20px" }}>Compara el desempeño académico entre dos planteles de diferentes estados</p>

          <div style={styles.cardsContainer}>
            
            {/* TARJETA VERDE (P1) */}
            <div style={styles.cardP1}>
              <div style={styles.cardHeaderTitle}>
                <span style={{ color: "#009444", fontSize: "20px", marginRight: "8px" }}>🏢</span>
                <strong>{nombrePlantelP1 || "Seleccione Plantel 1"}</strong>
              </div>
              <div style={styles.gridMétricas}>
                <div style={styles.subCard}>
                  <label style={styles.metricLabel}>Matrícula Total</label>
                  <span style={styles.metricValueBlack}>{datosComparativos.p1.matricula}</span>
                </div>
                <div style={styles.subCard}>
                  <label style={styles.metricLabel}>Promedio General</label>
                  <span style={styles.metricValueGreen}>{datosComparativos.p1.promedio}</span>
                </div>
                <div style={styles.subCard}>
                  <label style={styles.metricLabel}>Regulares</label>
                  <span style={styles.metricValueGreen}>{datosComparativos.p1.regulares}</span>
                  <small style={styles.metricPct}>{datosComparativos.p1.regulares_pct}%</small>
                </div>
                <div style={styles.subCard}>
                  <label style={styles.metricLabel}>Irregulares</label>
                  <span style={styles.metricValueRed}>{datosComparativos.p1.irregulares}</span>
                  <small style={styles.metricPct}>{datosComparativos.p1.irregulares_pct}%</small>
                </div>
              </div>
            </div>

            {/* TARJETA AZUL (P2) */}
            <div style={styles.cardP2}>
              <div style={styles.cardHeaderTitle}>
                <span style={{ color: "#0071bc", fontSize: "20px", marginRight: "8px" }}>🏢</span>
                <strong>{nombrePlantelP2 || "Seleccione Plantel 2"}</strong>
              </div>
              <div style={styles.gridMétricas}>
                <div style={styles.subCard}>
                  <label style={styles.metricLabel}>Matrícula Total</label>
                  <span style={styles.metricValueBlack}>{datosComparativos.p2.matricula}</span>
                </div>
                <div style={styles.subCard}>
                  <label style={styles.metricLabel}>Promedio General</label>
                  <span style={styles.metricValueBlue}>{datosComparativos.p2.promedio}</span>
                </div>
                <div style={styles.subCard}>
                  <label style={styles.metricLabel}>Regulares</label>
                  <span style={styles.metricValueGreen}>{datosComparativos.p2.regulares}</span>
                  <small style={styles.metricPct}>{datosComparativos.p2.regulares_pct}%</small>
                </div>
                
                <div style={styles.subCard}>
                  <label style={styles.metricLabel}>Irregulares</label>
                  <span style={styles.metricValueRed}>{datosComparativos.p2.irregulares}</span>
                  <small style={styles.metricPct}>{datosComparativos.p2.irregulares_pct}%</small>
                </div>
              </div>
            </div>

          </div>
        </div>

        {/* =====================================================
            📉 SECCIÓN SEGUIDA: GRÁFICA DE BARRAS COMPARATIVA
        ===================================================== */}
        <div style={styles.graficaCard}>
          <h3 style={styles.graficaTitle}>Comparación de Promedio General</h3>
          <p style={styles.graficaSubtitle}>
            Promedio académico de cada plantel — Diferencia: <span style={{ fontWeight: "700" }}>{diferencia} puntos</span>
          </p>
          
          <div style={{ width: "100%", height: 300, marginTop: "20px" }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={dataGrafica} margin={{ top: 10, right: 30, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="name" tick={{ fill: "#64748b", fontSize: 13 }} axisLine={{ stroke: "#cbd5e1" }} />
                <YAxis domain={[0, 10]} ticks={[0, 3, 6, 10]} tick={{ fill: "#64748b", fontSize: 13 }} axisLine={{ stroke: "#cbd5e1" }} />
                <Tooltip content={<CustomTooltip />} cursor={{ fill: "#e2e8f0", opacity: 0.4 }} />
                <Bar dataKey="promedio" barSize={340} radius={[4, 4, 0, 0]}>
                  {dataGrafica.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>


        {/* =====================================================
    REGULARIDAD VS IRREGULARIDAD
===================================================== */}

<div style={styles.graficaCard}>
  <h3 style={styles.graficaTitle}>
    Regularidad vs Irregularidad por Plantel
  </h3>

  <p style={styles.graficaSubtitle}>
    Comparación porcentual de alumnos regulares e irregulares.
  </p>

  <div style={{ width: "100%", height: 220 }}>

    <ResponsiveContainer width="100%" height="100%">

      <BarChart
        layout="vertical"
        data={dataRegularidad}
        margin={{ top: 5, right: 20, left: 30, bottom: 5 }}
      >

        <CartesianGrid
          strokeDasharray="3 3"
          horizontal={false}
        />

        <XAxis
          type="number"
          domain={[0, 100]}
          tickFormatter={(v) => `${v}%`}
        />

        <YAxis
          type="category"
          dataKey="plantel"
          width={180}
        />

        <Tooltip formatter={(v) => `${v}%`} />

        <Legend />

        <Bar
          dataKey="Regulares"
          stackId="a"
          fill="#009444"
        >
          <LabelList
            dataKey="Regulares"
            position="center"
            formatter={(v) => `${v}%`}
            fill="#ffffff"
          />
        </Bar>

        <Bar
          dataKey="Irregulares"
          stackId="a"
          fill="#dc2626"
        />

      </BarChart>

    </ResponsiveContainer>

  </div>
</div>

      </div>
    </div>
  );
}

// =====================================================
// 🎨 HOJA DE ESTILOS INTEGRADA RE-ESTILIZADA
// =====================================================
const styles = {
  container: { minHeight: "100vh", background: "#f4f7f9", padding: "30px" },
  mainContent: {},
  headerTitle: { fontSize: "34px", fontFamily: "serif", fontWeight: "700", color: "#0f172a" },
  headerSubtitle: { fontSize: "14px", color: "#64748b", marginBottom: "20px" },
  tabs: { display: "flex", gap: "10px", borderBottom: "1px solid #e2e8f0", marginBottom: "20px" },
  tab: { background: "transparent", border: "none", color: "#64748b", fontWeight: "600", padding: "10px 18px", cursor: "pointer" },
  tabActive: { background: "#00994c", color: "#fff", borderRadius: "8px" },
  periodoCard: { background: "#fff", width: "260px", padding: "14px", borderRadius: "12px", boxShadow: "0 2px 8px rgba(0,0,0,0.04)", marginBottom: "20px" },
  periodoLabel: { display: "block", fontWeight: "700", fontFamily: "serif", color: "#0f172a", marginBottom: "6px" },
  select: { width: "100%", padding: "8px", borderRadius: "8px", border: "1px solid #cbd5e1", outline: "none" },
  
  barraComparacion: { display: "flex", alignItems: "center", backgroundColor: "#009444", padding: "12px 20px", borderRadius: "8px", gap: "12px", color: "#fff" },
  barraTitulo: { fontWeight: "bold", fontSize: "14px" },
  badgeP1: { backgroundColor: "#22c55e", padding: "3px 6px", borderRadius: "4px", fontWeight: "bold", fontSize: "11px" },
  badgeP2: { backgroundColor: "#0071bc", padding: "3px 6px", borderRadius: "4px", fontWeight: "bold", fontSize: "11px" },
  vsLabel: { fontWeight: "bold", color: "#a3e635" },
  selectBarra: { backgroundColor: "#00b359", color: "#fff", border: "1px solid #00c864", padding: "8px 12px", borderRadius: "6px", minWidth: "160px", outline: "none" },

  cardsContainer: { display: "flex", gap: "20px", flexWrap: "wrap", marginTop: "15px" },
  cardP1: { flex: "1", minWidth: "400px", backgroundColor: "#ecfdf5", border: "2px solid #a7f3d0", borderRadius: "12px", padding: "20px" },
  cardP2: { flex: "1", minWidth: "400px", backgroundColor: "#eff6ff", border: "2px solid #bfdbfe", borderRadius: "12px", padding: "20px" },
  cardHeaderTitle: { fontSize: "18px", color: "#1e293b", marginBottom: "16px", display: "flex", alignItems: "center" },
  gridMétricas: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" },
  subCard: { backgroundColor: "#ffffff", padding: "14px", borderRadius: "8px", boxShadow: "0 1px 3px rgba(0,0,0,0.02)", display: "flex", flexDirection: "column" },
  metricLabel: { color: "#94a3b8", fontSize: "12px", fontWeight: "500", marginBottom: "4px" },
  metricValueBlack: { fontSize: "28px", fontWeight: "bold", color: "#0f172a" },
  metricValueGreen: { fontSize: "28px", fontWeight: "bold", color: "#009444" },
  metricValueBlue: { fontSize: "28px", fontWeight: "bold", color: "#0071bc" },
  metricValueRed: { fontSize: "28px", fontWeight: "bold", color: "#dc2626" },
  metricPct: { fontSize: "12px", color: "#64748b", marginTop: "2px" },

  // Estilos dedicados para la tarjeta contenedora de la gráfica
  graficaCard: {
    backgroundColor: "#ffffff",
    borderRadius: "12px",
    padding: "24px",
    marginTop: "25px",
    boxShadow: "0 4px 12px rgba(0,0,0,0.02)",
    border: "1px solid #e2e8f0"
  },
  graficaTitle: { fontSize: "18px", fontWeight: "700", color: "#0f172a", margin: 0 },
  graficaSubtitle: { fontSize: "13px", color: "#64748b", marginTop: "4px", marginBottom: "15px" },
 
  // Agrega esto al final del objeto:
  track: { display: 'flex', height: '28px', borderRadius: '8px', overflow: 'hidden', width: '100%', backgroundColor: '#f1f5f9' },
  barra: { height: '100%', transition: 'width 0.5s ease' },
  leyenda: { display: 'flex', justifyContent: 'space-between', marginTop: '6px' }
};


  


