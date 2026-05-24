import React, { useState, useEffect } from 'react';
import style from './TurmaModal.module.css';
import { IoClose } from 'react-icons/io5';
import api from '../../../Services/api';

const TurmaModal = ({ onClose, onSuccess }) => {
    const [formData, setFormData] = useState({
        ano: new Date().getFullYear(),
        id_sala: '',
        id_periodo: '',
        id_matriz_curricular: '',
        id_responsavel: ''
    });

    const [loading, setLoading] = useState(false);
    const [data, setData] = useState({
        salas: [],
        periodos: [],
        matrizes: [],
        funcionarios: []
    });

    useEffect(() => {
        const fetchOptions = async () => {
            try {
                const [salasRes, periodosRes, matrizesRes, funcionariosRes] = await Promise.all([
                    api.get('salas/'),
                    api.get('periodos/'),
                    api.get('matrizes-curriculares/?ativo=true'),
                    api.get('funcionarios/')
                ]);

                setData({
                    salas: salasRes.data.results || salasRes.data,
                    periodos: periodosRes.data.results || periodosRes.data,
                    matrizes: matrizesRes.data.results || matrizesRes.data,
                    funcionarios: funcionariosRes.data.results || funcionariosRes.data
                });
            } catch (error) {
                console.error("Erro ao carregar opções:", error);
            }
        };
        fetchOptions();
    }, []);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            await api.post('turmas/', formData);
            if (onSuccess) onSuccess();
            onClose();
        } catch (error) {
            console.error("Erro ao criar turma:", error);
            alert("Erro ao criar turma. Verifique os dados.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={style.modalOverlay}>
            <div className={style.modalContent}>
                <div className={style.header}>
                    <h2>Nova Turma</h2>
                    <button onClick={onClose} className={style.closeButton}>
                        <IoClose />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className={style.form}>
                    <div className={style.formGroup}>
                        <label>Matriz Curricular (Curso/Classe)</label>
                        <select
                            name="id_matriz_curricular"
                            value={formData.id_matriz_curricular}
                            onChange={handleChange}
                            required
                        >
                            <option value="">Selecione a Matriz...</option>
                            {data.matrizes.map(m => (
                                <option key={m.id_matriz_curricular} value={m.id_matriz_curricular}>
                                    {m.curso_nome} - {m.classe_nivel}ª Classe ({m.descricao || m.ano_letivo})
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className={style.formGroup}>
                        <label>Sala</label>
                        <select
                            name="id_sala"
                            value={formData.id_sala}
                            onChange={handleChange}
                            required
                        >
                            <option value="">Selecione a Sala...</option>
                            {data.salas.map(s => (
                                <option key={s.id_sala} value={s.id_sala}>
                                    Sala {s.numero_sala} (Cap: {s.capacidade_alunos})
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className={style.formGroup}>
                        <label>Período</label>
                        <select
                            name="id_periodo"
                            value={formData.id_periodo}
                            onChange={handleChange}
                            required
                        >
                            <option value="">Selecione o Período...</option>
                            {data.periodos.map(p => (
                                <option key={p.id_periodo} value={p.id_periodo}>
                                    {p.periodo}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className={style.formGroup}>
                        <label>Cordenador / Responsável</label>
                        <select
                            name="id_responsavel"
                            value={formData.id_responsavel}
                            onChange={handleChange}
                        >
                            <option value="">Selecione o Responsável...</option>
                            {data.funcionarios.map(f => (
                                <option key={f.id_funcionario} value={f.id_funcionario}>
                                    {f.nome_completo}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className={style.formGroup}>
                        <label>Ano Letivo</label>
                        <input
                            type="number"
                            name="ano"
                            value={formData.ano}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div className={style.actions}>
                        <button type="button" onClick={onClose} className={style.cancelBtn}>
                            Cancelar
                        </button>
                        <button type="submit" className={style.submitBtn} disabled={loading}>
                            {loading ? 'Criando...' : 'Criar Turma'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default TurmaModal;
