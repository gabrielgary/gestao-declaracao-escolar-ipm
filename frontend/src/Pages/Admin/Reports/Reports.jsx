
import React, { useState, useEffect, useMemo } from 'react';
import style from './Reports.module.css';
import { 
    HiOutlineClipboardList, 
    HiOutlineUsers, 
    HiOutlineTrendingUp, 
    HiOutlineShieldCheck, 
    HiOutlineSearch,
    HiOutlineDownload,
    HiOutlineDatabase
} from 'react-icons/hi';
import { FaFilePdf, FaFileCsv } from 'react-icons/fa';
import api from '../../../Services/api';
import NavBarMenu from '../../../Components/Elements/NavBarMenu/NavBarMenu';
import Header from '../../../Components/Elements/Header/Header';
import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';

import insignia from '../../../assets/images/insigna_angola.png';

const Reports = () => {
    const [activeTab, setActiveTab] = useState('solicitacoes');
    const [rawData, setRawData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    
    // Filtros
    const [filters, setFilters] = useState({
        status: '',
        start_date: '',
        end_date: '',
        mes: new Date().getMonth() + 1,
        ano: new Date().getFullYear(),
        tipo_auditoria: 'historico',
        classe: '',
        turma: '',
        cargo: ''
    });

    // Metadados
    const [metadata, setMetadata] = useState({
        classes: [],
        turmas: [],
        cargos: []
    });

    const tabs = [
        { id: 'solicitacoes', label: 'Solicitações', icon: <HiOutlineClipboardList />, color: 'var(--cor-primaria)' },
      //  { id: 'mensal', label: 'Financeiro', icon: <HiOutlineTrendingUp />, color: 'var(--cor-sucesso)' },
        { id: 'alunos', label: 'Estudantes', icon: <HiOutlineUsers />, color: 'var(--cor-info)' },
        { id: 'funcionarios', label: 'Recursos Humanos', icon: <HiOutlineUsers />, color: 'var(--cor-secundaria)' },
        { id: 'auditoria', label: 'Auditoria', icon: <HiOutlineShieldCheck />, color: 'var(--cor-aviso)' },
    ];

    useEffect(() => {
        const fetchMeta = async () => {
            try {
                const [classesRes, turmasRes, cargosRes] = await Promise.all([
                    api.get('classes/'),
                    api.get('turmas/'),
                    api.get('cargos/')
                ]);
                setMetadata({
                    classes: classesRes.data.results || classesRes.data,
                    turmas: turmasRes.data.results || turmasRes.data,
                    cargos: cargosRes.data.results || cargosRes.data
                });
            } catch (err) {
                console.error("Erro ao carregar metadados", err);
            }
        };
        fetchMeta();
    }, []);

    // Busca de dados (Dump inteligente conforme a Tab)
    useEffect(() => {
        const fetchTabData = async () => {
            setLoading(true);
            try {
                let endpoint = '';
                switch(activeTab) {
                    case 'solicitacoes': endpoint = 'reports/data/solicitacoes/'; break;
                    case 'mensal': endpoint = `reports/mensal/?format=json&mes=${filters.mes}&ano=${filters.ano}`; break;
                    case 'alunos': endpoint = 'reports/data/alunos/'; break;
                    case 'funcionarios': endpoint = 'reports/data/funcionarios/'; break;
                    case 'auditoria': endpoint = 'reports/data/auditoria/'; break;
                    default: endpoint = 'reports/data/solicitacoes/';
                }
                const response = await api.get(endpoint);
                setRawData(Array.isArray(response.data) ? response.data : []);
            } catch (error) {
                console.error('Erro ao buscar dados:', error);
                setRawData([]);
            } finally {
                setLoading(false);
            }
        };
        fetchTabData();
    }, [activeTab, filters.mes, filters.ano]);

    // Filtragem Local
    const filteredData = useMemo(() => {
        return rawData.filter(item => {
            const stringified = JSON.stringify(item).toLowerCase();
            if (searchTerm && !stringified.includes(searchTerm.toLowerCase())) return false;

            if (activeTab === 'solicitacoes') {
                if (filters.status && item.status_solicitacao !== filters.status) return false;
            }
            if (activeTab === 'alunos') {
                if (filters.classe && item.id_classe !== parseInt(filters.classe)) return false;
                if (filters.turma && item.id_turma !== parseInt(filters.turma)) return false;
            }
            if (activeTab === 'funcionarios') {
                if (filters.cargo && item.id_cargo !== parseInt(filters.cargo)) return false;
            }
            return true;
        });
    }, [rawData, searchTerm, filters, activeTab]);

    // Cálculo de KPIs dinâmicos
    const kpis = useMemo(() => {
        const total = filteredData.length;
        let secondary = 0;
        let tertiary = "N/A";

        if (activeTab === 'solicitacoes') {
            secondary = filteredData.reduce((acc, curr) => acc + (parseFloat(curr.valor_rupe) || 0), 0);
            tertiary = "Total Arrecadado";
        } else if (activeTab === 'mensal') {
            secondary = filteredData.reduce((acc, curr) => acc + (parseFloat(curr.total) || 0), 0);
            tertiary = "Total Mensal (Bruto)";
        } else if (activeTab === 'alunos') {
            secondary = filteredData.filter(a => a.genero === 'M').length;
            tertiary = "Alunos Masculinos";
        } else if (activeTab === 'funcionarios') {
            secondary = filteredData.filter(f => f.status_funcionario === 'Activo').length;
            tertiary = "Colaboradores Activos";
        }

        return { total, secondary, tertiary };
    }, [filteredData, activeTab]);

    // Geração de PDF Premium (Front-end)
    const handleGeneratePDF = () => {
        const doc = new jsPDF('p', 'mm', 'a4');
        const tabInfo = tabs.find(t => t.id === activeTab);
        
        // Configurações Globais
        const title = `RELATÓRIO DE ${tabInfo.label.toUpperCase()}`;
        
        // 1. Cabeçalho Oficial
        doc.addImage(insignia, 'PNG', 90, 10, 30, 30);
        doc.setFontSize(10);
        doc.setFont('Helvetica', 'bold');
        doc.text("REPÚBLICA DE ANGOLA", 105, 45, { align: "center" });
        doc.text("MINISTÉRIO DA EDUCAÇÃO", 105, 50, { align: "center" });
        doc.text("INSTITUTO POLITÉCNICO MAIOMBE - SEQUELE", 105, 55, { align: "center" });
        
        doc.setLineWidth(0.5);
        doc.line(15, 60, 195, 60);

        // 2. Título e Infos
        doc.setFontSize(16);
        doc.text(title, 105, 75, { align: "center" });
        
        doc.setFontSize(9);
        doc.setFont('Helvetica', 'normal');
        doc.text(`Data de Emissão: ${new Date().toLocaleString()}`, 15, 85);
        doc.text(`Responsável: Administrador do Sistema`, 15, 90);
        doc.text(`Contagem de Registos: ${filteredData.length}`, 195, 85, { align: "right" });

        // 3. Tabela de Dados
        let columns = [];
        let rows = [];

        if (activeTab === 'solicitacoes') {
            columns = ["Ref / ID", "Estudante", "Tipo de Documento", "Data / Hora", "Status", "Valor (AKZ)"];
            rows = filteredData.map(s => [
                s.rupe || `#${s.id_solicitacao}`, 
                s.aluno_nome, 
                s.tipo_documento, 
                new Date(s.data_solicitacao).toLocaleDateString(), 
                s.status_solicitacao.toUpperCase(), 
                `${(s.valor_rupe || 0).toLocaleString()} Kz`
            ]);
        } else if (activeTab === 'mensal') {
            columns = ["Categoria de Documento", "Quantidade Emitida", "Total Arrecadado (AKZ)"];
            rows = filteredData.map(m => [m.tipo, m.quantidade, `${(m.total || 0).toLocaleString()} Kz`]);
        } else if (activeTab === 'alunos') {
            columns = ["Nome Completo", "Bilhete de Identidade (BI)", "Género", "Turma Atual", "Curso Académico"];
            rows = filteredData.map(a => [a.nome_completo, a.numero_bi, a.genero, a.turma_codigo || '-', a.curso_nome || '-']);
        } else if (activeTab === 'funcionarios') {
            columns = ["Nome Completo", "Cargo / Função", "Contacto Telefónico", "Estado"];
            rows = filteredData.map(f => [f.nome_completo, f.cargo_nome || '-', f.telefone, f.status_funcionario]);
        } else if (activeTab === 'auditoria') {
            columns = ["Acção / Evento", "Utilizador", "Data e Hora", "Alterações"];
            rows = filteredData.map(item => [
                item.tipo_accao, 
                item.usuario_nome, 
                new Date(item.data_hora).toLocaleString(), 
                item.dados_novos ? JSON.stringify(item.dados_novos).substring(0, 50) + '...' : '-'
            ]);
        }

        autoTable(doc, {
            startY: 95,
            head: [columns],
            body: rows,
            theme: 'grid',
            headStyles: { fillColor: [0, 0, 0], textColor: [255, 255, 255], fontStyle: 'bold', fontSize: 8 },
            bodyStyles: { fontSize: 8, cellPadding: 3 },
            alternateRowStyles: { fillColor: [245, 245, 245] },
            margin: { top: 95 },
            didDrawPage: (data) => {
                // Rodapé com paginação
                doc.setFontSize(8);
                const str = `Página ${doc.internal.getNumberOfPages()}`;
                doc.text(str, data.settings.margin.left, doc.internal.pageSize.height - 10);
                doc.text("Documento processado por computador via IP Maiombe", 195, doc.internal.pageSize.height - 10, { align: "right" });
            }
        });

        doc.save(`${activeTab}_report_${new Date().getTime()}.pdf`);
    };

    return (
        <div className={'ContainerGeneral'}>
            <NavBarMenu />
            <main className={'ContainerMain'}>
                <Header text1={"Administração"} text2={"Central de Relatórios"} onSearch={setSearchTerm} />
                
                <div className={style.ReportsContainer}>
                    {/* Dashboard de KPIs */}
                    <div className={style.StatsGrid}>
                        <div className={style.StatCard}>
                            <div className={style.StatIcon} style={{ background: tabs.find(t=>t.id===activeTab).color }}>
                                <HiOutlineDatabase />
                            </div>
                            <div className={style.StatInfo}>
                                <h3>{kpis.total}</h3>
                                <p>Registos Filtrados</p>
                            </div>
                        </div>
                        <div className={style.StatCard}>
                            <div className={style.StatIcon} style={{ background: 'var(--cor-sucesso)' }}>
                                <HiOutlineTrendingUp />
                            </div>
                            <div className={style.StatInfo}>
                                <h3>{activeTab.includes('solicitacoes') || activeTab === 'mensal' ? kpis.secondary.toLocaleString() + " Kz" : kpis.secondary}</h3>
                                <p>{kpis.tertiary}</p>
                            </div>
                        </div>
                        <div className={style.StatCard}>
                            <div className={style.StatIcon} style={{ background: 'var(--cor-info)' }}>
                                <HiOutlineUsers />
                            </div>
                            <div className={style.StatInfo}>
                                <h3>{activeTab === 'alunos' ? filteredData.filter(a=>a.genero==='F').length : '---'}</h3>
                                <p>{activeTab === 'alunos' ? 'Alunas Femininas' : 'Visão Geral'}</p>
                            </div>
                        </div>
                    </div>

                    {/* Tabs Estilizadas */}
                    <div className={style.TabsContainer}>
                        {tabs.map(tab => (
                            <button
                                key={tab.id}
                                className={`${style.TabButton} ${activeTab === tab.id ? style.ActiveTab : ''}`}
                                onClick={() => setActiveTab(tab.id)}
                            >
                                {tab.icon} {tab.label}
                            </button>
                        ))}
                    </div>

                    {/* Secção de Filtros */}
                    <div className={style.FiltersSection}>
                        <div className={style.FilterGroup} style={{ flex: 1 }}>
                            <label><HiOutlineSearch /> Pesquisa Rápida</label>
                            <input 
                                type="text" 
                                placeholder="Filtrar instantaneamente na tabela..." 
                                value={searchTerm} 
                                onChange={(e) => setSearchTerm(e.target.value)} 
                            />
                        </div>

                        {activeTab === 'mensal' && (
                            <div className={style.FilterGroup}>
                                <label>Período de Referência</label>
                                <div style={{display: 'flex', gap: '8px'}}>
                                    <select value={filters.mes} onChange={(e) => setFilters({...filters, mes: e.target.value})}>
                                        <option value="1">Janeiro</option><option value="2">Fevereiro</option>
                                        <option value="3">Março</option><option value="4">Abril</option>
                                        <option value="5">Maio</option><option value="6">Junho</option>
                                        <option value="7">Julho</option><option value="8">Agosto</option>
                                        <option value="9">Setembro</option><option value="10">Outubro</option>
                                        <option value="11">Novembro</option><option value="12">Dezembro</option>
                                    </select>
                                    <input type="number" value={filters.ano} onChange={(e) => setFilters({...filters, ano: e.target.value})} style={{width: '90px'}} />
                                </div>
                            </div>
                        )}

                        {activeTab === 'alunos' && (
                            <>
                                <div className={style.FilterGroup}>
                                    <label>Filtrar Classe</label>
                                    <select value={filters.classe} onChange={(e) => setFilters({...filters, classe: e.target.value})}>
                                        <option value="">Todas</option>
                                        {metadata.classes.map(c => <option key={c.id_classe} value={c.id_classe}>{c.nivel}ª Classe</option>)}
                                    </select>
                                </div>
                                <div className={style.FilterGroup}>
                                    <label>Turma</label>
                                    <select value={filters.turma} onChange={(e) => setFilters({...filters, turma: e.target.value})}>
                                        <option value="">Todas</option>
                                        {metadata.turmas.map(t => <option key={t.id_turma} value={t.id_turma}>{t.codigo_turma}</option>)}
                                    </select>
                                </div>
                            </>
                        )}

                        <div className={style.ButtonsGap}>
                            <button className={style.BtnLight} onClick={handleGeneratePDF}>
                                <FaFilePdf /> Gerar Relatório PDF
                            </button>
                        </div>
                    </div>

                    {/* Previsualização em Folha A4 */}
                    <div className={style.PreviewSection}>
                        {loading ? (
                            <div className={style.SkeletonLoader}>
                                <div className={style.StatIcon} style={{ background: '#eee', color: '#999' }}><HiOutlineDatabase /></div>
                                <p>A sincronizar base de dados...</p>
                            </div>
                        ) : (
                            <div className={style.PaperWrapper}>
                                <div className={style.Paper}>
                                    <div className={style.InsigniaHeader}>
                                        <img src={insignia} className={style.InsigniaImg} alt="Angola" />
                                        <p style={{ fontWeight: 800, margin: 0 }}>INSTITUTO POLITÉCNICO MAIOMBE</p>
                                        <p style={{ fontSize: '9pt', color: '#666' }}>Sistema de Gestão Escolar - Central de Relatórios</p>
                                    </div>

                                    <div className={style.ReportTitle}>
                                        Relatório de {tabs.find(t => t.id === activeTab).label}
                                    </div>

                                    <table className={style.PreviewTable}>
                                        <thead>
                                            <tr>
                                                {activeTab === 'solicitacoes' && <><th>Ref / Aluno</th><th>Documento</th><th>Data</th><th>Estado</th><th>Valor</th></>}
                                                {activeTab === 'mensal' && <><th>Tipo Documento</th><th>Qtd</th><th>Total (AKZ)</th></>}
                                                {activeTab === 'alunos' && <><th>Nome Completo</th><th>BI</th><th>Turma</th></>}
                                                {activeTab === 'funcionarios' && <><th>Nome Completo</th><th>Cargo</th><th>Telefone</th></>}
                                                {activeTab === 'auditoria' && <><th>Acção</th><th>Usuário</th><th>Data / Hora</th></>}
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {filteredData.slice(0, 12).map((item, i) => (
                                                <tr key={i}>
                                                    {activeTab === 'solicitacoes' && (
                                                        <>
                                                            <td><div className={style.BoldText}>{item.aluno_nome}</div><span style={{fontSize: '8pt', color: '#999'}}>{item.rupe || `#${item.id_solicitacao}`}</span></td>
                                                            <td>{item.tipo_documento}</td>
                                                            <td>{item.data_solicitacao ? new Date(item.data_solicitacao).toLocaleDateString() : '---'}</td>
                                                            <td><span className={style.Badge}>{item.status_solicitacao}</span></td>
                                                            <td className={style.BoldText}>{(item.valor_rupe || 0).toLocaleString()} Kz</td>
                                                        </>
                                                    )}
                                                    {activeTab === 'mensal' && (
                                                        <>
                                                            <td>{item.tipo}</td>
                                                            <td>{item.quantidade}</td>
                                                            <td className={style.BoldText}>{(item.total || 0).toLocaleString()} Kz</td>
                                                        </>
                                                    )}
                                                    {activeTab === 'alunos' && (
                                                        <>
                                                        {
                                                            console.log(item)
                                                            
                                                        }
                                                            <td className={style.BoldText}>{item.nome_completo}</td>
                                                            <td>{item.numero_bi}</td>
                                                            <td>{item.turma_codigo || '-'}</td>
                                                        </>
                                                    )}
                                                    {activeTab === 'funcionarios' && (
                                                        <>
                                                        
                                                            <td className={style.BoldText}>{item.nome_completo}</td>
                                                            <td>{item.cargo_nome || '-'}</td>
                                                            <td>{item.telefone}</td>
                                                        </>
                                                    )}
                                                    {activeTab === 'auditoria' && (
                                                        <>
                                                            <td>{item.tipo_accao}</td>
                                                            <td>{item.usuario_nome}</td>
                                                            <td>{item.data_hora ? new Date(item.data_hora).toLocaleString() : '---'}</td>
                                                        </>
                                                    )}
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                    
                                    {filteredData.length > 12 && (
                                        <p style={{textAlign: 'center', marginTop: '20px', color: '#999', fontSize: '9pt'}}>
                                            ... exibindo 12 de {filteredData.length} registos. A exportação PDF conterá o relatório completo.
                                        </p>
                                    )}
                                    {filteredData.length === 0 && <div className={style.EmptyState}>Nenhum registo encontrado para os filtros seleccionados.</div>}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </main>
        </div>
    );
};

export default Reports;
