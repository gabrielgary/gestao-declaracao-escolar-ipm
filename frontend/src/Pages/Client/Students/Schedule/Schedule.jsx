import React, { useEffect, useState } from 'react';
import style from './Schedule.module.css';
import '../../../../assets/style/global.style.css'
import MenuNavBarCliente from '../../../../Components/Elements/MenuNavBarCliente/MenuNavBarCliente'
import Header from '../../../../Components/Elements/Header/Header'
import { RiCalendar2Line, RiTimeLine, RiMapPin2Line, RiBook3Line } from 'react-icons/ri';
import { useAuth } from '../../../../Context/AuthContext';
import api from '../../../../Services/api';

const Schedule = () => {
    const { user } = useAuth();
    const [horarios, setHorarios] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchSchedule = async () => {
            try {
                const response = await api.get(`/alunos/${user.id}/horario/`);
                setHorarios(response.data);
                setLoading(false);
            } catch (error) {
                console.error("Erro ao buscar horários:", error);
                setLoading(false);
            }
        };
        if (user?.id) fetchSchedule();
    }, [user]);

    // Grouping logic for the grid
    const timeSlots = Array.from(new Set(horarios.map(h => `${h.hora_inicio.substring(0, 5)} - ${h.hora_fim.substring(0, 5)}`))).sort();

    const getSubjectForDay = (slot, day) => {
        const h = horarios.find(item =>
            `${item.hora_inicio.substring(0, 5)} - ${item.hora_fim.substring(0, 5)}` === slot &&
            item.dia_semana === day
        );
        return h ? h.disciplina_nome : '---';
    };

    return (
        <div className='containelGeralclient'>
            <MenuNavBarCliente user={'student'} />
            <main className='containelMainclient'>
                <Header text1="Estudante" text2="Horários" />
                <div className={style.container}>
                    <header className={style.header}>
                        <h1>Meu Horário Semanal</h1>
                        <p>Confira a programação das suas aulas para a semana atual.</p>
                    </header>

                    <div className={style.scheduleWrapper}>
                        <div className={style.grid}>
                            <div className={style.headerRow}>
                                <div className={style.timeCol}><RiTimeLine /> Horário</div>
                                <div>Segunda</div>
                                <div>Terça</div>
                                <div>Quarta</div>
                                <div>Quinta</div>
                                <div>Sexta</div>
                            </div>

                            {loading ? (
                                <div className={style.row}><div className={style.timeCell} style={{ width: '100%' }}>Carregando horários...</div></div>
                            ) : timeSlots.length > 0 ? (
                                timeSlots.map((slot, i) => (
                                    <div key={i} className={style.row}>
                                        <div className={style.timeCell}>{slot}</div>
                                        <div className={style.subjectCell}><span>{getSubjectForDay(slot, 'Segunda-feira')}</span></div>
                                        <div className={style.subjectCell}><span>{getSubjectForDay(slot, 'Terça-feira')}</span></div>
                                        <div className={style.subjectCell}><span>{getSubjectForDay(slot, 'Quarta-feira')}</span></div>
                                        <div className={style.subjectCell}><span>{getSubjectForDay(slot, 'Quinta-feira')}</span></div>
                                        <div className={style.subjectCell}><span>{getSubjectForDay(slot, 'Sexta-feira')}</span></div>
                                    </div>
                                ))
                            ) : (
                                <div className={style.row}><div className={style.timeCell} style={{ width: '100%' }}>Nenhum horário definido para esta turma.</div></div>
                            )}
                        </div>
                    </div>

                    <div className={style.infoSection}>
                        <div className={style.infoCard}>
                            <RiMapPin2Line />
                            <div>
                                <h4>Localização</h4>
                                <p>Sua sala de aula habitual</p>
                            </div>
                        </div>
                        <div className={style.infoCard}>
                            <RiCalendar2Line />
                            <div>
                                <h4>Semana Acadêmica</h4>
                                <p>Semestre Corrente</p>
                            </div>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
};

export default Schedule;
