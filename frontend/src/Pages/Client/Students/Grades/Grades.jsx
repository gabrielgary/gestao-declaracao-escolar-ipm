import React, { useEffect, useState } from 'react';
import style from './Grades.module.css';
import '../../../../assets/style/global.style.css'
import MenuNavBarCliente from '../../../../Components/Elements/MenuNavBarCliente/MenuNavBarCliente'
import Header from '../../../../Components/Elements/Header/Header'
import { RiLineChartLine, RiArrowUpSLine, RiArrowDownSLine, RiMedalLine, RiExpandDiagonalLine } from 'react-icons/ri';
import { useAuth } from '../../../../Context/AuthContext';
import api from '../../../../Services/api';

const Grades = () => {
    const { user } = useAuth();
    const [stats, setStats] = useState({
        media_geral: 0,
        notas_por_disciplina: [],
        presenca_percentual: 0
    });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchGrades = async () => {
            try {
                const response = await api.get(`/alunos/${user.id}/boletim/`);
                setStats(response.data);
                setLoading(false);
            } catch (error) {
                console.error("Erro ao buscar notas:", error);
                setLoading(false);
            }
        };
        if (user?.id) fetchGrades();
    }, [user]);

    const bestSubject = stats.notas_por_disciplina.length > 0
        ? stats.notas_por_disciplina.reduce((prev, current) => (prev.media_final_valor > current.media_final_valor) ? prev : current)
        : { disciplina: '---', media_final_valor: 0 };

    return (
        <div className='containelGeralclient'>
            <MenuNavBarCliente user={'student'} />
            <main className='containelMainclient'>
                <Header text1="Estudante" text2="Minhas Notas" />
                <div className={style.container}>
                    <header className={style.header}>
                        <h1>Minhas Notas</h1>
                        <p>Acompanhe seu desempenho acadêmico detalhado por disciplina.</p>
                    </header>

                    <div className={style.statsGrid}>
                        <div className={style.statCard}>
                            <div className={style.statHeader}>
                                <span className={style.statLabel}>Média Geral</span>
                                <RiLineChartLine />
                            </div>
                            <div className={style.statValue}>{stats.media_geral.toFixed(1)}</div>
                            <span className={`${style.statChange} ${stats.media_geral >= 10 ? style.positive : style.negative}`}>
                                {stats.media_geral >= 10 ? <RiArrowUpSLine /> : <RiArrowDownSLine />}
                                {stats.media_geral >= 10 ? 'Bom desempenho' : 'Abaixo da média'}
                            </span>
                        </div>
                        <div className={style.statCard}>
                            <div className={style.statHeader}>
                                <span className={style.statLabel}>Melhor Disciplina</span>
                                <RiMedalLine />
                            </div>
                            <div className={style.statValue}>{bestSubject.disciplina.substring(0, 15)}</div>
                            <span className={style.subjectBadge}>{bestSubject.media_final_valor.toFixed(1)} / 20</span>
                        </div>
                        <div className={style.statCard}>
                            <div className={style.statHeader}>
                                <span className={style.statLabel}>Status Acadêmico</span>
                                <RiExpandDiagonalLine />
                            </div>
                            <div className={`${style.statValue} ${stats.media_geral >= 10 ? style.statusOk : style.statusWarning}`}>
                                {stats.media_geral >= 14 ? 'Excelente' : stats.media_geral >= 10 ? 'Aprovado' : 'Reprovado'}
                            </div>
                            <span className={style.statSubtext}>Frequência: {stats.presenca_percentual}%</span>
                        </div>
                    </div>

                    <div className={style.tableWrapper}>
                        <table className={style.table}>
                            <thead>
                                <tr>
                                    <th>Disciplina</th>
                                    <th>1º Trimestre</th>
                                    <th>2º Trimestre</th>
                                    <th>3º Trimestre</th>
                                    <th>Média Final</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {loading ? (
                                    <tr><td colSpan="6">Carregando notas...</td></tr>
                                ) : stats.notas_por_disciplina.length > 0 ? (
                                    stats.notas_por_disciplina.map((item, index) => (
                                        <tr key={index}>
                                            <td className={style.subjectName}>{item.disciplina}</td>
                                            <td>{item.trimestres['1'].MT > 0 ? item.trimestres['1'].MT.toFixed(1) : '-'}</td>
                                            <td>{item.trimestres['2'].MT > 0 ? item.trimestres['2'].MT.toFixed(1) : '-'}</td>
                                            <td>{item.trimestres['3'].MT > 0 ? item.trimestres['3'].MT.toFixed(1) : '-'}</td>
                                            <td className={style.gradeAvg}>{item.media_final}</td>
                                            <td>
                                                <span className={`${style.badge} ${item.media_final_valor >= 14 ? style.excellent :
                                                    item.media_final_valor >= 10 ? style.approved :
                                                        item.count_mt === 3 ? style.rejected : style.pending
                                                    }`}>
                                                    {item.resultado === '---' ? 'Pendente' : item.resultado}
                                                </span>
                                            </td>
                                        </tr>
                                    ))
                                ) : (
                                    <tr><td colSpan="6">Nenhuma nota lançada ainda.</td></tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </main>
        </div>
    );
};

export default Grades;
