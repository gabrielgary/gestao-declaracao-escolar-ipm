import { useState, useEffect, useRef } from 'react'
import {
    RiSearchLine,
    RiNotification3Line,
    RiSunLine,
    RiMoonLine,
    RiMenu4Line,
    RiCloseLine,
    RiCheckLine,
    RiErrorWarningLine,
    RiUserLine,
    RiSettings4Line,
    RiLogoutBoxRLine,
    RiPaletteLine
} from "react-icons/ri";


import style from './Header.module.css'
import { useAuth } from '../../../Context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import api from '../../../Services/api';

export default function Header({ text1, text2, onSearch }) {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const [showNotifications, setShowNotifications] = useState(false)
    const [showProfileDropdown, setShowProfileDropdown] = useState(false)
    const [notifications, setNotifications] = useState([])
    const [unreadCount, setUnreadCount] = useState(0)
    const [loadingNotifs, setLoadingNotifs] = useState(false)
    const notificationRef = useRef(null)
    const profileRef = useRef(null)
    const paletteRef = useRef(null)
    const [showPalette, setShowPalette] = useState(false)
    const [currentColor, setCurrentColor] = useState(localStorage.getItem('primary-color') || '#0ea5e9')

    const palettes = [
        { id: 'sky', color: '#0ea5e9', hover: '#0284c7', name: 'Azul Celeste' },
        { id: 'indigo', color: '#6366f1', hover: '#4f46e5', name: 'Índigo Real' },
        { id: 'emerald', color: '#10b981', hover: '#059669', name: 'Verde Esmeralda' },
        { id: 'amber', color: '#f59e0b', hover: '#d97706', name: 'Âmbar Escolar' },
        { id: 'rose', color: '#ef4444', hover: '#e11d48', name: 'Vermelho Paixão' },
        { id: 'slate', color: '#334155', hover: '#1e293b', name: 'Slate' },
    ]

    useEffect(() => {
        const savedColor = localStorage.getItem('primary-color')
        if (savedColor) applyColor(savedColor)
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
        setShowPalette(false)
    }


    // Load Notifications from API
    const fetchNotifications = async () => {
        try {
            setLoadingNotifs(true)
            const response = await api.get('notificacoes/')
            setNotifications(response.data.results || response.data)
            setUnreadCount((response.data.results || response.data).filter(n => !n.lida).length)
        } catch (error) {
            // Se for erro de autenticação (401), não precisamos inundar o console
            // O interceptor já deve tentar o refresh, se falhar aqui é porque a sessão caiu.
            if (error.response?.status === 401) {
                console.warn("Sessão expirada ao buscar notificações.")
            } else if (error.code === 'ERR_NETWORK') {
                console.error("Backend offline. Certifique-se que o Django (python manage.py runserver) está rodando.")
            } else {
                console.error("Erro ao buscar notificações:", error)
            }
        } finally {
            setLoadingNotifs(false)
        }
    }

    useEffect(() => {
        if (user) {
            fetchNotifications()
            // Polling opcional a cada 1 minuto
            const interval = setInterval(() => {
                // Verificar se o servidor está respondendo antes de tentar
                fetchNotifications()
            }, 60000)
            return () => clearInterval(interval)
        }
    }, [user])

    const markAsRead = async (id) => {
        try {
            await api.post(`notificacoes/${id}/marcar_lida/`)
            setNotifications(prev => prev.map(n => n.id_notificacao === id ? { ...n, lida: true } : n))
            setUnreadCount(prev => Math.max(0, prev - 1))
        } catch (error) {
            console.error("Erro ao marcar como lida:", error)
        }
    }

    const markAllAsRead = async () => {
        try {
            await api.post('notificacoes/marcar_todas_lidas/')
            setNotifications(prev => prev.map(n => ({ ...n, lida: true })))
            setUnreadCount(0)
        } catch (error) {
            console.error("Erro ao marcar todas como lidas:", error)
        }
    }



    // Click outside to close tabs
    useEffect(() => {
        function handleClickOutside(event) {
            if (notificationRef.current && !notificationRef.current.contains(event.target)) {
                setShowNotifications(false)
            }
            if (profileRef.current && !profileRef.current.contains(event.target)) {
                setShowProfileDropdown(false)
            }
            if (paletteRef.current && !paletteRef.current.contains(event.target)) {
                setShowPalette(false)
            }
        }

        document.addEventListener("mousedown", handleClickOutside)
        return () => document.removeEventListener("mousedown", handleClickOutside)
    }, [])

    const [isSidebarOpen, setIsSidebarOpen] = useState(false)

    // Sync body class with sidebar state
    useEffect(() => {
        if (isSidebarOpen) {
            document.body.classList.add('sidebar-open')
        } else {
            document.body.classList.remove('sidebar-open')
        }
        return () => {
            document.body.classList.remove('sidebar-open')
        }
    }, [isSidebarOpen])



    const handleLogout = async () => {
        await logout();
        navigate('/');
    };

    const userRoleDisplay = {
        'funcionario': 'Funcionário',
        'aluno': 'Aluno',
        'encarregado': 'Encarregado'
    };

    const getInitials = (name) => {
        const finalName = name || user?.nome_completo;
        if (!finalName) return '??';
        const parts = finalName.trim().split(' ');
        if (parts.length >= 2) {
            return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
        }
        return name.substring(0, 2).toUpperCase();
    };

    return (
        <header className={style.Header}>
            <div className={style.HeaderLeftMobile}>
                <button
                    className={style.MenuToggle}
                    onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                >
                    {isSidebarOpen ? <RiCloseLine /> : <RiMenu4Line />}
                </button>
                <div className={style.Breadcrumbs}>
                    {text1} / <span>{text2}</span>
                </div>
            </div>

            <div className={style.HeaderActions}>
                <div className={style.SearchBar}>
                    <RiSearchLine />
                    <input
                        type="text"
                        placeholder="Pesquisar..."
                        onChange={(e) => onSearch && onSearch(e.target.value)}
                    />
                </div>
                <div className={style.ActionIcons}>
                    <div className={style.NotificationWrapper} ref={paletteRef}>
                        <button
                            className={`${style.IconButton} ${showPalette ? style.Active : ''}`}
                            onClick={() => setShowPalette(!showPalette)}
                            title="Mudar Cor do Sistema"
                        >
                            <RiPaletteLine />
                        </button>
                        {showPalette && (
                            <div className={style.NotificationDropdown} style={{ width: '250px', right: 0 }}>
                                <div className={style.DropdownHeader}>
                                    <h3>Tema de Cores</h3>
                                </div>
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', padding: '15px' }}>
                                    {palettes.map(p => (
                                        <div 
                                            key={p.id}
                                            onClick={() => handleColorChange(p.color)}
                                            style={{
                                                display: 'flex', flexDirection: 'column', alignItems: 'center', cursor: 'pointer',
                                                border: currentColor === p.color ? `2px solid ${p.color}` : '2px solid transparent',
                                                borderRadius: '8px', padding: '8px 4px', transition: 'all 0.2s ease',
                                                background: currentColor === p.color ? `${p.color}10` : 'transparent'
                                            }}
                                        >
                                            <div style={{ width: '25px', height: '25px', borderRadius: '50%', backgroundColor: p.color, marginBottom: '6px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}></div>
                                            <span style={{ fontSize: '0.75rem', textAlign: 'center', fontWeight: currentColor === p.color ? '600' : '400' }}>{p.name}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>

                    <div className={style.NotificationWrapper} ref={notificationRef}>
                        <button
                            className={`${style.IconButton} ${showNotifications ? style.Active : ''}`}
                            onClick={() => setShowNotifications(!showNotifications)}
                        >
                            <RiNotification3Line />
                            {unreadCount > 0 && <span className={style.Badge}>{unreadCount}</span>}
                        </button>

                        {showNotifications && (
                            <div className={style.NotificationDropdown}>
                                <div className={style.DropdownHeader}>
                                    <h3>Notificações</h3>
                                    <span onClick={markAllAsRead} style={{ cursor: 'pointer' }}>Marcar todas como lidas</span>
                                </div>
                                <div className={style.NotificationList}>
                                    {loadingNotifs ? (
                                        <div className={style.EmptyState}>Carregando...</div>
                                    ) : notifications.length > 0 ? (
                                        notifications.map(notif => (
                                            <div
                                                key={notif.id_notificacao}
                                                className={`${style.NotificationItem} ${notif.lida ? style.Read : ''}`}
                                                onClick={() => !notif.lida && markAsRead(notif.id_notificacao)}
                                            >
                                                <div className={`${style.NotifIcon} ${style[notif.tipo || 'info']}`}>
                                                    {notif.tipo === 'success' ? <RiCheckLine /> : <RiErrorWarningLine />}
                                                </div>
                                                <div className={style.NotifContent}>
                                                    <h4>{notif.titulo}</h4>
                                                    <p>{notif.mensagem}</p>
                                                    <span className={style.NotifTime}>
                                                        {new Date(notif.data_criacao).toLocaleString()}
                                                    </span>
                                                </div>
                                            </div>
                                        ))
                                    ) : (
                                        <div className={style.EmptyState}>Sem notificações</div>
                                    )}
                                </div>
                                <div className={style.DropdownFooter}>
                                    Ver todas as notificações
                                </div>
                            </div>
                        )}
                    </div>
                </div>
                <div className={style.ProfileWrapper} ref={profileRef}>
                    <div
                        className={`${style.UserProfileHeader} ${showProfileDropdown ? style.Active : ''}`}
                        onClick={() => setShowProfileDropdown(!showProfileDropdown)}
                    >
                        <div className={style.AvatarSmall}>
                            {user?.img_path ? (
                                <img src={user.img_path} alt="Avatar" className={style.AvatarImage} />
                            ) : (
                                getInitials(user?.nome)
                            )}
                        </div>
                        <div className={style.InfoSmall}>
                            <h4>{user?.nome || user?.nome_completo || 'Usuário'}</h4>
                            <span>{userRoleDisplay[user?.tipo] || 'Membro'}</span>
                        </div>
                    </div>

                    {showProfileDropdown && (
                        <div className={style.ProfileDropdown}>
                            <div className={style.ProfileHeader}>
                                <div className={style.AvatarLarge}>
                                    {user?.img_path ? (
                                        <img src={user.img_path} alt="Avatar" className={style.AvatarImageLarge} />
                                    ) : (
                                        getInitials(user?.nome)
                                    )}
                                </div>
                                <div className={style.ProfileInfo}>
                                    <h4>{user?.nome || user?.nome_completo || 'Usuário'}</h4>
                                    <span>{user?.email || 'email@exemplo.com'}</span>
                                </div>
                            </div>
                            <div className={style.ProfileMenu}>
                                <Link to="/profile" className={style.MenuItem} onClick={() => setShowProfileDropdown(false)}>
                                    <RiUserLine />
                                    <span>Meu Perfil</span>
                                </Link>
                                {/*
                                <button className={style.MenuItem}>
                                    <RiSettings4Line />
                                    <span>Configurações</span>
                                </button>*/}
                                <hr className={style.Divider} />
                                <button className={`${style.MenuItem} ${style.Logout}`} onClick={handleLogout}>
                                    <RiLogoutBoxRLine />
                                    <span>Sair da Conta</span>
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </header>
    )
}
