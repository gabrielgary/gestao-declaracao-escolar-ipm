import React, { useState, useEffect, useMemo } from 'react';
import style from './SolicitacaoFlow.module.css';
import { RiUser3Line, RiFileList3Line, RiWallet3Line, RiCheckLine, RiPrinterLine, RiSmartphoneLine, RiArrowRightLine, RiArrowLeftLine, RiSearchLine, RiErrorWarningLine } from 'react-icons/ri';
import api from '../../../Services/api';

import { useAuth } from '../../../Context/AuthContext';
import { getMediaUrl } from '../../../Utils/urlHelper';

const SolicitacaoFlow = ({ userType = 'aluno', fixedStudent = null, onComplete }) => {
    const { user } = useAuth();
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);
    const [studentInfo, setStudentInfo] = useState(fixedStudent);
    const [biSearch, setBiSearch] = useState('');
    const [myStudents, setMyStudents] = useState([]);

    const [selectedDoc, setSelectedDoc] = useState('');
    const [selectedClass, setSelectedClass] = useState('');
    const [classes, setClasses] = useState([]);

    const [paymentMethod, setPaymentMethod] = useState('');
    const [result, setResult] = useState(null);
    const [error, setError] = useState('');

    const [missingFields, setMissingFields] = useState({});
    const [isEditingMissing, setIsEditingMissing] = useState(false);

    // New state for confirmation modal
    const [showConfirmModal, setShowConfirmModal] = useState(false);
    const [pendingSolicitacao, setPendingSolicitacao] = useState(null);

    // Success modal state
    const [showSuccessModal, setShowSuccessModal] = useState(false);

    const docOptions = [
        { id: 'DECLARAÇÃO_EMPREGO', label: 'Declaração (Efeito de Emprego)' },
        { id: 'DECLARAÇÃO_PASSAPORTE', label: 'Declaração (Efeito de Passaporte)' },
        { id: 'DECLARAÇÃO_MATRICULA', label: 'Declaração (Efeito de Matrícula)' },
        { id: 'DECLARAÇÃO_OUTROS', label: 'Declaração (Outros Fins)' },
        { id: 'DECLARAÇÃO_APROVEITAMENTO', label: 'Declaração de Aproveitamento (Com Notas)' },
        { id: 'CERTIFICADO', label: 'Certificado de Conclusão' },
        { id: 'BOLETIM_1', label: 'Boletim (I Trimestre)' },
        { id: 'BOLETIM_2', label: 'Boletim (II Trimestre)' },
        { id: 'BOLETIM_3', label: 'Boletim (III Trimestre)' }
    ];

    // Fields to check
    const mandatoryFields = useMemo(() => [
        { key: 'nome_pai', label: 'Nome do Pai' },
        { key: 'nome_mae', label: 'Nome da Mãe' },
        { key: 'data_nascimento', label: 'Data de Nascimento', type: 'date' },
        { key: 'naturalidade', label: 'Naturalidade' },
        { key: 'provincia_naturalidade', label: 'Província de Naturalidade' },
        { key: 'data_emissao_bilhete', label: 'Data de Emissão do BI', type: 'date' }
    ], []);

    useEffect(() => {
        const fetchClasses = async () => {
            try {
                const response = await api.get('/classes/');
                setClasses(response.data.results || response.data);
            } catch (err) {
                console.error("Erro ao buscar classes", err);
            }
        };
        fetchClasses();
    }, []);

    useEffect(() => {
        // Desativado: Não travar mais a solicitação por falta de dados (Pai/Mãe/etc)
        setIsEditingMissing(false);
    }, [studentInfo]);

    const handleMissingFieldChange = (key, value) => {
        setMissingFields(prev => ({ ...prev, [key]: value }));
    };

    const saveMissingData = async () => {
        try {
            setLoading(true);
            setError('');
            // Validar se todos foram preenchidos
            for (const key in missingFields) {
                if (!missingFields[key]) {
                    setError(`Por favor, preencha o campo ${mandatoryFields.find(f => f.key === key).label}`);
                    setLoading(false);
                    return;
                }
            }

            await api.patch(`/alunos/${studentInfo.id_aluno}/`, missingFields);
            const updated = { ...studentInfo, ...missingFields };
            setStudentInfo(updated);
            setIsEditingMissing(false);
            setError('');
        } catch (error) {
            setError(`Erro ao atualizar dados do aluno. <br> Erro: ${error}`);
        } finally {
            setLoading(false);
        }
    };

    const availableClasses = useMemo(() => {
        // Filtra classes baseado na regra de negócio e no aluno selecionado
        if (!studentInfo || !selectedDoc || classes.length === 0) {
            return [];
        }

        // Extração robusta do nível da classe
        const currentLevel = parseInt(
            studentInfo.classe_nivel || 
            studentInfo.perfil?.id_turma?.id_classe?.nivel ||
            studentInfo.aluno?.id_turma?.id_classe?.nivel ||
            studentInfo.turma_detalhes?.classe?.nivel || 
            studentInfo.id_turma?.id_classe?.nivel || 
            0
        );

        let filtered = [];

        // Regras:
        // Declaração: < currentLevel
        // Boletim: <= currentLevel
        // Certificado: == 13
        const docUpper = selectedDoc.toUpperCase();
        
        if (docUpper.includes('DECLARAÇÃO')) {
            if (docUpper.includes('APROVEITAMENTO')) {
                // Com notas: apenas classes passadas
                filtered = classes.filter(c => c.nivel < currentLevel);
            } else {
                // Sem notas: permite a classe actual (igual ao boletim)
                filtered = classes.filter(c => c.nivel <= currentLevel);
            }
        } else if (docUpper.includes('CERTIFICADO')) {
            const isFinalista = studentInfo.status_aluno === 'Finalizou';
            // Só libera a 13ª classe se o status for explicitamente 'Finalizou'
            filtered = isFinalista ? classes.filter(c => c.nivel === 13) : [];
        } else {
            // Fallback para outros documentos (se houver)
            filtered = classes.filter(c => c.nivel <= currentLevel);
        }

        return filtered.sort((a, b) => b.nivel - a.nivel);
    }, [selectedDoc, studentInfo, classes]);

    useEffect(() => {
        const fetchMyStudents = async () => {
            try {
                if (user?.id || user?.id_aluno || user?.id_encarregado) {
                    const id = user.id_encarregado || user.id_aluno || user.id;
                    const response = await api.get(`/encarregados/${id}/educandos/`);
                    setMyStudents(response.data);
                }
            } catch {
                console.error("Erro ao buscar educandos");
            }
        };

        const fetchStudentInfo = async () => {
            try {
                setLoading(true);
                const id = user.id_aluno || user.id;
                const response = await api.get(`/alunos/${id}/`);
                setStudentInfo(response.data);
                setStep(2); // Vai direto para o passo de documento
            } catch (err) {
                console.error("Erro ao carregar dados do aluno", err);
                setError("Não foi possível carregar os seus dados académicos.");
            } finally {
                setLoading(false);
            }
        };

        if (fixedStudent) {
            setStudentInfo(fixedStudent);
            setStep(2);
        } else if (userType === 'aluno' && (user?.id || user?.id_aluno)) {
            fetchStudentInfo();
        } else if (userType === 'encarregado' && (user?.id || user?.id_encarregado)) {
            fetchMyStudents();
        }
    }, [fixedStudent, user, userType]);

    const handleStudentSelect = (e) => {
        const selectedId = e.target.value;
        if (!selectedId) return;
        const student = myStudents.find(s => s.id_aluno === parseInt(selectedId));
        if (student) {
            setStudentInfo(student);
            setError('');
        }
    };

    const confirmStudentSelection = () => {
        if (studentInfo) {
            setStep(2);
        }
    };

    const searchStudent = async () => {
        if (!biSearch) return;
        setLoading(true);
        setError('');
        try {
            const response = await api.get(`/alunos/?search=${biSearch}`);
            if (response.data.results && response.data.results.length > 0) {
                setStudentInfo(response.data.results[0]);
                setStep(2);
            } else {
                setError('Estudante não encontrado com este BI.');
            }
        } catch {
            setError('Erro ao pesquisar estudante.');
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async () => {
        if (!studentInfo || !selectedDoc) return;
        setLoading(true);
        setError('');
        try {
            const payload = {
                id_aluno: studentInfo.id_aluno,
                tipo_documento: selectedDoc,
                canal_pagamento_rup: paymentMethod === 'confirmado_local' ? 'fisico_rup' : paymentMethod,
                id_encarregado: userType === 'encarregado' ? (user.id_encarregado || user.id) : null,
                id_funcionario: userType === 'funcionario' ? (user.id_funcionario || user.id) : null,
                classe_solicitada: selectedClass || null
            };

            // 1. Criar Solicitação (Sempre cria pendente)
            const response = await api.post('/solicitacoes/', payload);
            const data = response.data;

            // Se for funcionário + Pagamento Instantâneo, abrir modal de conferência
            if (userType === 'funcionario' && paymentMethod === 'confirmado_local') {
                setPendingSolicitacao(data);
                setShowConfirmModal(true);
                setLoading(false);
                return;
            }

            // Fluxo normal (RUP para User/Funcionario que escolheu RUP)
            setResult(data);
            setStep(4);
            // Don't call onComplete immediately, let changes be viewed
            // if (onComplete) onComplete(data);

        } catch (err) {
            console.error(err);
            setError(err.response?.data?.error || 'Erro ao processar solicitação.');
        } finally {
            if (paymentMethod !== 'confirmado_local') {
                setLoading(false);
            }
        }
    };

    const handleConfirmPayment = async () => {
        if (!pendingSolicitacao) return;
        setLoading(true);
        try {
            // 2. Confirmar Pagamento
            const idSolicitacao = pendingSolicitacao.solicitacao ? pendingSolicitacao.solicitacao.id_solicitacao : pendingSolicitacao.id_solicitacao;

            const confirmResponse = await api.post(`/solicitacoes/${idSolicitacao}/confirmar_pagamento/`, {
                id_funcionario: user.id_funcionario || user.id
            });

            // Mesclar resultados
            const finalResult = { ...pendingSolicitacao, ...confirmResponse.data, confirmed: true };

            // Auto-open PDF if available
            if (finalResult.download_url || finalResult.caminho_arquivo) {
                const url = getMediaUrl(finalResult.download_url || finalResult.caminho_arquivo);
                // Try to open in new tab
                window.open(url, '_blank');
            }

            setResult(finalResult);
            setShowConfirmModal(false);
            setShowSuccessModal(true); // Show success modal instead of going directly to step 4
            // if (onComplete) onComplete(finalResult); 
        } catch (err) {
            console.error("ERRO AO CONFIRMAR PAGAMENTO:", {
                status: err.response?.status,
                data: err.response?.data,
                config: err.config
            });

            const msg = err.response?.data?.error || err.response?.data?.detail || "Erro ao confirmar pagamento.";
            setError(msg);
            alert(`Falha na confirmação: ${msg}`);
        } finally {
            setLoading(false);
        }
    };

    // Helper to print RUP
    const handlePrintRUP = async (id) => {
        try {
            setLoading(true);
            const response = await api.get(`/solicitacoes/${id}/imprimir_rup/`);
            if (response.data.download_url) {
                window.open(response.data.download_url, '_blank');
            } else {
                alert("Erro ao obter URL do RUP.");
            }
        } catch (error) {
            console.error("Erro ao imprimir RUP", error);
            alert("Não foi possível gerar o RUP.");
        } finally {
            setLoading(false);
        }
    };

    // Add a small helper component for Errors inside the flow
    const FlowError = ({ message }) => {
        if (!message) return null;
        return (
            <div className={style.errorContainer}>
                <RiErrorWarningLine className={style.errorIcon} />
                <p className={style.errorMsg} dangerouslySetInnerHTML={{ __html: message }}></p>
            </div>
        );
    };

    return (
        <div className={style.flowContainer}>
            {/* Modal de Confirmação de Pagamento Instantâneo */}
            {showConfirmModal && pendingSolicitacao && (
                <div className={style.modalOverlay}>
                    <div className={style.modalContent}>
                        <div className={style.modalHeader}>
                            <h3><RiWallet3Line /> Confirmar Pagamento</h3>
                        </div>
                        <div className={style.modalBody}>
                            <div className={style.rupDisplay}>
                                <label>Referência Bancária (RUP)</label>
                                <div className={style.rupCode}>{pendingSolicitacao.solicitacao?.rupe || '---'}</div>
                            </div>

                            <div className={style.detailsList}>
                                <p><strong>Aluno</strong> <span>{pendingSolicitacao.solicitacao?.aluno_nome}</span></p>
                                <p><strong>Documento</strong> <span>{pendingSolicitacao.solicitacao?.tipo_documento}</span></p>
                                <p><strong>Valor</strong> <strong>{pendingSolicitacao.fatura?.total ? new Intl.NumberFormat('pt-AO', { style: 'currency', currency: 'AOA' }).format(pendingSolicitacao.fatura.total) : '---'}</strong></p>
                            </div>

                            <div className={style.alertInfo}>
                                <RiErrorWarningLine />
                                <p>Confirme que recebeu o valor acima do requerente. A validação gera o documento imediatamente.</p>
                            </div>
                        </div>
                        <div className={style.modalActions}>
                            <button
                                className={style.btnCancel}
                                onClick={() => {
                                    setShowConfirmModal(false);
                                    setStep(4);
                                    setResult(pendingSolicitacao);
                                }}
                            >
                                Cancelar
                            </button>
                            <button
                                className={style.btnConfirm}
                                onClick={handleConfirmPayment}
                                disabled={loading}
                            >
                                {loading ? 'A confirmar...' : 'Confirmar Pagamento'}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Success Modal */}
            {showSuccessModal && result && (
                <div className={style.modalOverlay}>
                    <div className={style.modalContent}>
                        <div className={style.successIcon}>
                            <RiCheckLine />
                        </div>
                        <h2>Operação Concluída!</h2>
                        <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>
                            O pagamento foi validado e o documento já está pronto.
                        </p>

                        <div className={style.detailsList} style={{ textAlign: 'left', background: 'var(--bg-page)', padding: '1.5rem', borderRadius: '16px', marginBottom: '2rem' }}>
                            <p style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>
                                <strong>Documento:</strong> {result.solicitacao?.tipo_documento || result.tipo_documento}
                            </p>
                            <p style={{ paddingTop: '0.5rem' }}>
                                <strong>Aluno:</strong> {result.solicitacao?.aluno_nome || result.aluno_nome}
                            </p>
                        </div>

                        <div className={style.modalActions} style={{ justifyContent: 'center' }}>
                            <button
                                className={style.btnPrev}
                                onClick={() => {
                                    setShowSuccessModal(false);
                                    setStep(1);
                                    setStudentInfo(fixedStudent);
                                    setSelectedDoc('');
                                    setSelectedClass('');
                                    setPaymentMethod('');
                                    setResult(null);
                                }}
                            >
                                Nova Solicitação
                            </button>
                            <button
                                className={style.btnSubmit}
                                onClick={() => {
                                    setShowSuccessModal(false);
                                    setStep(4);
                                }}
                            >
                                <RiCheckLine /> Ver Detalhes
                            </button>
                        </div>
                    </div>
                </div>
            )}

            <div className={style.stepper}>
                <div className={`${style.step} ${step >= 1 ? style.active : ''}`}>
                    <div className={style.stepIcon}><RiUser3Line /></div>
                    <span>Identificação</span>
                </div>
                <div className={style.stepLine} />
                <div className={`${style.step} ${step >= 2 ? style.active : ''}`}>
                    <div className={style.stepIcon}><RiFileList3Line /></div>
                    <span>Documento</span>
                </div>
                <div className={style.stepLine} />
                <div className={`${style.step} ${step >= 3 ? style.active : ''}`}>
                    <div className={style.stepIcon}><RiWallet3Line /></div>
                    <span>Pagamento</span>
                </div>
            </div>

            <div className={style.stepContent}>
                {step === 1 && (
                    <div className={style.stepIn}>
                        <h2>Quem está a solicitar?</h2>
                        <p>Identifique o estudante para o qual deseja emitir o documento oficial.</p>

                        {userType === 'encarregado' && myStudents.length > 0 ? (
                            <div className={style.confirmCard}>
                                <label style={{ fontWeight: '600', marginBottom: '0.5rem', display: 'block' }}>Seus Educandos</label>
                                <select
                                    className={style.selectField}
                                    onChange={handleStudentSelect}
                                    defaultValue=""
                                >
                                    <option value="" disabled>Escolha o aluno...</option>
                                    {myStudents.map(student => (
                                        <option key={student.id_aluno} value={student.id_aluno}>
                                            {student.nome_completo} ({student.classe_nivel}ª Classe)
                                        </option>
                                    ))}
                                </select>

                                <div className={style.actions}>
                                    <button
                                        className={style.btnNext}
                                        onClick={confirmStudentSelection}
                                        disabled={!studentInfo}
                                    >
                                        Continuar <RiArrowRightLine />
                                    </button>
                                </div>
                                <FlowError message={error} />
                            </div>
                        ) : (
                            <div className={style.stepIn}>
                                <div className={style.searchBox}>
                                    <input
                                        type="text"
                                        placeholder="Número do Bilhete de Identidade (BI)"
                                        value={biSearch}
                                        onChange={(e) => setBiSearch(e.target.value.toUpperCase())}
                                        onKeyPress={(e) => e.key === 'Enter' && searchStudent()}
                                    />
                                    <button onClick={searchStudent} disabled={loading}>
                                        {loading ? '...' : <RiSearchLine />}
                                    </button>
                                </div>
                                <FlowError message={error} />
                            </div>
                        )}
                    </div>
                )}

                {step === 2 && studentInfo && (
                    <div className={style.stepIn}>
                        <h2>Confirmar Dados e Documento</h2>
                        <p>Verifique se os dados do estudante estão corretos antes de emitir o documento.</p>

                        <div className={style.confirmCard}>
                            <div className={style.studentProfileHeader}>
                                <div className={style.avatar}>
                                    {studentInfo.img_path ? <img src={studentInfo.img_path} alt="" /> : <RiUser3Line />}
                                </div>
                                <div className={style.profileInfo}>
                                    <h3>{studentInfo.nome_completo || studentInfo.nome}</h3>
                                    <div className={style.badgeRow}>
                                        <span className={style.statusBadge}>{studentInfo.status_aluno || 'Activo'}</span>
                                        <span className={style.classBadge}>
                                            {studentInfo.classe_nivel || studentInfo.id_turma?.id_classe?.nivel || '?'}ª Classe
                                        </span>
                                    </div>
                                </div>
                                <button className={style.btnOutline} onClick={() => setStep(1)}>
                                    Trocar Aluno
                                </button>
                            </div>

                            <div className={style.infoGrid}>
                                <div className={style.infoItem}>
                                    <label>Número de BI</label>
                                    <strong>{studentInfo.numero_bi}</strong>
                                </div>
                                <div className={style.infoItem}>
                                    <label>Nº de Matrícula</label>
                                    <strong>{studentInfo.numero_matricula || 'N/A'}</strong>
                                </div>
                                <div className={style.infoItem}>
                                    <label>Curso Atual</label>
                                    <strong>{studentInfo.curso_nome || studentInfo.id_turma?.id_curso?.nome_curso || 'N/A'}</strong>
                                </div>
                               
                            </div>

                            <div className={style.selectionSection}>
                                <div className={style.formGroup}>
                                    <label>Documento de Solicitação</label>
                                    <select className={style.selectField} value={selectedDoc} onChange={(e) => {
                                        setSelectedDoc(e.target.value);
                                        setSelectedClass('');
                                        setError('');
                                    }}>
                                        <option value="">Escolha uma opção...</option>
                                        {docOptions.map(opt => (
                                            <option key={opt.id} value={opt.id}>{opt.label}</option>
                                        ))}
                                    </select>
                                </div>

                                {selectedDoc && !error && (
                                    <div className={style.formGroup} style={{ marginTop: '1.5rem' }}>
                                        <label>Referente à Classe</label>
                                        <select
                                            className={style.selectField}
                                            value={selectedClass}
                                            onChange={(e) => setSelectedClass(e.target.value)}
                                            disabled={availableClasses.length === 0}
                                        >
                                            <option value="">Selecione a classe acadêmica...</option>
                                            {availableClasses.map(cls => (
                                                <option key={cls.id_classe} value={cls.id_classe}>
                                                    {cls.nivel}ª Classe ({cls.descricao})
                                                </option>
                                            ))}
                                        </select>
                                        {availableClasses.length === 0 && (
                                            <span className={style.helperText}>Nenhuma classe compatível encontrada para este documento.</span>
                                        )}
                                    </div>
                                )}
                            </div>
                            
                            <FlowError message={error} />

                            <div className={style.actions}>
                                <button className={style.btnPrev} onClick={() => setStep(1)}>
                                    <RiArrowLeftLine /> Voltar
                                </button>
                                <button
                                    className={style.btnNext}
                                    onClick={() => setStep(3)}
                                    disabled={!selectedDoc || !selectedClass}
                                >
                                    Próximo Passo <RiArrowRightLine />
                                </button>
                            </div>
                        </div>
                    </div>
                )}

                {step === 3 && (
                    <div className={style.stepIn}>
                        <h2>Opções de Pagamento</h2>
                        <p>Selecione um dos métodos de pagamento autorizados abaixo.</p>

                        <div className={style.paymentGrid}>
                            {/* Multicaixa Express (Indisponível mas visual) */}
                            <div className={`${style.paymentOption} ${style.disabled}`}>
                                <RiSmartphoneLine className={style.payIcon} />
                                <span className={style.badge} style={{ background: '#64748b' }}>EM BREVE</span>
                                <h3>MCX Express</h3>
                                <p>Pagamento via smartphone.</p>
                            </div>

                            <div
                                className={`${style.paymentOption} ${paymentMethod === 'fisico_rup' ? style.selected : ''}`}
                                onClick={() => setPaymentMethod('fisico_rup')}
                            >
                                <RiPrinterLine className={style.payIcon} />
                                <h3>Referência RUP</h3>
                                <p>Pague no ATM ou Internet Banking.</p>
                            </div>

                            {userType === 'funcionario' && (
                                <div
                                    className={`${style.paymentOption} ${style.premiumOption} ${paymentMethod === 'confirmado_local' ? style.selected : ''}`}
                                    onClick={() => setPaymentMethod('confirmado_local')}
                                >
                                    <RiWallet3Line className={style.payIcon} />
                                    <span className={style.badge} style={{ background: '#f59e0b' }}>LOCAL</span>
                                    <h3>Pagamento Local</h3>
                                    <p>Confirmar recebimento direto.</p>
                                </div>
                            )}
                        </div>

                        {paymentMethod === 'confirmado_local' && (
                            <div className={style.alertInfo} style={{ marginTop: '2rem', maxWidth: '600px' }}>
                                < RiErrorWarningLine />
                                <p><strong>Atenção:</strong> Use esta opção APENAS se já tiver sido pago o valor em na usando o TPA da INSTITUIÇÃO. A emissão será irreversível.</p>
                            </div>
                        )}

                        <FlowError message={error} />

                        <div className={style.actions}>
                            <button className={style.btnPrev} onClick={() => setStep(2)}>
                                <RiArrowLeftLine /> Voltar
                            </button>
                            <button
                                className={style.btnSubmit}
                                onClick={handleSubmit}
                                disabled={!paymentMethod || loading}
                            >
                                {loading ? 'A processar...' : 'Finalizar Solicitação'}
                            </button>
                        </div>
                    </div>
                )}

                {step === 4 && result && (
                    <div className={`${style.stepIn} ${style.successStep}`}>
                        <div className={style.successIcon}><RiCheckLine /></div>
                        <h2>Solicitação Concluída!</h2>
                        <p>O pedido foi registado no sistema com sucesso.</p>

                        <div className={style.rupAviso} style={result.confirmed ? { borderColor: '#10b981', background: 'rgba(16, 185, 129, 0.05)' } : {}}>
                            <RiPrinterLine style={result.confirmed ? { color: '#10b981' } : {}} />
                            <div>
                                <h4>{result.confirmed ? 'Documento Pronto' : 'Aguardando Pagamento'}</h4>
                                <p>{result.confirmed ? 'O documento oficial já foi gerado e assinado digitalmente.' : 'Imprima o RUP e efetue o pagamento para libertar o documento.'}</p>
                                
                                <button
                                    className={style.btnSubmit}
                                    style={{ marginTop: '1rem', background: result.confirmed ? '#10b981' : '#f59e0b' }}
                                    onClick={() => {
                                        if (result.confirmed) {
                                            window.open(getMediaUrl(result.download_url || result.caminho_arquivo), '_blank');
                                        } else {
                                            handlePrintRUP(result.solicitacao?.id_solicitacao || result.id_solicitacao);
                                        }
                                    }}
                                >
                                    {result.confirmed ? 'Imprimir Documento (.pdf)' : 'Imprimir Guia RUP (.pdf)'}
                                </button>
                            </div>
                        </div>

                        <div className={style.actions}>
                            <button
                                className={style.btnPrev}
                                onClick={() => onComplete && onComplete(result)}
                            >
                                Concluir e Sair
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default SolicitacaoFlow;
