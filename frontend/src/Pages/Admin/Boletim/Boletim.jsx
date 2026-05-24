import { useState, useEffect } from 'react'
import style from './Boletim.module.css'
import NavBarMenu from '../../../Components/Elements/NavBarMenu/NavBarMenu'
import Header from '../../../Components/Elements/Header/Header'
import '../../../assets/style/global.style.css'
import { FaFileAlt, FaPencilAlt, FaEye, FaDownload, FaCopy, FaTrash } from 'react-icons/fa'
import api from '../../../Services/api'
import Loading from '../../../Components/Elements/Loading/Loading'
import DocumentPreviewModal from '../../../Components/Elements/DocumentPreviewModal/DocumentPreviewModal'
import Pagination from '../../../Components/Elements/Pagination/Pagination'

// Sample templates data (Keeping static for now as there is no backend model)
const templatesData = [
    { id: 1, name: "Modelo Padrão 2024", description: "Modelo oficial do boletim escolar", lastModified: "2024-01-10", isActive: false },
    { id: 2, name: "Modelo Simplificado", description: "Versão reduzida para impressão", lastModified: "2023-12-15", isActive: false },
    { id: 3, name: "Modelo Detalhado", description: "Com notas e observações completas", lastModified: "2023-11-20", isActive: false },
]

export default function Boletim() {
    const [activeTab, setActiveTab] = useState('modelos')
    const [searchTerm, setSearchTerm] = useState('')
    const [documents, setDocuments] = useState([])
    const [loading, setLoading] = useState(true)
    const [previewModal, setPreviewModal] = useState({ isOpen: false, url: '', title: '' })
    const [currentPage, setCurrentPage] = useState(1)
    const ITEMS_PER_PAGE = 8

    useEffect(() => {
        const fetchDocuments = async () => {
            try {
                const response = await api.get('documentos/?tipo_documento=BOLETIM')
                setDocuments(response.data.results || response.data)
            } catch (error) {
                console.error("Erro ao carregar boletins:", error)
            } finally {
                setLoading(false)
            }
        }
        fetchDocuments()
    }, [])

    const filteredDocuments = documents.filter(doc =>
        doc.aluno_nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (doc.classe && doc.classe.toLowerCase().includes(searchTerm.toLowerCase()))
    )

    const totalPages = Math.ceil(filteredDocuments.length / ITEMS_PER_PAGE)
    const paginatedDocuments = filteredDocuments.slice(
        (currentPage - 1) * ITEMS_PER_PAGE,
        currentPage * ITEMS_PER_PAGE
    )

    useEffect(() => { setCurrentPage(1) }, [searchTerm])

    const filteredTemplates = templatesData.filter(template =>
        template.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        template.description.toLowerCase().includes(searchTerm.toLowerCase())
    )

    const tabs = [
        { id: 'modelos', label: 'Modelos de Boletim', icon: <FaFileAlt /> },
        { id: 'documentos', label: 'Boletins Gerados', icon: <FaFileAlt /> }
    ]

    const handleCreateModel = () => {
        console.log('Criar novo modelo de boletim')
    }

    const handleEditModel = (model) => {
        console.log('Editar modelo:', model)
    }

    const handleActivateModel = (model) => {
        console.log('Ativar modelo:', model)
    }

    const handleDuplicateModel = (model) => {
        console.log('Duplicar modelo:', model)
    }

    const handleDeleteModel = (model) => {
        console.log('Eliminar modelo:', model)
    }

    const handleViewDocument = (doc) => {
        if (doc.caminho_pdf) {
            setPreviewModal({
                isOpen: true,
                url: doc.caminho_pdf,
                title: `Boletim - ${doc.aluno_nome}`
            })
        }
    }

    const handleDownloadDocument = (doc) => {
        if (doc.caminho_pdf) {
            const link = document.createElement('a')
            link.href = doc.caminho_pdf
            link.download = `boletim_${doc.aluno_nome}_${doc.uuid_documento}.pdf`
            document.body.appendChild(link)
            link.click()
            document.body.removeChild(link)
        }
    }

    return (
        <div className="ContainerGeneral">
            <NavBarMenu />
            <main className="ContainerMain">
                <Header text1={"Documentos"} text2={"Boletim"} onSearch={setSearchTerm} />

                <div className={style.BoletimContainer}>
                    {/* Tabs Navigation */}
                    <div className={style.TabsContainer}>
                        {tabs.map(tab => (
                            <button
                                key={tab.id}
                                className={`${style.TabButton} ${activeTab === tab.id ? style.TabActive : ''}`}
                                onClick={() => setActiveTab(tab.id)}
                            >
                                <span className={style.TabIcon}>{tab.icon}</span>
                                <span>{tab.label}</span>
                            </button>
                        ))}
                    </div>

                    {/* Content */}
                    <div className={style.ContentCard}>
                        {activeTab === 'modelos' ? (
                            <>
                                {/* Models Header */}
                                <div className={style.CardHeader}>
                                    <div className={style.HeaderLeft}>
                                        <h3>Modelos de Boletim</h3>
                                        <p className={style.Subtitle}>Gerir e personalizar modelos de boletim escolar</p>
                                    </div>
                                    <button className={style.CreateButton} onClick={handleCreateModel}  style={{cursor:"not-allowed"}} disabled>
                                        + Criar Novo Modelo
                                    </button>
                                </div>

                                {/* Models Grid */}
                                <div className={`${style.ModelsGrid} ${style.ContainerDisabled}`}>
                                    {filteredTemplates.map(model => (
                                        <div key={model.id} className={style.ModelCard}>
                                            {model.isActive && (
                                                <span className={style.ActiveBadge}>✓ Ativo</span>
                                            )}
                                            <div className={style.ModelIcon}>
                                                <FaFileAlt />
                                            </div>
                                            <h4>{model.name}</h4>
                                            <p>{model.description}</p>
                                            <div className={style.ModelMeta}>
                                                <span>Modificado: {model.lastModified}</span>
                                            </div>
                                            <div className={style.ModelActions}>
                                                <button
                                                    className={style.BtnEdit}
                                                    onClick={() => handleEditModel(model)}
                                                    title="Editar Modelo"
                                                >
                                                    <FaPencilAlt /> Editar
                                                </button>
                                                {!model.isActive && (
                                                    <button
                                                        className={style.BtnActivate}
                                                        onClick={() => handleActivateModel(model)}
                                                        title="Ativar Modelo"
                                                    >
                                                        Ativar
                                                    </button>
                                                )}
                                                <button
                                                    className={style.BtnDuplicate}
                                                    onClick={() => handleDuplicateModel(model)}
                                                    title="Duplicar Modelo"
                                                >
                                                    <FaCopy />
                                                </button>
                                                <button
                                                    className={style.BtnDelete}
                                                    onClick={() => handleDeleteModel(model)}
                                                    title="Eliminar"
                                                >
                                                    <FaTrash />
                                                </button>
                                            </div>
                                        </div>
                                    ))}
                                    {filteredTemplates.length === 0 && (
                                        <p className={style.EmptyState}>Nenhum modelo encontrado para "{searchTerm}"</p>
                                    )}
                                </div>
                            </>
                        ) : (
                            <>
                                {/* Documents Header */}
                                <div className={style.CardHeader}>
                                    <div className={style.HeaderLeft}>
                                        <h3>Boletins Gerados</h3>
                                        <p className={style.Subtitle}>Visualizar e gerir boletins escolares emitidos</p>
                                    </div>
                                </div>

                                {/* Documents Table */}
                                <div className={style.TableWrapper}>
                                    {loading ? (
                                        <div className="flex items-center justify-center p-10">
                                            <Loading />
                                        </div>
                                    ) : (
                                        <>
                                        <table className={style.Table}>
                                            <thead>
                                                <tr>
                                                    <th>Estudante</th>
                                                    <th>Classe</th>
                                                    <th>Curso</th>
                                                    <th>Data de Emissão</th>
                                                    <th>Status</th>
                                                    <th>Ações</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {paginatedDocuments.map(doc => (
                                                    <tr key={doc.id_documento}>
                                                        <td>
                                                            <div className={style.StudentCell}>
                                                                <div className={style.Avatar}>
                                                                    {doc.aluno_img ? (
                                                                        <img src={doc.aluno_img} alt={doc.aluno_nome} />
                                                                    ) : (
                                                                        doc.aluno_nome?.split(' ').map(n => n[0]).join('')
                                                                    )}
                                                                </div>
                                                                <span>{doc.aluno_nome}</span>
                                                            </div>
                                                        </td>
                                                        <td>{doc.classe || 'N/A'}</td>
                                                        <td>{doc.curso || 'N/A'}</td>
                                                        <td>{new Date(doc.data_emissao).toLocaleDateString()}</td>
                                                        <td>
                                                            <span className={`${style.StatusBadge} ${style.StatusFinished}`}>
                                                                Finalizado
                                                            </span>
                                                        </td>
                                                        <td>
                                                            <div className={style.ActionButtons}>
                                                                <button
                                                                    className={style.ViewBtn}
                                                                    onClick={() => handleViewDocument(doc)}
                                                                    title="Visualizar"
                                                                >
                                                                    <FaEye />
                                                                </button>
                                                                <button
                                                                    className={style.DownloadBtn}
                                                                    onClick={() => handleDownloadDocument(doc)}
                                                                    title="Download"
                                                                >
                                                                    <FaDownload />
                                                                </button>
                                                            </div>
                                                        </td>
                                                    </tr>
                                                ))}
                                                {filteredDocuments.length === 0 && (
                                                    <tr>
                                                        <td colSpan="6" className={style.EmptyState}>
                                                            Nenhum boletim encontrado para "{searchTerm}"
                                                        </td>
                                                    </tr>
                                                )}
                                            </tbody>
                                        </table>
                                        <Pagination currentPage={currentPage} totalPages={totalPages} onPageChange={setCurrentPage} />
                                        </>
                                    )}
                                </div>
                            </>
                        )}
                    </div>
                </div>
            </main>
            <DocumentPreviewModal
                isOpen={previewModal.isOpen}
                onClose={() => setPreviewModal(prev => ({ ...prev, isOpen: false }))}
                pdfUrl={previewModal.url}
                title={previewModal.title}
            />
        </div>
    )
}
