import React, { useEffect, useState } from 'react';
import style from './Documentos.module.css';

// padrão para todas as paginas
import '../../../../assets/style/global.style.css'
import MenuNavBarCliente from '../../../../Components/Elements/MenuNavBarCliente/MenuNavBarCliente'
import Header from '../../../../Components/Elements/Header/Header'
import { RiFileList3Line, RiDownloadLine, RiEyeLine, RiSearchLine, RiFilter3Line } from 'react-icons/ri';
import { useAuth } from '../../../../Context/AuthContext';
import api from '../../../../Services/api';
import Loading from '../../../../Components/Elements/Loading/Loading';

const Documentos = () => {
  const { user } = useAuth();
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDocs = async () => {
      try {
        if (user?.id) {
          const response = await api.get(`/documentos/para_encarregado/?id_encarregado=${user.id}`);
          // Garantir que carregamos os resultados paginados se existirem
          setDocuments(response.data.results || response.data);
        }
      } catch (error) {
        console.error("Erro ao carregar documentos:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchDocs();
  }, [user]);

  const [selectedDoc, setSelectedDoc] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

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

  const handleDownload = (doc) => {
    const url = normalizeUrl(doc.caminho_pdf || doc.caminho_arquivo);
    if (url) {
      window.open(url, '_blank');
    } else {
      alert("Arquivo não disponível.");
    }
  };

  const filteredDocs = documents.filter(doc => 
    doc.tipo_documento?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    doc.aluno_nome?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className='containelGeralclient'>
      <MenuNavBarCliente user={'parent'} />
      <main className='containelMainclient'>
        <Header text1="Documentos" text2="Repositório Oficial" />

        <div className={style.container}>
          <header className={style.header}>
            <h1>Gestão de Documentos</h1>
            <p>Aceda e faça o download de documentos oficiais, boletins de notas e certificados de todos os seus educandos.</p>
          </header>

          <div className={style.filtersBar}>
            <div className={style.searchField}>
              <RiSearchLine />
              <input 
                type="text" 
                placeholder="Pesquisar por aluno ou documento..." 
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>

          <div className={style.tableContainer}>
            {loading ? (
              <p><Loading/></p>
            ) : filteredDocs.length > 0 ? (
              <table className={style.table}>
                <thead>
                  <tr>
                    <th>Educando</th>
                    <th>Documento</th>
                    <th>Emissão</th>
                    <th>Estado</th>
                    <th>Operações</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredDocs.map((doc) => (
                    <tr key={doc.id_documento}>
                      <td><strong>{doc.aluno_nome || 'Aluno'}</strong></td>
                      <td>
                        <div className={style.docType}>
                          <RiFileList3Line />
                          <span>{doc.tipo_documento}</span>
                        </div>
                      </td>
                      <td>{new Date(doc.data_emissao).toLocaleDateString('pt-BR')}</td>
                      <td>
                        <span className={`${style.statusBadge} ${style.statusReady}`}>
                          <span className={style.dot} />
                          Disponível
                        </span>
                      </td>
                      <td>
                        <div className={style.actionsGroup}>
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
                            <RiDownloadLine />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className={style.emptyMsg}>Nenhum documento encontrado.</p>
            )}
          </div>
        </div>

        {/* Modal de Visualização de PDF */}
        {selectedDoc && (
          <div className={style.modalOverlay} onClick={() => setSelectedDoc(null)}>
            <div className={style.modalContent} onClick={e => e.stopPropagation()}>
              <div className={style.modalHeader}>
                <h3><RiEyeLine /> {selectedDoc.tipo_documento} ({selectedDoc.aluno_nome})</h3>
                <button onClick={() => setSelectedDoc(null)} className={style.closeBtn}>×</button>
              </div>
              <div className={style.modalBody}>
                <iframe
                  src={`${normalizeUrl(selectedDoc.caminho_pdf || selectedDoc.caminho_arquivo)}#toolbar=1&navpanes=0&scrollbar=1`}
                  title="Visualizador de PDF"
                  className={style.pdfViewer}
                ></iframe>
              </div>
              <div className={style.modalFooter}>
                <button onClick={() => handleDownload(selectedDoc)} className={style.downloadBtn}>
                  <RiDownloadLine /> Baixar Documento
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default Documentos;

