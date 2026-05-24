import React, { useEffect, useState } from 'react';
import style from './ChildrenActions.module.css';

// padrão para todas as paginas
import '../../../../assets/style/global.style.css'
import MenuNavBarCliente from '../../../../Components/Elements/MenuNavBarCliente/MenuNavBarCliente'
import Header from '../../../../Components/Elements/Header/Header'
import { useNavigate } from 'react-router-dom';
import api from '../../../../Services/api';
import Loading from '../../../../Components/Elements/Loading/Loading';
import { RiSearchLine, RiFilter3Line, RiCalendarLine, RiEyeLine, RiDownload2Line, RiHistoryLine, RiFileTextLine, RiUser3Line, RiArrowLeftLine } from 'react-icons/ri';

const ChildrenActions = () => {
  const navigate = useNavigate();
  const [child, setChild] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDoc, setSelectedDoc] = useState(null);

  // Filtros
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState('all');

  const MEDIA_BASE = import.meta.env.VITE_API_BASE_URL 
    ? import.meta.env.VITE_API_BASE_URL.replace(/\/api\/v1\/?$/, '/media')
    : 'http://localhost:8000/media';

  const normalizeUrl = (url) => {
    if (!url) return null;
    if (typeof url !== 'string') return url.url || null;
    if (url.startsWith('http')) return url;
    const cleanPath = url.replace(/^\/media\//, '').replace(/^media\//, '');
    return `${MEDIA_BASE}/${cleanPath.replace(/^\//, '')}`;
  };

  useEffect(() => {
    const studentData = localStorage.getItem('selectedStudent');
    if (studentData) {
      const parsedStudent = JSON.parse(studentData);
      setChild(parsedStudent);
      fetchUnifiedHistory(parsedStudent.id_aluno);
    } else {
      navigate('/parent/children');
    }
  }, [navigate]);

  const fetchUnifiedHistory = async (studentId) => {
    try {
      setLoading(true);
      // Reutiliza a lógica de "minhas solicitações" do painel do aluno, filtrando por id_aluno
      const response = await api.get(`/solicitacoes/minhas/?id_aluno=${studentId}`);
      
      const combined = (response.data.results || response.data).map(item => ({
        ...item,
        id_unico: `sol-${item.id_solicitacao}`,
        category: item.status_solicitacao === 'disponivel' || item.status_solicitacao === 'impresso' ? 'documento' : 'solicitacao',
        display_date: item.data_solicitacao,
        arquivo: item.caminho_arquivo || item.caminho_pdf
      })).sort((a, b) => new Date(b.display_date) - new Date(a.display_date));

      setHistory(combined);
    } catch (error) {
      console.error("Erro ao buscar histórico unificado:", error);
    } finally {
      setLoading(false);
    }
  };

  const filteredHistory = history.filter(item => {
    const matchesSearch = item.tipo_documento.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (item.rupe && item.rupe.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesStatus = statusFilter === 'all' || item.status_solicitacao === statusFilter;
    const matchesType = typeFilter === 'all' || item.category === typeFilter;
    
    return matchesSearch && matchesStatus && matchesType;
  });

  const handleDownload = (item) => {
    const url = normalizeUrl(item.arquivo);
    if (!url) return;
    window.open(url, '_blank');
  };

  const getStatusClass = (status) => {
    const s = status?.toLowerCase();
    if (['aprovado', 'pago', 'concluido', 'disponivel', 'impresso'].includes(s)) return style.statusReady;
    if (['pendente', 'aguardando_assinatura'].includes(s)) return style.statusPending;
    if (s === 'rejeitado') return style.statusRejected;
    return style.statusPending;
  };

  const getStatusLabel = (status) => {
    const labels = {
      'pendente': 'Pendente (RUP)',
      'pago': 'Pago / Em Processamento',
      'aguardando_assinatura': 'Aguardando Assinatura',
      'disponivel': 'Disponível',
      'impresso': 'Impresso',
      'concluido': 'Finalizado',
      'rejeitado': 'Rejeitado'
    };
    return labels[status?.toLowerCase()] || status;
  };

  if (!child) return null;

  return (
    <div className='containelGeralclient'>
      <MenuNavBarCliente user={'parent'} />
      <main className='containelMainclient'>
        <Header text1="Perfil do Educando" text2="Histórico e Ações" />

        <div className={style.detailsContainer}>
          <div className={style.backNav}>
            <button onClick={() => navigate('/parent/children')} className={style.backBtn}>
              <RiArrowLeftLine /> Voltar para lista
            </button>
          </div>

          <div className={style.childHeader}>
            <div className={style.avatarLarge}>
              {child.img_path ? (
                <img src={normalizeUrl(child.img_path)} alt={child.nome_completo} className={style.avatarImg} />
              ) : (
                <RiUser3Line />
              )}
            </div>
            <div className={style.headerInfo}>
              <h1>{child.nome_completo}</h1>
              <p>{child.classe_nivel}ª Classe - Turma {child.turma_codigo} | Matrícula nº {child.numero_matricula}</p>
            </div>
          </div>

          <div className={style.historySection}>
            <div className={style.sectionHeader}>
                <h2><RiHistoryLine /> Histórico de Solicitações e Documentos</h2>
                <p>Veja abaixo todos os pedidos efetuados para este educando.</p>
            </div>

            {/* Filtros */}
            <div className={style.filtersBar}>
               <div className={style.searchField}>
                  <RiSearchLine />
                  <input 
                    type="text" 
                    placeholder="Pesquisar por tipo ou RUP..." 
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
               </div>
               
               <div className={style.selectsGroup}>
                  <div className={style.filterItem}>
                    <RiFilter3Line />
                    <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
                        <option value="all">Todos os Estados</option>
                        <option value="pendente">Pendente</option>
                        <option value="pago">Pago</option>
                        <option value="disponivel">Disponível</option>
                        <option value="concluido">Finalizado</option>
                        <option value="rejeitado">Rejeitado</option>
                    </select>
                  </div>

                  <div className={style.filterItem}>
                    <RiFileTextLine />
                    <select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}>
                        <option value="all">Ver Tudo</option>
                        <option value="solicitacao">Apenas Pedidos</option>
                        <option value="documento">Documentos Finais</option>
                    </select>
                  </div>
               </div>
            </div>

            <div className={style.tableContainer}>
              {loading ? (
                <p><Loading/></p>
              ) : filteredHistory.length > 0 ? (
                <table className={style.historyTable}>
                  <thead>
                    <tr>
                      <th>Tipo / Referência</th>
                      <th>Data</th>
                      <th>Estado</th>
                      <th>Ações</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredHistory.map((item) => (
                      <tr key={item.id_unico}>
                        <td>
                            <div className={style.docInfo}>
                                <strong>{item.tipo_documento}</strong>
                                {item.rupe && <small>RUP: {item.rupe}</small>}
                                {item.category === 'documento' && <span className={style.categoryBadge}>Oficial</span>}
                            </div>
                        </td>
                        <td>
                            <div className={style.dateInfo}>
                                <RiCalendarLine />
                                {new Date(item.display_date).toLocaleDateString('pt-BR')}
                            </div>
                        </td>
                        <td>
                          <span className={`${style.statusBadge} ${getStatusClass(item.status_solicitacao)}`}>
                            {getStatusLabel(item.status_solicitacao)}
                          </span>
                        </td>
                        <td>
                          <div className={style.actionsGroup}>
                            {item.arquivo && (
                                <>
                                    <button 
                                        className={style.viewBtnIcon} 
                                        onClick={() => setSelectedDoc(item)}
                                        title="Visualizar"
                                    >
                                        <RiEyeLine />
                                    </button>
                                    <button  
                                        className={style.downloadBtnIcon} 
                                        onClick={() => handleDownload(item)}
                                        title="Baixar"
                                    >
                                        <RiDownload2Line />
                                    </button>
                                </>
                            )}
                            {!item.arquivo && (
                                <span className={style.noAction}>Aguardando...</span>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <p className={style.emptyMsg}>
                    {searchTerm || statusFilter !== 'all' || typeFilter !== 'all' 
                      ? "Nenhum resultado corresponde aos filtros aplicados." 
                      : "Nenhuma solicitação encontrada para este educando."}
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Modal de Visualização de PDF */}
        {selectedDoc && (
          <div className={style.modalOverlay} onClick={() => setSelectedDoc(null)}>
            <div className={style.modalContent} onClick={e => e.stopPropagation()}>
              <div className={style.modalHeader}>
                <h3><RiEyeLine /> {selectedDoc.tipo_documento}</h3>
                <button onClick={() => setSelectedDoc(null)} className={style.closeBtn}>×</button>
              </div>
              <div className={style.modalBody}>
                <iframe
                  src={`${normalizeUrl(selectedDoc.arquivo)}#toolbar=1&navpanes=0&scrollbar=1`}
                  title="Visualizador de PDF"
                  className={style.pdfViewer}
                ></iframe>
              </div>
              <div className={style.modalFooter}>
                <button onClick={() => handleDownload(selectedDoc)} className={style.downloadBtn}>
                  <RiDownload2Line /> Baixar Documento
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default ChildrenActions;
