import { useState, useEffect } from 'react'
import style from './Settings.module.css'
import NavBarMenu from '../../../Components/Elements/NavBarMenu/NavBarMenu'
import Header from '../../../Components/Elements/Header/Header'
import '../../../assets/style/global.style.css'
import api from '../../../Services/api'
import {
    FaBuilding,
    FaDatabase,
    FaCloudArrowDown,
    FaClockRotateLeft,
    FaTrash,
    FaPalette,
    FaPenNib,
    FaStamp
} from 'react-icons/fa6'

export default function Settings() {
    const [activeTab, setActiveTab] = useState('general')
    const [isBackingUp, setIsBackingUp] = useState(false)
    const [backupProgress, setBackupProgress] = useState(0)
    const [backups, setBackups] = useState([])
    const [config, setConfig] = useState(null)
   const [loading, setLoading] = useState(false)
    const [currentColor, setCurrentColor] = useState(localStorage.getItem('primary-color') || '#0ea5e9')

    const palettes = [
        { id: 'sky', color: '#0ea5e9', hover: '#0284c7', name: 'Azul Celeste' },
        { id: 'indigo', color: '#6366f1', hover: '#4f46e5', name: 'Índigo Real' },
        { id: 'emerald', color: '#10b981', hover: '#059669', name: 'Verde Esmeralda' },
        { id: 'amber', color: '#f59e0b', hover: '#d97706', name: 'Âmbar Escolar' },
        { id: 'rose', color: '#ef4444', hover: '#e11d48', name: 'Vermelho Paixão' },
        { id: 'slate', color: '#334155', hover: '#1e293b', name: 'Slate Profissional' },
    ]

    useEffect(() => {
        fetchConfig()
        fetchBackups()
        
        const savedColor = localStorage.getItem('primary-color')
        if (savedColor) {
            applyColor(savedColor)
        }
    }, [])

    const applyColor = (color) => {
        const selectedPalette = palettes.find(p => p.color === color) || palettes[0]
        const hoverColor = selectedPalette.hover
        
        const targets = [document.documentElement, document.body]
        targets.forEach(el => {
            el.style.setProperty('--cor-primaria', color)
            el.style.setProperty('--cor-primaria-hover', hoverColor)
            el.style.setProperty('--cor-primaria-clara', `${color}20`)
            
            // Legacy Support (Mapeamento)
            el.style.setProperty('--primary', color) 
            el.style.setProperty('--primary-dark', hoverColor)
            el.style.setProperty('--primary-light', `${color}20`)
            el.style.setProperty('--primary-soft', `${color}15`)
            el.style.setProperty('--accent-indigo', color)
            el.style.setProperty('--text-primary', color)
        })
    }

    const handleColorChange = (color) => {
        setCurrentColor(color)
        localStorage.setItem('primary-color', color)
        applyColor(color)
    }

    const fetchConfig = async () => {
        try {
            const response = await api.get('configuracao-sistema/')
            const data = response.data.results || response.data
            if (data && data.length > 0) {
                setConfig(data[0])
            }
        } catch (error) {
            console.error("Erro ao carregar configurações:", error)
        }
    }

    const fetchBackups = async () => {
        try {
            const response = await api.get('backups/')
            setBackups(response.data)
        } catch (error) {
            console.error("Erro ao carregar backups:", error)
        }
    }

    const handleFileUpload = async (e, field) => {
        const file = e.target.files[0]
        if (!file) return

        const formData = new FormData()
        formData.append(field, file)

        setLoading(true)
        try {
            const configId = config?.id
            if (configId) {
                const response = await api.patch(`configuracao-sistema/${configId}/`, formData, {
                    headers: { 'Content-Type': 'multipart/form-data' }
                })
                setConfig(response.data)
                alert(`${field.charAt(0).toUpperCase() + field.slice(1)} atualizado com sucesso!`)
            }
        } catch (error) {
            console.error(`Erro ao carregar ${field}:`, error)
        } finally {
            setLoading(false)
        }
    }
/* Desabilidado pois o secretario nao pode mudar dados da escolar */
    /*const handleSaveConfig = async () => {
        setLoading(true)
        try {
            const configId = config?.id
            if (configId) {
                await api.patch(`configuracao-sistema/${configId}/`, config)
            } else {
                const response = await api.post('configuracao-sistema/', config)
                setConfig(response.data)
            }
            alert('Configurações salvas com sucesso!')
        } catch (error) {
            console.error("Erro ao salvar configurações:", error)
            alert('Erro ao guardar as configurações.')
        } finally {
            setLoading(false)
        }
    }*/

    const handleRunBackup = async () => {
        setIsBackingUp(true)
        setBackupProgress(30)
        try {
            await api.post('backups/run_backup/')
            setBackupProgress(100)
            setTimeout(() => {
                setIsBackingUp(false)
                fetchBackups()
            }, 1000)
        } catch (error) {
            console.error("Erro ao realizar backup:", error)
            setIsBackingUp(false)
            alert('Erro ao realizar backup.')
        }
    }

    const handleDeleteBackup = async (filename) => {
        if (!window.confirm('Tem certeza que deseja eliminar este backup?')) return
        try {
            await api.delete(`backups/delete_backup/?filename=${filename}`)
            fetchBackups()
        } catch (error) {
            console.error("Erro ao eliminar backup:", error)
        }
    }

    const handleRestoreBackup = async (filename) => {
        if (!window.confirm(`Tem certeza que deseja restaurar o sistema usando o backup "${filename}"?`)) return
        setIsBackingUp(true)
        setBackupProgress(50)
        try {
            await api.post('backups/restore_backup/', { filename })
            setBackupProgress(100)
            alert('Sistema restaurado com sucesso!')
        } catch (error) {
            console.error("Erro ao restaurar backup:", error)
        } finally {
            setIsBackingUp(false)
        }
    }

    const tabs = [
        { id: 'general', label: 'Instituição', icon: <FaBuilding /> },
        { id: 'appearance', label: 'Temas', icon: <FaPalette /> },
        { id: 'backup', label: 'Base de Dados', icon: <FaDatabase /> },
    ]

    return (
        <div className="ContainerGeneral">
            <NavBarMenu />
            <main className="ContainerMain">
                <Header text1={"Configurações"} text2={"Gestão Administrativa"} />

                <div className={style.SettingsContainer}>
                    <div className={style.SideNav}>
                        {tabs.map(tab => (
                            <button
                                key={tab.id}
                                className={`${style.NavButton} ${activeTab === tab.id ? style.NavActive : ''}`}
                                onClick={() => setActiveTab(tab.id)}
                            >
                                <span className={style.NavIcon}>{tab.icon}</span>
                                <span>{tab.label}</span>
                            </button>
                        ))}
                    </div>

                    <div className={style.ContentArea}>
                        {activeTab === 'general' && (
                            <div className={style.SettingSection}>
                                <div className={style.SectionHeader}>
                                    <h3>Dados da Instituição</h3>
                                    <p>Estes dados serão usados nos cabeçalhos e rodapés de todos os relatórios.</p>
                                </div>
                                
                                <div className={style.FilesGrid}>
                                    <div className={style.FileUploadCard}>
                                        <div className={style.FilePreview}>
                                            {config?.logo ? <img src={config.logo} alt="Logo" /> : <FaBuilding />}
                                        </div>
                                        <div className={style.FileInfo}>
                                            <h4>Logótipo Institucional</h4>
                                            <input type="file" id="logo-up" hidden onChange={(e) => handleFileUpload(e, 'logo')} />
                                          {/*  <label htmlFor="logo-up" className={style.UploadBtnSmall}>Alterar</label>*/}
                                        </div>
                                    </div>

                                    <div className={style.FileUploadCard}>
                                        <div className={style.FilePreview}>
                                            {config?.assinatura_director ? <img src={config.assinatura_director} alt="Assinatura" /> : <FaPenNib />}
                                        </div>
                                        <div className={style.FileInfo}>
                                            <h4>Assinatura do Diretor</h4>
                                            <input type="file" id="sign-up" hidden onChange={(e) => handleFileUpload(e, 'assinatura_director')} />
                                        {/*    <label htmlFor="sign-up" className={style.UploadBtnSmall}>Alterar</label>*/}
                                        </div>
                                    </div>
                                    <div className={style.FileUploadCard}>
                                        <div className={style.FilePreview}>
                                            {config?.assinatura_director_pedagogico ? <img src={config.assinatura_director_pedagogico} alt="Assinatura" /> : <FaPenNib />}
                                        </div>
                                        <div className={style.FileInfo}>
                                            <h4>Assinatura do Diretor Pedagogico</h4>
                                            <input type="file" id="sign-up" hidden onChange={(e) => handleFileUpload(e, 'assinatura_director')} />
                                        {/*    <label htmlFor="sign-up" className={style.UploadBtnSmall}>Alterar</label>*/}
                                        </div>
                                    </div>

                                    <div className={style.FileUploadCard}>
                                        <div className={style.FilePreview}>
                                            {config?.carimbo_instituicao ? <img src={config.carimbo_instituicao} alt="Carimbo" /> : <FaStamp />}
                                        </div>
                                        <div className={style.FileInfo}>
                                            <h4>Carimbo Oficial</h4>
                                            <input type="file" id="stamp-up" hidden onChange={(e) => handleFileUpload(e, 'carimbo_instituicao')} />
                                            {/*<label htmlFor="stamp-up" className={style.UploadBtnSmall}>Alterar</label>*/}
                                        </div>
                                    </div>
                                </div>

                                <div className={style.FormGrid}>
                                    <div className={style.InputGroup}>
                                        <label>Nome do Colégio / Escola</label>
                                        <input readOnly
                                            type="text"
                                            value={config?.nome_instituicao || ''}
                                            onChange={(e) => setConfig({ ...config, nome_instituicao: e.target.value })}
                                        />
                                    </div>
                                    <div className={style.InputGroup}>
                                        <label>Director Geral (Instituição)</label>
                                        <input readOnly
                                            type="text"
                                            placeholder="Nome completo do Diretor"
                                            value={config?.director_geral || ''}
                                            onChange={(e) => setConfig({ ...config, director_geral: e.target.value })}
                                        />
                                    </div>
                                    <div className={style.InputGroup}>
                                        <label>NIF / Identificação Fiscal</label>
                                        <input readOnly
                                            type="text"
                                            value={config?.nif || ''}
                                            onChange={(e) => setConfig({ ...config, nif: e.target.value })}
                                        />
                                    </div>
                                    <div className={style.InputGroupFull}>
                                        <label>Endereço Completo</label>
                                        <input readOnly
                                            type="text"
                                            value={config?.endereco || ''}
                                            onChange={(e) => setConfig({ ...config, endereco: e.target.value })}
                                        />
                                    </div>
                                    <div className={style.InputGroup}>
                                        <label>Telefone</label>
                                        <input
                                        readOnly
                                            type="text"
                                            value={config?.telefone || ''}
                                            onChange={(e) => setConfig({ ...config, telefone: e.target.value })}
                                        />
                                    </div>
                                    <div className={style.InputGroup}>
                                        <label>Email Oficial</label>
                                        <input
                                        readOnly
                                            type="email"
                                            value={config?.email_oficial || ''}
                                            onChange={(e) => setConfig({ ...config, email_oficial: e.target.value })}
                                        />
                                    </div>
                                </div>
                                {/* btn desabilitado pois os secretarios nao podem mudar dados da escolar */}
                                {/*
                                <button className={style.SaveButton} onClick={handleSaveConfig} disabled={loading}>
                                    {loading ? 'Processando...' : 'Salvar Alterações'}
                                </button>*/}
                            </div>
                        )}

                        {activeTab === 'appearance' && (
                            <div className={style.SettingSection}>
                                <div className={style.SectionHeader}>
                                    <h3>Personalização de Cores</h3>
                                    <p>Escolha a cor de destaque que define a identidade visual do sistema.</p>
                                </div>

                                <div className={style.ColorsModernGrid}>
                                    {palettes.map(p => (
                                        <div 
                                            key={p.id}
                                            className={`${style.ColorLargeSquare} ${currentColor === p.color ? style.ActiveColor : ''}`} 
                                            style={{ '--preview-color': p.color }}
                                            onClick={() => handleColorChange(p.color)}
                                        >
                                            <div className={style.ColorBox} style={{ backgroundColor: p.color }}></div>
                                            <span>{p.name}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {activeTab === 'backup' && (
                            <div className={style.SettingSection}>
                                <div className={style.SectionHeader}>
                                    <h3>Segurança de Dados</h3>
                                    <p>Realize backups periódicos para garantir que nenhum dado seja perdido.</p>
                                </div>

                                <div className={style.BackupActionCard}>
                                    <FaCloudArrowDown className={style.BackupIcon} />
                                    <div className={style.BackupCallToAction}>
                                        <h4>Cópia de Segurança Completa</h4>
                                        <p>Gera um ficheiro .SQL com todas as turmas, alunos e histórico do sistema.</p>
                                        <button className={style.PrimaryBtn} onClick={handleRunBackup} disabled={isBackingUp}>
                                            {isBackingUp ? `Gerando Backup... ${backupProgress}%` : 'Executar Agora'}
                                        </button>
                                    </div>
                                </div>

                                <div className={style.BackupTableContainer}>
                                    <h4>Backups Disponíveis</h4>
                                    {backups.map((bkp, i) => (
                                        <div key={i} className={style.BackupListItem}>
                                            <FaClockRotateLeft />
                                            <div className={style.BkpInfo}>
                                                <p>{bkp.filename}</p>
                                                <span>{(bkp.size / 1024 / 1024).toFixed(2)} MB • {new Date(bkp.created_at).toLocaleDateString()}</span>
                                            </div>
                                            <div className={style.BkpActions}>
                                                <button onClick={() => handleRestoreBackup(bkp.filename)}style={{
                                                    color:'var(--primary)'
                                                }}>Restaurar</button>
                                                <button onClick={() => window.open(bkp.url, '_blank')} className={style.DownloadBtn}>Baixar</button>
                                                <button onClick={() => handleDeleteBackup(bkp.filename)} className={style.DeleteBtn }><FaTrash /></button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </main>
        </div>
    )
}
