import React, { useEffect, useState, useRef } from 'react';
import style from './DashboardsStudents.module.css';
import '../../../../assets/style/global.style.css'
import MenuNavBarCliente from '../../../../Components/Elements/MenuNavBarCliente/MenuNavBarCliente'
import Header from '../../../../Components/Elements/Header/Header'
import Cards from '../../../../Components/Elements/Cards/Cards'
import { RiFileList3Line, RiBookOpenLine, RiCalendarEventLine, RiNotification3Line, RiShieldUserLine, RiArticleLine, RiPieChartLine, RiLineChartLine } from 'react-icons/ri'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  AreaChart, Area, PieChart, Pie, Cell, Legend
} from 'recharts';
import CardsDocments from '../../../../Components/Elements/CardsDocuments/CardsDocuments';
import { useAuth } from '../../../../Context/AuthContext';
import api from '../../../../Services/api';

// Custom hook for animated counter
const useAnimatedCounter = (endValue, duration = 1000, shouldAnimate = false) => {
  const [count, setCount] = useState(0);
  const countRef = useRef(0);
  const animationRef = useRef(null);

  useEffect(() => {
    if (!shouldAnimate) {
      setCount(endValue);
      return;
    }

    const startTime = Date.now();
    const startValue = countRef.current;
    const difference = endValue - startValue;

    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);

      // Easing function for smooth animation
      const easeOutQuart = 1 - Math.pow(1 - progress, 4);
      const currentValue = startValue + (difference * easeOutQuart);

      countRef.current = currentValue;
      setCount(currentValue);

      if (progress < 1) {
        animationRef.current = requestAnimationFrame(animate);
      }
    };

    animationRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [endValue, duration, shouldAnimate]);

  return count;
};

const DashboardsStudents = () => {
  const { user } = useAuth();
  const [isLoaded, setIsLoaded] = useState(false);
  const [stats, setStats] = useState({
    media_geral: 0,
    presenca_percentual: 0,
    total_faltas: 0,
    notas_por_disciplina: []
  });
  const [documentsStats, setDocumentsStats] = useState({
    boletim: 0,
    declaracao: 0,
    certificado: 0
  });

  // Animated counters
  const animatedMediaGeral = useAnimatedCounter(stats.media_geral, 1200, isLoaded);
  const animatedPresenca = useAnimatedCounter(stats.presenca_percentual, 1200, isLoaded);
  const animatedFaltas = useAnimatedCounter(stats.total_faltas, 1000, isLoaded);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [boletimResponse, documentsResponse] = await Promise.all([
          api.get(`/alunos/${user.id}/boletim/`),
          api.get(`/solicitacoes/?id_aluno=${user.id}&status=PAGO`)
        ]);

        setStats(boletimResponse.data);
        console.log(boletimResponse.data)
        // Contar documentos por tipo
        const docs = documentsResponse.data.results || documentsResponse.data || [];
        const counts = {
          boletim: docs.filter(d => d.tipo_documento === 'BOLETIM').length,
          declaracao: docs.filter(d => d.tipo_documento.includes('DECLARAÇÃO') || d.tipo_documento.includes('DECLARACAO')).length,
          certificado: docs.filter(d => d.tipo_documento === 'CERTIFICADO').length
        };
        setDocumentsStats(counts);

        // Small delay for smooth transition
        setTimeout(() => {
          setIsLoaded(true);
        }, 300);
      } catch (error) {
        console.error("Erro ao buscar dados do dashboard:", error);
        setIsLoaded(true);
      }
    };
    if (user?.id) fetchData();
  }, [user]);

  // Map backend notes to evolution chart - comparing disciplines
  const performanceData = stats.notas_por_disciplina.length > 0
    ? stats.notas_por_disciplina.map(n => ({
      disciplina: n.disciplina.length > 15 ? n.disciplina.substring(0, 12) + '...' : n.disciplina,
      media: n.media_final_valor
    }))
    : [
      { disciplina: 'Mat', media: 0 },
      { disciplina: 'Port', media: 0 },
      { disciplina: 'Fís', media: 0 },
      { disciplina: 'Quím', media: 0 },
    ];

  return (
    <div className='containelGeralclient'>
      <MenuNavBarCliente user={'student'} />
      <main className='containelMainclient'>
        <Header text1="Estudante" text2="Dashboard" />
        <div className={`${style.dashboardContainer} ${isLoaded ? style.loaded : ''}`}>
          <header className={style.welcomeSection}>
            <h1>Bem-vindo de volta, {user?.nome || 'Estudante'}</h1>
            <p>Acompanhe seu progresso acadêmico.</p>
          </header>

          <div className={`${style.scrollWrapper} stagger-container`}>
            <div className={style.gridCards}>
              <Cards
                icon={<RiLineChartLine size={30} />}
                title="Média Geral"
                value={animatedMediaGeral.toFixed(1)+" Valores"}
            
              />{/*
              <Cards
                icon={<RiPieChartLine size={30} />}
                title="Presença Total"
                value={`${Math.round(animatedPresenca)}%`}
                value_percentual={(stats.presenca_percentual >= 75 ? 2.1 : -4.5) + "%"}
              />*/}
              <Cards
                icon={<RiArticleLine size={30} />}
                title="Faltas Acumuladas"
                value={`${Math.round(animatedFaltas)} Faltas`}
      
              />
              <Cards
                icon={<RiFileList3Line size={30} />}
                title="Status Geral"
                value={stats.media_geral >= 10 ? "Aprovado" : "Em Risco"}
                
              />
            </div>
          </div>

          <div className={`${style.chartsGrid} stagger-container`}>
            <div className={`${style.cardChart} glass-card`}>
              <div className={style.sectionHeader}>
                <h2 className="text-gradient">Evolução Acadêmica</h2>
              </div>
              <div className={style.chartContainer}>
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={performanceData}>
                    <defs>
                      <linearGradient id="colorGrade" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="var(--cor-primaria)" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="var(--cor-primaria)" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                    <XAxis
                      dataKey="disciplina"
                      stroke="var(--text-muted)"
                      fontSize={11}
                      fontWeight={400}
                      tickLine={false}
                      axisLine={false}
                    />
                    <YAxis
                      stroke="var(--text-muted)"
                      fontSize={11}
                      fontWeight={400}
                      tickLine={false}
                      axisLine={false}
                      domain={[0, 20]}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'var(--bg-card)',
                        border: '1px solid var(--border-color)',
                        borderRadius: '12px',
                        boxShadow: 'var(--shadow-soft)',
                        fontWeight: 400
                      }}
                      labelStyle={{ fontWeight: 500 }}
                      formatter={(value) => [`${value.toFixed(1)}`, 'Média']}
                    />
                    <Area
                      type="monotone"
                      dataKey="media"
                      stroke="var(--cor-primaria)"
                      strokeWidth={2.5}
                      fillOpacity={1}
                      fill="url(#colorGrade)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className={`${style.cardChart} glass-card`}>
              <div className={style.sectionHeader}>
                <h2 className="text-gradient">Documentos Gerados</h2>
              </div>
              <div className={style.chartContainer}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={[
                        { name: 'Boletins', value: documentsStats.boletim, color: 'var(--cor-primaria)' },
                        { name: 'Declarações', value: documentsStats.declaracao, color: '#8b5cf6' },
                        { name: 'Certificados', value: documentsStats.certificado, color: '#10b981' }
                      ]}
                      cx="50%"
                      cy="50%"
                      innerRadius={45}
                      outerRadius={70}
                      paddingAngle={3}
                      dataKey="value"
                      label={({ value }) => value > 0 ? `${value}` : ''}
                      labelLine={false}
                    >
                      {[
                        { name: 'Boletins', value: documentsStats.boletim, color: 'var(--cor-primaria)' },
                        { name: 'Declarações', value: documentsStats.declaracao, color: '#8b5cf6' },
                        { name: 'Certificados', value: documentsStats.certificado, color: '#10b981' }
                      ].map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'var(--bg-card)',
                        border: '1px solid var(--border-color)',
                        borderRadius: '12px',
                        boxShadow: 'var(--shadow-soft)',
                        padding: '8px 12px'
                      }}
                    />
                    <Legend
                      verticalAlign="bottom"
                      height={36}
                      iconType="circle"
                      formatter={(value) => <span style={{ fontSize: '12px', color: 'var(--text-main)' }}>{value}</span>}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          <section className={style.quickAccessSection}>
            <div className={style.sectionHeader}>
              <h2>Acesso Rápido</h2>
            </div>
            <div className={style.quickAccessGrid}>
              <div className={style.revealItem}>
                <CardsDocments text="Solicitações" icon={<RiFileList3Line size={50} />} url="/student/ask" text_display={"Realizar Solicitação"} />
              </div>
              <div className={style.revealItem}>
                <CardsDocments text="Notas e Avaliações" icon={<RiShieldUserLine size={50} />} url="/student/grades"  text_display={"Ver Notas"}/>
              </div>
              <div className={style.revealItem}>
                <CardsDocments text="Documentos" icon={<RiCalendarEventLine size={50} />} url="/student/document" text_display={"Ver Documentos"}/>
              </div>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
};

export default DashboardsStudents;
