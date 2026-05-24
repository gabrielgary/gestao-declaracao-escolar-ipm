import { useState, useEffect } from 'react'
import style from './Dashboards.module.css'
import '../../../assets/style/global.style.css'
import NavBarMenu from '../../../Components/Elements/NavBarMenu/NavBarMenu'
import Header from '../../../Components/Elements/Header/Header'
import Cards from '../../../Components/Elements/Cards/Cards'
import { FaCircleCheck, FaFileInvoice, FaMagnifyingGlass, FaUserGraduate } from 'react-icons/fa6'
import { RiBillLine } from 'react-icons/ri'
import api from '../../../Services/api'

// IMPORTAÇÕES PARA OS GRAFICOS
import {
    AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
    PieChart, Pie, Cell
} from 'recharts';
import Loading from '../../../Components/Elements/Loading/Loading'

export default function Dashboards() {
    const [searchTerm, setSearchTerm] = useState('')
    const [stats, setStats] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const response = await api.get('dashboard/stats/')
                setStats(response.data)
            } catch (error) {
                console.error("Erro ao carregar dados do dashboard:", error)
            } finally {
                setLoading(false)
            }
        }
        fetchStats()
    }, [])

    if (loading) {
        return (
            <div className={'ContainerGeneral'}>
                <NavBarMenu />
                <main className={'ContainerMain'}>
                    <Header text1={"Resumo"} text2={"Dashboard"} onSearch={setSearchTerm} />
                    <div className="flex items-center justify-center h-full">
                        <Loading />
                    </div>
                </main>
            </div>
        )
    }

    if (!stats) return null
    // Destructuring new data keys
    const { kpis, requests_comparison_data, engagement_data, recent_activities, recent_audit_logs } = stats

    const calculatePercentage = (current, previous) => {
        if (previous === 0) return current > 0 ? "+100%" : "0%";
        const percent = ((current - previous) / previous) * 100;
        return (percent > 0 ? "+" : "") + percent.toFixed(1) + "%";
    }

    // Cores para o gráfico de setor
    const PIE_COLORS = ['#8884d8', '#82ca9d', '#ffc658'];

    const filteredActivities = recent_activities.filter(activity =>
        activity.aluno_nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
        activity.tipo_documento.toLowerCase().includes(searchTerm.toLowerCase()) ||
        activity.status_solicitacao.toLowerCase().includes(searchTerm.toLowerCase())
    )

    return (
        <div className={'ContainerGeneral'}>
            <NavBarMenu />
            <main className={'ContainerMain'}>
                <Header text1={"Resumo"} text2={"Dashboard"} onSearch={setSearchTerm} />
                <div className={style.GridCards}>
                    <Cards
                        icon={<FaFileInvoice size={40} />}
                        title={"Total Solicitações"}
                        value={kpis.total_solicitacoes.total.toLocaleString()}
                        value_percentual={calculatePercentage(kpis.total_solicitacoes.current, kpis.total_solicitacoes.previous)}
                    />
                    <Cards
                        icon={<FaCircleCheck size={40} />}
                        title={"Documentos Emitidos"}
                        value={kpis.declaracoes_emitidas.total.toLocaleString()}
                        value_percentual={calculatePercentage(kpis.declaracoes_emitidas.current, kpis.declaracoes_emitidas.previous)}
                    />
                    <Cards
                        icon={<FaUserGraduate size={40} />}
                        title={"Nossos Alunos"}
                        value={kpis.novos_alunos.total.toLocaleString()}
                        value_percentual={calculatePercentage(kpis.novos_alunos.current, kpis.novos_alunos.previous)}
                    />
                    <Cards
                        icon={<RiBillLine size={40} />}
                        title={"Receita Total das Solicitações"}
                        value={`${kpis.receita_total.total.toLocaleString()},00Kz`}
                        value_percentual={calculatePercentage(kpis.receita_total.current, kpis.receita_total.previous)}
                    />
                </div>
                <div className={style.ChartsRow}>
                    {/* Gráfico 1: Comparação de Solicitações (AreaChart) */}
                    <div className={style.RevenueChart}>
                        <div className={style.ChartHeader}>
                            <div>
                                <h3>Comparação de Solicitações</h3>
                                <p className="text-sm text-gray-500">Por tipo de documento (6 meses)</p>
                            </div>
                        </div>
                        <div className="h-[250px] w-full mt-4">
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={requests_comparison_data}>
                                    <defs>
                                        <linearGradient id="colorDecl" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                        </linearGradient>
                                        <linearGradient id="colorCert" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#f97316" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#f97316" stopOpacity={0} />
                                        </linearGradient>
                                        <linearGradient id="colorBol" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border-color)" />
                                    <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: 'var(--text-muted)', fontSize: 12 }} dy={10} />
                                    <YAxis axisLine={false} tickLine={false} tick={{ fill: 'var(--text-muted)', fontSize: 12 }} />
                                    <Tooltip
                                        cursor={{ stroke: 'var(--border-color)', strokeWidth: 1 }}
                                        contentStyle={{
                                            borderRadius: '12px',
                                            border: '0.1px solid var(--border-color)',
                                            backgroundColor: 'var(--bg-card)',
                                            color: 'var(--text-main)',
                                            boxShadow: 'var(--shadow-hover)'
                                        }}
                                    />
                                    <Legend iconType="circle" />
                                    <Area
                                        type="monotone"
                                        dataKey="Declaracao"
                                        name="Declaração"
                                        stroke="#3b82f6"
                                        strokeWidth={1}
                                        fillOpacity={1}
                                        fill="url(#colorDecl)"
                                    />
                                    <Area
                                        type="monotone"
                                        dataKey="Certificado"
                                        name="Certificado"
                                        stroke="#f97316"
                                        strokeWidth={1}
                                        fillOpacity={1}
                                        fill="url(#colorCert)"
                                    />
                                    <Area
                                        type="monotone"
                                        dataKey="Boletim"
                                        name="Boletim"
                                        stroke="#22c55e"
                                        strokeWidth={1}
                                        fillOpacity={1}
                                        fill="url(#colorBol)"
                                    />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* Gráfico 2: Engajamento de Usuários (PieChart) */}
                    <div className={style.PerformanceChart}>
                        <div className={style.ChartHeader}>
                            <h3>Acessos dos Usuários</h3>
                            <p className="text-sm text-gray-500">Distribuição por Tipo</p>
                        </div>
                        <div className="h-[250px] w-full flex items-center justify-center mt-4">
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={engagement_data}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={60}
                                        outerRadius={80}
                                        fill="#8884d8"
                                        paddingAngle={5}
                                        dataKey="value"
                                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                                    >
                                        {engagement_data.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                                        ))}
                                    </Pie>
                                    <Tooltip
                                        contentStyle={{
                                            borderRadius: '12px',
                                            border: '1px solid var(--border-color)',
                                            backgroundColor: 'var(--bg-card)',
                                            color: 'var(--text-main)',
                                        }}
                                    />
                                    <Legend iconType="circle" verticalAlign="bottom" height={36} />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                </div>
                <div className={style.BottomGrid}>
                    <div className={style.RecentActivity}>
                        <div className={style.TableHeaderAction}>
                            <h3>Últimas Solicitações</h3>
                            <div className={style.SearchBarSmall}>
                                <FaMagnifyingGlass />
                                <input
                                    type="text"
                                    placeholder="Pesquisar..."
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                />
                            </div>
                        </div>

                        <div className={style.TableContainer}>
                            <table>
                                <thead>
                                    <tr>
                                        <th>Nome</th>
                                        <th>Tipo</th>
                                        <th>Data</th>
                                        <th>Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {filteredActivities.map((activity) => (
                                        <tr key={activity.id_solicitacao}>
                                            <td>
                                                <div className="flex items-center gap-2">
                                                    {activity.aluno_img ? (
                                                        <img src={activity.aluno_img} alt="" className="w-8 h-8 rounded-full object-cover" />
                                                    ) : (
                                                        <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
                                                            {activity.aluno_nome.charAt(0)}
                                                        </div>
                                                    )}
                                                    <span>{activity.aluno_nome}</span>
                                                </div>
                                            </td>
                                            <td>{activity.tipo_documento}</td>
                                            <td>{new Date(activity.data_solicitacao).toLocaleDateString()}</td>
                                            <td>
                                                <span className={
                                                    activity.status_solicitacao === 'pendente' ? style.StatusBadgeOrange :
                                                        activity.status_solicitacao === 'aprovado' ? style.StatusBadgeGreen :
                                                            activity.status_solicitacao === 'pago' ? style.StatusBadgeBlue :
                                                                style.StatusBadgeRed
                                                }>
                                                    {activity.status_solicitacao}
                                                </span>
                                            </td>
                                        </tr>
                                    ))}
                                    {filteredActivities.length === 0 && (
                                        <tr>
                                            <td colSpan="4" style={{ textAlign: 'center', padding: '20px', color: 'var(--text-muted)' }}>
                                                Nenhum resultado encontrado
                                            </td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <div className={style.RecentAudit}>
                        <div className={style.TableHeaderAction}>
                            <h3>Actividades Recente</h3>
                        </div>
                        <div className={style.AuditList}>
                            {recent_audit_logs?.map((log) => (
                                <div key={log.id} className={style.AuditItem}>
                                    <div className={style.AuditIcon}>
                                        <div className={style.Dot}></div>
                                    </div>
                                    <div className={style.AuditContent}>
                                        <p className={style.AuditText}>
                                            <strong>{log.user}</strong> {log.action?.toLowerCase().replace(/_/g, ' ') || 'realizou uma ação'}
                                        </p>
                                        <span className={style.AuditTime}>
                                            {new Date(log.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} • {new Date(log.time).toLocaleDateString()}
                                        </span>
                                    </div>
                                </div>
                            ))}
                            {recent_audit_logs?.length === 0 && (
                                <p className={style.EmptyText}>Sem atividades recentes.</p>
                            )}
                        </div>
                    </div>
                </div>
            </main>
        </div>
    )
}
