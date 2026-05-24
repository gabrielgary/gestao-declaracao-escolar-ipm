import React, { useEffect, useState } from 'react';
import style from './Attendance.module.css';
import '../../../../assets/style/global.style.css'
import MenuNavBarCliente from '../../../../Components/Elements/MenuNavBarCliente/MenuNavBarCliente'
import Header from '../../../../Components/Elements/Header/Header'
import { RiUserFollowLine, RiUserUnfollowLine, RiInformationLine } from 'react-icons/ri';
import { useAuth } from '../../../../Context/AuthContext';
import api from '../../../../Services/api';

const Attendance = () => {
    const { user } = useAuth();
    const [stats, setStats] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchAttendance = async () => {
            try {
                const response = await api.get(`/alunos/${user.id}/boletim/`);
                setStats(response.data.notas_por_disciplina);
                //console.log(stats);
                
                setLoading(false);
            } catch (error) {
                console.error("Erro ao buscar presenças:", error);
                setLoading(false);
            }
        };
        if (user?.id) fetchAttendance();
    }, [user]);

    return (
        <div className='containelGeralclient'>
            <MenuNavBarCliente user={'student'} />
            <main className='containelMainclient'>
                <Header text1="Estudante" text2="Presenças" />
                <div className={style.container}>
                    <header className={style.header}>
                        <h1>Controle de Presenças</h1>
                        <p>Monitore sua frequência escolar em cada disciplina.</p>
                    </header>

                    <div className={style.grid}>
                        {loading ? (
                            <p>Carregando presenças...</p>
                        ) : stats.length > 0 ? (
                            stats.map((item, index) => (
                                <div key={index} className={style.attendanceCard}>
                                    <div className={style.cardHeader}>
                                        <h3>{item.disciplina}</h3>
                                        <span className={item.presenca_percentual >= 90 ? style.badgeSuccess : style.badgeWarning}>
                                            {item.presenca_percentual.toFixed(1)}%
                                        </span>
                                    </div>

                                    <div className={style.progressBarContainer}>
                                        <div
                                            className={style.progressBar}
                                            style={{ width: `${item.presenca_percentual}%`, backgroundColor: item.presenca_percentual >= 90 ? 'var(--cor-primaria)' : 'var(--cor-aviso)' }}
                                        ></div>
                                    </div>

                                    <div className={style.cardDetails}>
                                        <div className={style.detailItem}>
                                            <RiUserFollowLine className={style.iconSuccess} />
                                            <span>{Math.round(40 * (item.presenca_percentual / 100))} Presenças</span>
                                        </div>
                                        <div className={style.detailItem}>
                                            <RiUserUnfollowLine className={style.iconDanger} />
                                            <span>{item.faltas} Faltas</span>
                                        </div>
                                    </div>
                                </div>
                            ))
                        ) : (
                            <p>Nenhum registro de frequência encontrado.</p>
                        )}
                    </div>

                    <div className={style.alertSection}>
                        <RiInformationLine />
                        <p>Lembre-se: A frequência mínima exigida para aprovação é de <strong>75%</strong> por disciplina.</p>
                    </div>
                </div>
            </main>
        </div>
    );
};

export default Attendance;
