import React, { useEffect, useState } from 'react';
import style from './DashboardEncarregado.module.css';
import '../../../../assets/style/global.style.css'
import MenuNavBarCliente from '../../../../Components/Elements/MenuNavBarCliente/MenuNavBarCliente'
import Header from '../../../../Components/Elements/Header/Header'
import Cards from '../../../../Components/Elements/Cards/Cards'
import CardsDocments from '../../../../Components/Elements/CardsDocuments/CardsDocuments';
import { RiUser3Line, RiBillLine, RiCalendarCheckLine, RiNotification3Line, RiFileList3Line, RiBarChartFill } from 'react-icons/ri'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { useAuth } from '../../../../Context/AuthContext';
import api from '../../../../Services/api';

const DashboardEncarregado = () => {
  const { user } = useAuth();
  const [educandos, setEducandos] = useState([]);
  const [performance, setPerformance] = useState([]);
  const [notificacoes, setNotificacoes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        if (user?.id) {
          const [educandosRes, performanceRes, notificacoesRes] = await Promise.all([
            api.get(`/encarregados/${user.id}/educandos/`),
            api.get(`/encarregados/${user.id}/rendimento_educandos/`),
            api.get('/notificacoes/')
          ]);
          setEducandos(Array.isArray(educandosRes.data) ? educandosRes.data : []);
          setPerformance(Array.isArray(performanceRes.data) ? performanceRes.data : []);
          setNotificacoes(Array.isArray(notificacoesRes.data) ? notificacoesRes.data : []);
        }
      } catch (error) {
        console.error("Erro ao carregar dados do dashboard:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [user]);

  const COLORS = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];
  const unreadNotifications = notificacoes.filter(n => !n.lida).length;

  return (
    <div className='containelGeralclient'>
      <MenuNavBarCliente user={'parent'} />
      <main className='containelMainclient'>
        <Header text1="Dashboard" text2="Visão Geral" />

        <div className={style.dashboardContainer}>
          <header className={style.welcomeSection}>
            <h1>Bem-vindo, Sr(a). {user?.nome?.split(' ')[0] || 'Encarregado'}</h1>
            <p>Acompanhe o percurso académico e os rendimentos dos seus educandos de forma centralizada.</p>
          </header>

          <div className={style.gridCards}>
            <Cards
              icon={<RiUser3Line size={50} />}
              title="Educandos Ativos"
              value={loading ? "..." : `${String(educandos.length).padStart(2, '0')} Alunos`}
              value_percentual={0}
            />
            <Cards
              icon={<RiBarChartFill size={40} />}
              title="Média do Grupo"
              value={loading ? "..." : (Array.isArray(performance) && performance.length > 0 ? (performance.reduce((acc, curr) => acc + (curr.media || 0), 0) / performance.length).toFixed(1) : "0.0")}
              value_percentual={0}
            />
            <Cards
              icon={<RiNotification3Line size={50} />}
              title="Notificações"
              value={loading ? "..." : `${String(unreadNotifications).padStart(2, '0')} Novas`}
              value_percentual={unreadNotifications > 0 ? 100 : 0}
            />
          </div>

          <div className={style.chartsGrid}>
            <div className={style.cardChart}>
              <div className={style.sectionHeader}>
                <h2>Comparação de Rendimentos entre Educandos</h2>
                <p>Análise comparativa do desempenho acadêmico (Média Geral).</p>
              </div>
              <div className={style.chartContainer}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={performance} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                    <defs>
                      {COLORS.map((color, idx) => (
                        <linearGradient key={`gradient-${idx}`} id={`colorGrad${idx}`} x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor={color} stopOpacity={0.3} />
                          <stop offset="95%" stopColor={color} stopOpacity={0} />
                        </linearGradient>
                      ))}
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                    <XAxis
                      dataKey="nome"
                      stroke="var(--text-muted)"
                      fontSize={12}
                      tickLine={false}
                      axisLine={false}
                      tick={{ fill: 'var(--text-secondary)' }}
                    />
                    <YAxis
                      stroke="var(--text-muted)"
                      fontSize={12}
                      tickLine={false}
                      axisLine={false}
                      domain={[0, 20]}
                      tick={{ fill: 'var(--text-secondary)' }}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'var(--bg-card)',
                        border: '1px solid var(--border-color)',
                        borderRadius: '12px',
                        boxShadow: 'var(--shadow-soft)',
                        color: 'var(--text-primary)'
                      }}
                      formatter={(value) => [`${value} Valores`, 'Média']}
                    />
                    <Line
                      type="monotone"
                      dataKey="media"
                      stroke="#8b5cf6"
                      strokeWidth={3}
                      dot={{ fill: '#8b5cf6', r: 5 }}
                      activeDot={{ r: 7 }}
                      animationDuration={1500}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          <section className={style.cardDocuments}>
            <div className={style.sectionHeader}>
              <h2>Acesso Rápido a Serviços</h2>
            </div>
            <div className={style.gridCardsComp}>
              <CardsDocments text="Solicitar Documento" icon={<RiBillLine size={50} />} url="/parent/ask" />
              <CardsDocments text="Lista de Educandos" icon={<RiUser3Line  size={50}/>} url="/parent/children" />
              <CardsDocments text="Repositório Digital" icon={<RiFileList3Line size={50} />} url="/parent/document" />
            </div>
          </section>
        </div>
      </main>
    </div>
  );
};

export default DashboardEncarregado;


