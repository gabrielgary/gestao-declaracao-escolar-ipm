import React, { useEffect, useState } from 'react';
import style from './DocumentsCliente.module.css';
import '../../../../assets/style/global.style.css'
import MenuNavBarCliente from '../../../../Components/Elements/MenuNavBarCliente/MenuNavBarCliente'
import Header from '../../../../Components/Elements/Header/Header'
import { RiFileList3Line, RiDownload2Line, RiEyeLine } from 'react-icons/ri';
import { useAuth } from '../../../../Context/AuthContext';
import api from '../../../../Services/api';
import { getMediaUrl } from '../../../../Utils/urlHelper';

const DocumentsCliente = () => {
  const { user } = useAuth();
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDoc, setSelectedDoc] = useState(null);


  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        // Filtra apenas solicitações com status que permitem download (pagas/processadas)
        const statusFilter = 'pago,disponivel,aguardando_assinatura,impresso';
        const response = await api.get(`/solicitacoes/minhas/?id_aluno=${user.id}&status_solicitacao__in=${statusFilter}`);
        setDocuments(response.data.results || response.data);
        setLoading(false);
        
      } catch (error) {
        console.error("Erro ao buscar documentos:", error);
        setLoading(false);
      }
    };
    if (user?.id) fetchDocuments();
  }, [user]);


  const handleDownload = (doc) => {
    const url = getMediaUrl(doc.caminho_arquivo || doc.caminho_pdf);
    if (!url) return;
    const link = document.createElement('a');
    link.href = url;
    link.download = `${doc.tipo_documento}_${doc.id_solicitacao}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'disponivel': return 'statusReady';
      case 'pendente': return 'statusPending';
      case 'rejeitado': return 'statusRejected';
      case 'pago': return 'statusProcessing';
      case 'aguardando_assinatura': return 'statusProcessing';
      case 'impresso': return 'statusProcessing';
      default: return 'statusPending';
    }
  };

  const handlePrintRUP = async (id) => {
    try {
      const response = await api.get(`/solicitacoes/${id}/imprimir_rup/`);
      if (response.data.download_url) {
        // Força o download do PDF em vez de abrir em nova aba
        const link = document.createElement('a');
        link.href = response.data.download_url;
        link.download = `RUP_Solicitacao_${id}.pdf`; // Nome do arquivo
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } else {
        alert("Erro ao obterURL do RUP.");
      }
    } catch (error) {
      console.error("Erro ao imprimir RUP", error);
      alert("Não foi possível gerar o RUP.");
    }
  };

  return (
    <div className='containelGeralclient'>
      <MenuNavBarCliente user={'student'} />
      <main className='containelMainclient'>
        <Header text1="Estudante" text2="Meus Documentos" />
        <div className={style.container}>
            <header className={style.header}>
                <div>
                  <h1>Meus Documentos</h1>
                  <p>Gerencie suas solicitações e baixe documentos oficiais.</p>
                </div>
                <div className={style.statsSummary}>
                    <div className={style.statItem}>
                        <span>Total de Pedidos</span>
                        <strong>{documents.length}</strong>
                    </div>
                </div>
              </header>

              <div className={style.tableContainer}>
                <table className={style.table}>
                  <thead>
                    <tr>
                      <th>Tipo de Documento</th>
                      <th>Data</th>
                      <th>Status</th>
                      <th>Expiração RUP</th>
                      <th>Ações</th>
                    </tr>
                  </thead>
                  <tbody>
                    {loading ? (
                      <tr><td colSpan="5" className="py-10 text-center text-muted">Carregando seus documentos...</td></tr>
                    ) : documents.length > 0 ? (
                      documents.map((doc) => (
                        <tr key={doc.id_solicitacao}>
                          <td>
                            <div className={style.docInfo}>
                              <div className={style.docIcon}>
                                <RiFileList3Line />
                              </div>
                              <div className={style.docText}>
                                <strong>{doc.tipo_documento}</strong>
                                <span>Ref: #{doc.id_solicitacao}</span>
                              </div>
                            </div>
                          </td>
                          <td>
                            <div className={style.dateInfo}>
                                {new Date(doc.data_solicitacao).toLocaleDateString('pt-AO')}
                                <span>{new Date(doc.data_solicitacao).toLocaleTimeString('pt-AO', { hour: '2-digit', minute: '2-digit' })}</span>
                            </div>
                          </td>
                          <td>
                            <span className={`${style.statusBadge} ${style[getStatusColor(doc.status_solicitacao)]}`}>
                              {doc.status_solicitacao.replace(/_/g, ' ')}
                            </span>
                          </td>
                          <td>
                            {doc.data_expiracao_rup ? (
                                <div className={style.rupInfo}>
                                    {new Date(doc.data_expiracao_rup).toLocaleDateString('pt-AO')}
                                    {new Date(doc.data_expiracao_rup) < new Date() && <span className={style.expired}>Expirado</span>}
                                </div>
                            ) : '-'}
                          </td>
                          <td>
                            <div className={style.actionsGroup}>
                              {['disponivel', 'aguardando_assinatura', 'impresso'].includes(doc.status_solicitacao) && (
                                <>
                                  <button 
                                    className={`${style.actionBtn} ${style.viewBtn}`} 
                                    title="Visualizar"
                                    onClick={() => setSelectedDoc(doc)}
                                  >
                                    <RiEyeLine />
                                  </button>
                                  <button 
                                    className={style.actionBtn} 
                                    title="Baixar" 
                                    onClick={() => handleDownload(doc)}
                                  >
                                    <RiDownload2Line />
                                  </button>
                                </>
                              )}
                              {doc.status_solicitacao === 'pendente' && (
                                <button
                                  className={style.payBtn}
                                  title="Baixar RUP"
                                  onClick={() => handlePrintRUP(doc.id_solicitacao)}
                                >
                                  <RiDownload2Line /> RUP
                                </button>
                              )}
                            </div>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr><td colSpan="5" className={style.emptyState}>Nenhuma solicitação encontrada.</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
        </div>
      </main>

      {/* Modal Visualizador (Igual Biblioteca) */}
      {selectedDoc && (
        <div className={style.modalOverlay} onClick={() => setSelectedDoc(null)}>
          <div className={style.modalContent} onClick={e => e.stopPropagation()}>
            <div className={style.modalHeader}>
              <div className={style.modalTitleInfo}>
                <RiFileList3Line />
                <h3>{selectedDoc.tipo_documento}</h3>
              </div>
              <button onClick={() => setSelectedDoc(null)} className={style.closeBtn}>×</button>
            </div>
            <div className={style.modalBody}>
              {selectedDoc.caminho_arquivo || selectedDoc.caminho_pdf ? (
                <iframe
                  src={`${getMediaUrl(selectedDoc.caminho_arquivo || selectedDoc.caminho_pdf)}#toolbar=1&navpanes=0&scrollbar=1`}
                  title="Visualizador de PDF"
                  className={style.pdfViewer}
                ></iframe>
              ) : (
                <div className={style.errorPlaceholder}>
                  Documento não disponível para visualização automática.
                </div>
              )}
            </div>
            <div className={style.modalFooter}>
              <button
                className={style.actionBtn}
                onClick={() => handleDownload(selectedDoc)}
              >
                <RiDownload2Line size={20} style={{ marginRight: '8px' }} /> Baixar Documento Oficial
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentsCliente;
