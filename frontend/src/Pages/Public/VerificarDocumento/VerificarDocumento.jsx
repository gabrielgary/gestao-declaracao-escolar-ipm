import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import api from '../../../Services/api'
import style from './VerificarDocumento.module.css'
import { FaCheckCircle, FaExclamationTriangle, FaTimesCircle, FaFileAlt, FaUniversity, FaCalendarAlt, FaUserGraduate, FaUpload, FaShieldAlt } from 'react-icons/fa'
import Loading from '../../../Components/Elements/Loading/Loading'
import MenuSitePublic from '../../../Components/Utils/MenuSitePublic/MenuSitePublic'
import insignia from '../../../assets/images/insigna_angola.png'

export default function VerificarDocumento() {
    const navigate = useNavigate()
    const { uuid } = useParams()
    const [status, setStatus] = useState(uuid ? 'loading' : 'idle') // idle, loading, valid, invalid, error
    const [docData, setDocData] = useState(null)
    const [error, setError] = useState('')
    const [inputUuid, setInputUuid] = useState('')
    const [uploadError, setUploadError] = useState('')
    const [isDragging, setIsDragging] = useState(false)

    const handleSearch = (e) => {
        e.preventDefault()
        if (inputUuid.trim()) {
            navigate(`/public/verificar/${inputUuid.trim()}`)
        }
    }

    const processFile = (file) => {
        setUploadError('')
        if (!file || file.type !== 'application/pdf') {
            setUploadError('Por favor, envie um ficheiro PDF estruturado válido.')
            return
        }

        setStatus('loading')
        
        const uuidRegex = /[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/i
        const match = file.name.match(uuidRegex)
        
        if (match) {
            navigate(`/public/verificar/${match[0]}`)
            return
        }

        const reader = new FileReader()
        reader.onload = (event) => {
            const content = event.target.result
            const contentMatch = content.match(uuidRegex)
            if (contentMatch) {
                navigate(`/public/verificar/${contentMatch[0]}`)
            } else {
                setStatus('idle')
                setUploadError('Não foi possível ler o código autêntico desta folha automaticamente. Insira o código impresso na folha manualmente na caixa acima.')
            }
        }
        reader.onerror = () => {
            setStatus('idle')
            setUploadError('Erro ao ler a estrutura do ficheiro.')
        }
        reader.readAsText(file)
    }

    const handleFileUpload = (e) => {
        processFile(e.target.files[0])
    }

    const handleDragOver = (e) => {
        e.preventDefault()
        setIsDragging(true)
    }

    const handleDragLeave = (e) => {
        e.preventDefault()
        setIsDragging(false)
    }

    const handleDrop = (e) => {
        e.preventDefault()
        setIsDragging(false)
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            processFile(e.dataTransfer.files[0])
        }
    }

    useEffect(() => {
        const verificarDoc = async () => {
            try {
                // Usando a instância centralizada 'api'
                // Nota: A baseURL já termina em /api/v1/
                const response = await api.get(`documentos/verificar/${uuid}/`)
                setDocData(response.data)
                setStatus('valid')
            } catch (err) {
                if (err.response && err.response.status === 404) {
                    setStatus('invalid')
                } else {
                    setStatus('error')
                    setError('Erro ao conectar com o servidor. Tente novamente mais tarde.')
                }
            }
        }

        if (uuid) {
            verificarDoc()
        }
    }, [uuid])

    return (
        <div className={style.VerificationPage}>
                 <MenuSitePublic />
            <div className={style.Overlay}></div>
            <div className={style.ContentWrapper}>
                <div className={style.Card}>
                    <div className={style.Header}>
                        <div className={style.Logo}>
                            <img src={insignia} alt="Insignia" />
                            <h2>Instituto Politécnico do Maiombe</h2>
                        </div>
                        <h1>Autenticação de Documento</h1>
                    </div>

                    <div className={style.StatusArea}>
                        {uploadError && (
                            <div className={style.CustomAlertCard}>
                                <FaExclamationTriangle className={style.AlertIconBase} />
                                <div className={style.AlertContent}>
                                    <h4>Atenção</h4>
                                    <p>{uploadError}</p>
                                </div>
                                <button className={style.CloseAlertBtn} onClick={() => setUploadError('')}>
                                    <FaTimesCircle />
                                </button>
                            </div>
                        )}

                        {status === 'idle' && (
                            <div className={style.InputBox}>
                                <h3>Tem um documento em mãos?</h3>
                                <p>Insira o código digital alfanumérico (UUID) ou escaneie o QR Code.</p>
                                <form onSubmit={handleSearch} className={style.SearchForm}>
                                    <input 
                                        type="text" 
                                        value={inputUuid} 
                                        onChange={(e) => setInputUuid(e.target.value)} 
                                        placeholder="Ex: 123e4567-e89b-12d3..."
                                        required 
                                        className={style.UUIDInput}
                                    />
                                    <button type="submit" className={style.SearchBtn}>Autenticar Manualmente</button>
                                </form>

                                <div 
                                    className={`${style.UploadBox} ${isDragging ? style.Dragging : ''}`}
                                    onDragOver={handleDragOver}
                                    onDragLeave={handleDragLeave}
                                    onDrop={handleDrop}
                                >
                                    <div className={style.UploadIconWrapper}>
                                        <FaUpload className={style.UploadIconBig} />
                                    </div>
                                    <p className={style.UploadTitle}>Arraste e solte o documento PDF aqui</p>
                                    <span className={style.UploadDivider}>ou</span>
                                    <label className={style.UploadBtnLabel}>
                                        Selecionar Ficheiro
                                        <input 
                                            type="file" 
                                            accept=".pdf" 
                                            onChange={handleFileUpload} 
                                            className={style.FileInput} 
                                        />
                                    </label>
                                </div>
                            </div>
                        )}

                        {status === 'loading' && (
                            <div className={style.LoadingBox}>
                                <div className={style.ShieldScanner}>
                                    <FaShieldAlt className={style.ShieldIcon} />
                                    <div className={style.ScanLine}></div>
                                </div>
                                <p>A monitorizar a assinatura digital do documento...</p>
                            </div>
                        )}

                        {status === 'valid' && docData && (
                            <div className={`${style.ResultBox} ${style.Valid}`}>
                                <div className={style.StatusBadge}>
                                    <FaCheckCircle />
                                    <span>Documento Autêntico</span>
                                </div>
                                
                                <div className={style.DetailsGrid}>
                                    <div className={style.DetailItem}>
                                        <FaFileAlt className={style.Icon} />
                                        <div className={style.Info}>
                                            <label>Tipo de Documento</label>
                                            <p>{docData.tipo_documento}</p>
                                        </div>
                                    </div>
                                    <div className={style.DetailItem}>
                                        <FaUserGraduate className={style.Icon} />
                                        <div className={style.Info}>
                                            <label>Titular (Ofuscado)</label>
                                            <p>{docData.aluno_nome_ofuscado}</p>
                                        </div>
                                    </div>
                                    <div className={style.DetailItem}>
                                        <FaCheckCircle className={style.Icon} />
                                        <div className={style.Info}>
                                            <label>Nº BI (Ofuscado)</label>
                                            <p>{docData.bi_aluno_ofuscado}</p>
                                        </div>
                                    </div>
                                    <div className={style.DetailItem}>
                                        <FaCalendarAlt className={style.Icon} />
                                        <div className={style.Info}>
                                            <label>Data de Emissão</label>
                                            <p>{new Date(docData.data_emissao).toLocaleDateString()} às {new Date(docData.data_emissao).toLocaleTimeString()}</p>
                                        </div>
                                    </div>
                                </div>

                                <div className={style.SecurityCodeBox}>
                                    <label>CÓDIGO DE SEGURANÇA VISUAL</label>
                                    <div className={style.Code}>{docData.codigo_seguranca}</div>
                                    <span>Confirme se este código é idêntico ao impresso no papel.</span>
                                </div>

                                <div className={style.SecurityNote}>
                                    <p>Este documento foi emitido pelo sistema de gestão escolar IP Maiombe e a sua integridade é garantida pela nossa plataforma digital.</p>
                                </div>

                                <div className={style.DocPreviewBox}>
                                    <h4 className={style.PreviewTitle}>Visualização do Documento</h4>
                                    <div className={style.IframeContainer}>
                                        <iframe 
                                            src={docData.download_url} 
                                            title="Documento Validado"
                                            className={style.DocIframe}
                                        ></iframe>
                                    </div>
                                    <a href={docData.download_url} target="_blank" rel="noopener noreferrer" className={style.DownloadBtn}>
                                        <FaFileAlt /> Abrir em Nova Separador
                                    </a>
                                </div>
                            </div>
                        )}

                        {status === 'invalid' && (
                            <div className={`${style.ResultBox} ${style.Invalid}`}>
                                <div className={style.StatusBadge}>
                                    <FaTimesCircle />
                                    <span>Documento Inválido</span>
                                </div>
                                <p className={style.WarningText}>
                                    O código de verificação <strong>{uuid}</strong> não foi encontrado na nossa base de dados.
                                </p>
                                <div className={style.Alert}>
                                    <FaExclamationTriangle />
                                    <p>Atenção: Este documento pode ser uma falsificação. Por favor, contacte a secretaria para confirmar.</p>
                                </div>
                            </div>
                        )}

                        {status === 'error' && (
                            <div className={`${style.ResultBox} ${style.Error}`}>
                                <FaExclamationTriangle className={style.ErrorIcon} />
                                <p>{error}</p>
                                <button onClick={() => window.location.reload()} className={style.RetryBtn}>Tentar Novamente</button>
                            </div>
                        )}
                    </div>

                    <div className={style.Footer}>
                        <p>© 2026 Instituto Politécnico do Maiombe. Todos os direitos reservados.</p>
                        <div className={style.Links}>
                            <Link to="/">Voltar ao Site</Link>
                            <span>|</span>
                            <a href="tel:+2449XXXXXXXX">Suporte Técnico</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
