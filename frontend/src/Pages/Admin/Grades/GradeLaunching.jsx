import React, { useState, useEffect } from 'react';
import style from './GradeLaunching.module.css';
import NavBarMenu from '../../../Components/Elements/NavBarMenu/NavBarMenu';
import Header from '../../../Components/Elements/Header/Header';
import { useAuth } from '../../../Context/AuthContext';
import api from '../../../Services/api';
import { RiSave3Line, RiFilter2Line, RiUser3Line } from 'react-icons/ri';
import { FaGraduationCap } from 'react-icons/fa6';
import Loading from '../../../Components/Elements/Loading/Loading';

const GradeLaunching = () => {
    const { user } = useAuth();
    const [assignments, setAssignments] = useState([]);
    const [selectedAssignment, setSelectedAssignment] = useState(null);
    const [students, setStudents] = useState([]);
    const [loading, setLoading] = useState(false);
    const [saving, setSaving] = useState(false);

    const [trimestre, setTrimestre] = useState('1');
    const [tipoNota, setTipoNota] = useState('MAC');
    const [grades, setGrades] = useState({}); // { studentId: value }

    const [message, setMessage] = useState({ type: '', text: '' });

    // 1. Carregar turmas/disciplinas vinculadas ao professor
    useEffect(() => {
        const fetchAssignments = async () => {
            try {
                // Se for admin, talvez queira todas? Por enquanto focamos no professor logado
                const response = await api.get(`/professor-disciplina/?id_funcionario=${user.id}`);
                setAssignments(response.data.results || response.data);
            } catch (error) {
                console.error("Erro ao carregar vinculações:", error);
            }
        };
        if (user?.id) fetchAssignments();
    }, [user]);

    // 2. Carregar alunos quando a turma for selecionada
    useEffect(() => {
        const fetchStudents = async () => {
            if (!selectedAssignment) return;
            setLoading(true);
            try {
                const response = await api.get(`/alunos/?id_turma=${selectedAssignment.id_turma}`);
                const studentsList = response.data.results || response.data;
                setStudents(studentsList);

                // Inicializar objeto de notas
                const initialGrades = {};
                studentsList.forEach(s => initialGrades[s.id_aluno] = '');

                // Opcional: Buscar notas já existentes para este contexto
                fetchExistingGrades(selectedAssignment, initialGrades);

            } catch (error) {
                console.error("Erro ao carregar alunos:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchStudents();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [selectedAssignment]);

    const fetchExistingGrades = async (assignment, currentGrades) => {
        try {
            const response = await api.get(`/notas/?id_turma=${assignment.id_turma}&id_disciplina=${assignment.id_disciplina}&trimestre=${trimestre}&tipo_nota=${tipoNota}`);
            const existing = response.data.results || response.data;
            const updated = { ...currentGrades };
            existing.forEach(n => {
                updated[n.id_aluno] = n.valor;
            });
            setGrades(updated);
        } catch (err) {
            console.warn("Erro ao buscar notas existentes", err);
        }
    };

    // Recarregar notas quando mudar trimestre/tipo
    useEffect(() => {
        if (selectedAssignment && students.length > 0) {
            const currentGrades = {};
            students.forEach(s => currentGrades[s.id_aluno] = '');
            fetchExistingGrades(selectedAssignment, currentGrades);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [trimestre, tipoNota]);

    const handleGradeChange = (studentId, value) => {
        if (value === '' || (parseFloat(value) >= 0 && parseFloat(value) <= 20)) {
            setGrades(prev => ({ ...prev, [studentId]: value }));
        }
    };

    const handleSave = async (e) => {
        e.preventDefault();
        setSaving(true);
        setMessage({ type: '', text: '' });

        try {
            const payload = {
                id_turma: selectedAssignment.id_turma,
                id_disciplina: selectedAssignment.id_disciplina,
                id_professor: user.id,
                trimestre: trimestre,
                tipo_nota: tipoNota,
                notas: Object.entries(grades)
                    .filter(([, val]) => val !== '')
                    .map(([id, val]) => ({
                        id_aluno: parseInt(id),
                        valor: parseFloat(val)
                    }))
            };

            await api.post('notas/lancar_lote/', payload);
            setMessage({ type: 'success', text: 'Notas lançadas com sucesso!' });
        } catch (error) {
            setMessage({ type: 'error', text: error.response?.data?.error || 'Erro ao salvar notas.' });
        } finally {
            setSaving(false);
        }
    };

    return (
        <div className={'ContainerGeneral'}>
            <NavBarMenu />
            <main className={'ContainerMain'}>
                <Header text1={"Académico"} text2={"Lançamento de Notas"} />

                <div className={style.content}>
                    <section className={style.controls}>
                        <div className={style.filterGroup}>
                            <label><RiFilter2Line /> Turma & Disciplina</label>
                            <select
                                value={selectedAssignment?.id_professor_disciplina || ''}
                                onChange={(e) => {
                                    const ass = assignments.find(a => a.id_professor_disciplina === parseInt(e.target.value));
                                    setSelectedAssignment(ass);
                                }}
                            >
                                <option value="">Selecione sua turma...</option>
                                {assignments.map(a => (
                                    <option key={a.id_professor_disciplina} value={a.id_professor_disciplina}>
                                        {a.turma_codigo} - {a.disciplina_nome}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div className={style.filterGroup}>
                            <label>Trimestre</label>
                            <select value={trimestre} onChange={(e) => setTrimestre(e.target.value)}>
                                <option value="1">1º Trimestre</option>
                                <option value="2">2º Trimestre</option>
                                <option value="3">3º Trimestre</option>
                            </select>
                        </div>

                        <div className={style.filterGroup}>
                            <label>Tipo de Nota</label>
                            <select value={tipoNota} onChange={(e) => setTipoNota(e.target.value)}>
                                <option value="MAC">MAC (Contínua)</option>
                                <option value="PP">PP (Prova Professor)</option>
                                <option value="PT">PT (Prova Trimestral)</option>
                            </select>
                        </div>
                    </section>

                    {message.text && (
                        <div className={`${style.alert} ${style[message.type]}`}>
                            {message.text}
                        </div>
                    )}

                    <div className={style.tableWrapper}>
                        {loading ? (
                            <p className={style.empty}><Loading /></p>
                        ) : selectedAssignment ? (
                            <form onSubmit={handleSave}>
                                <table className={style.gradesTable}>
                                    <thead>
                                        <tr>
                                            <th>Estudante</th>
                                            <th style={{ width: '120px' }}>Nota (0-20)</th>
                                            <th>Status</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {students.map(student => (
                                            <tr key={student.id_aluno}>
                                                <td>
                                                    <div className={style.studentInfo}>
                                                        {student.img_path ? <img src={student.img_path} alt="" /> : <RiUser3Line />}
                                                        <div>
                                                            <strong>{student.nome_completo}</strong>
                                                            <span>{student.numero_matricula}</span>
                                                        </div>
                                                    </div>
                                                </td>
                                                <td>
                                                    <input
                                                        type="number"
                                                        step="0.1"
                                                        min="0"
                                                        max="20"
                                                        placeholder="0.0"
                                                        value={grades[student.id_aluno] || ''}
                                                        onChange={(e) => handleGradeChange(student.id_aluno, e.target.value)}
                                                        className={parseFloat(grades[student.id_aluno]) < 10 ? style.fail : ''}
                                                    />
                                                </td>
                                                <td>
                                                    {grades[student.id_aluno] !== '' && (
                                                        <span className={parseFloat(grades[student.id_aluno]) >= 10 ? style.statusOk : style.statusFail}>
                                                            {parseFloat(grades[student.id_aluno]) >= 10 ? 'Aprovado' : 'Reprovado'}
                                                        </span>
                                                    )}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>

                                <div className={style.footer}>
                                    <p>{students.length} alunos listados</p>
                                    <button type="submit" className={style.btnSave} disabled={saving}>
                                        <RiSave3Line /> {saving ? 'Salvando...' : 'Salvar Notas'}
                                    </button>
                                </div>
                            </form>
                        ) : (
                            <div className={style.noSelection}>
                                <FaGraduationCap size={60} />
                                <p>Selecione uma Turma e Disciplina para começar o lançamento.</p>
                            </div>
                        )}
                    </div>
                </div>
            </main>
        </div>
    );
};

export default GradeLaunching;
