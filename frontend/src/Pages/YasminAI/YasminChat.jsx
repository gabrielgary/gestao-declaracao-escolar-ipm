import { useState, useRef, useEffect, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import style from './YasminChat.module.css';
import '../../assets/style/global.style.css';
import MenuNavBarCliente from '../../Components/Elements/MenuNavBarCliente/MenuNavBarCliente';
import NavBarMenu from '../../Components/Elements/NavBarMenu/NavBarMenu';
import Header from '../../Components/Elements/Header/Header';
import {
    RiSendPlane2Fill,
    RiUser3Line,
    RiDeleteBin6Line,
    RiFileListLine,
    RiFilePdf2Line,
    RiDatabase2Line,
    RiBarChart2Line,
    RiUserAddLine,
    RiMoneyDollarCircleLine,
    RiFileTextLine,
    RiMedalLine,
    RiBankCardLine,

    RiParentLine,
    RiCalendarCheckLine,
} from 'react-icons/ri';
import { FaAtom } from 'react-icons/fa6';
import { useAuth } from '../../Context/AuthContext';
import yasminService from '../../Services/yasminService';

// Cards de sugestão por perfil
const SUGGESTIONS_ADMIN = [
    { icon: RiFileListLine,           label: 'Resumo das Solicitações',  sublabel: 'Ver estado actual',      prompt: 'Dá-me um resumo das solicitações de documentos.' },
    { icon: RiFilePdf2Line,           label: 'Documentos Gerados',       sublabel: 'PDFs emitidos',           prompt: 'Quantos documentos foram gerados até agora e de que tipo?' },
    { icon: RiDatabase2Line,          label: 'Gerar Backup',             sublabel: 'Segurança dos dados',     prompt: 'Gera um backup do sistema.' },
    { icon: RiBarChart2Line,          label: 'Estatísticas Gerais',      sublabel: 'Alunos e receita',        prompt: 'Mostra-me as estatísticas gerais do sistema.' },
    { icon: RiUserAddLine,            label: 'Como registar um aluno?',  sublabel: 'Guia passo a passo',      prompt: 'Como faço para registar um novo aluno no sistema?' },
    { icon: RiMoneyDollarCircleLine,  label: 'Confirmar pagamento',      sublabel: 'Fluxo de documentos',     prompt: 'Como confirmo o pagamento de uma solicitação de documento?' },
];

const SUGGESTIONS_STUDENT = [
    { icon: RiMedalLine,         label: 'As Minhas Notas',      sublabel: 'Ver aproveitamento escolar',   prompt: 'Como consulto as minhas notas no sistema?' },
    { icon: RiCalendarCheckLine, label: 'As Minhas Faltas',     sublabel: 'Assiduidade e presenças',      prompt: 'Como vejo as minhas faltas e presenças no sistema?' },
];

const SUGGESTIONS_PARENT = [
    { icon: RiParentLine,            label: 'Resumo dos Meus Filhos',      sublabel: 'Visão geral dos educandos',    prompt: 'Dá-me um resumo da situação escolar dos meus educandos.' },
    { icon: RiBankCardLine,          label: 'Propinas Pagas',              sublabel: 'Pagamentos confirmados',       prompt: 'Quais as propinas que já foram pagas pelo meu educando?' },
    { icon: RiMoneyDollarCircleLine, label: 'Propinas Por Pagar',          sublabel: 'Pagamentos em falta',          prompt: 'Quais as propinas que ainda estão por pagar pelo meu educando?' },
];

export default function YasminChat() {
    const { user, loading } = useAuth();
    const [input, setInput] = useState('');
    const [messages, setMessages] = useState([]);
    const [isTyping, setIsTyping] = useState(false);
    const [yasminStatus, setYasminStatus] = useState('checking'); // 'online' | 'offline' | 'checking'
    const messagesEndRef = useRef(null);
    const textareaRef = useRef(null);

    const [isStaff, setIsStaff] = useState(false);
    const [menuType, setMenuType] = useState('student');

    useEffect(() => {
        if (!loading) {
            const type = user?.tipo_usuario?.toLowerCase() || localStorage.getItem('user_type')?.toLowerCase();
            if (type === 'funcionario' || type === 'admin' || type === 'professor' || type === 'secretaria') {
                setIsStaff(true);
            } else {
                setIsStaff(false);
                setMenuType(type === 'encarregado' ? 'parent' : 'student');
            }
        }
    }, [user, loading]);

    // Verificar status da Yasmin ao carregar
    useEffect(() => {
        const checkStatus = async () => {
            const result = await yasminService.checkStatus();
            setYasminStatus(result.status === 'offline' ? 'offline' : 'online');
        };
        checkStatus();
    }, []);

    const scrollToBottom = useCallback(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, []);

    useEffect(() => {
        scrollToBottom();
    }, [messages, scrollToBottom]);

    // Auto-resize do textarea
    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 150)}px`;
        }
    }, [input]);

    const handleSend = async (customInput = null) => {
        const textToSend = customInput || input;
        if (!textToSend.trim() || isTyping) return;

        const userMsg = { role: 'user', content: textToSend };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsTyping(true);

        try {
            const role = isStaff ? 'admin' : (menuType === 'parent' ? 'parent' : 'student');
            const userToken = localStorage.getItem('access_token');
            const response = await yasminService.sendMessage(textToSend, role, user?.id, userToken);

            const aiMsg = {
                role: 'ai',
                content: response.response || 'Desculpe, tive um problema ao processar a sua solicitação.'
            };
            setMessages(prev => [...prev, aiMsg]);
        } catch (error) {
            console.error('Erro na Yasmin:', error);
            setMessages(prev => [...prev, {
                role: 'ai',
                content: 'Olá! No momento estou com dificuldades de conexão. Por favor, verifica se o servidor da Yasmin está activo na porta 8001.'
            }]);
        } finally {
            setIsTyping(false);
        }
    };

    const handleClearHistory = async () => {
        try {
            await yasminService.clearHistory(user?.id);
            setMessages([]);
        } catch {
            setMessages([]);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const getSuggestions = () => {
        if (isStaff) return SUGGESTIONS_ADMIN;
        if (menuType === 'parent') return SUGGESTIONS_PARENT;
        return SUGGESTIONS_STUDENT;
    };

    const generalContainerClass = isStaff ? 'ContainerGeneral' : 'containelGeralclient';
    const mainContainerClass = isStaff ? 'ContainerMain' : 'containelMainclient';

    if (loading) return null;

    return (
        <div className={generalContainerClass}>
            {isStaff ? <NavBarMenu /> : <MenuNavBarCliente user={menuType} />}

            <main className={mainContainerClass}>
                <Header text1="Inteligência Artificial" text2="Yasmin" />

                <div className={style.yasminContainer}>
                    <div className={style.chatWrapper}>

                        {/* Barra de estado + botão limpar */}
                        <div className={style.chatTopBar}>
                            <div className={`${style.statusBadge} ${style[yasminStatus]}`}>
                                <span className={style.statusDot}></span>
                                {yasminStatus === 'online' ? 'Yasmin Online' : yasminStatus === 'offline' ? 'Yasmin Offline' : 'A verificar...'}
                            </div>
                            {messages.length > 0 && (
                                <button className={style.clearBtn} onClick={handleClearHistory} title="Limpar conversa">
                                    <RiDeleteBin6Line size={16} />
                                    <span>Limpar</span>
                                </button>
                            )}
                        </div>

                        <div className={style.messagesContainer}>
                            {messages.length === 0 ? (
                                <div className={style.emptyState}>
                                    <div className={style.logoLarge}>
                                        <FaAtom size={64} />
                                    </div>
                                    <div className={style.greeting}>
                                        <h2>Olá, {user?.nome?.split(' ')[0] || 'Utilizador'}</h2>
                                        <h2 className={style.textGradient}>Como posso ajudar hoje?</h2>
                                    </div>
                                    <div className={style.suggestionScroll}>
                                        {getSuggestions().map((s, i) => {
                                            const Icon = s.icon;
                                            return (
                                                <div
                                                    key={i}
                                                    className={style.suggestionCard}
                                                    onClick={() => handleSend(s.prompt)}
                                                >
                                                    <div className={style.cardIcon}><Icon size={22} /></div>
                                                    <span>{s.label}</span>
                                                    <small>{s.sublabel}</small>
                                                </div>
                                            );
                                        })}
                                    </div>
                                </div>
                            ) : (
                                <div className={style.boxmessage}>
                                    <div className={style.boxmessagemini}>
                                        {messages.map((msg, index) => (
                                            <div key={index} className={`${style.messageRow} ${style[msg.role]}`}>
                                                <div className={`${style.msgAvatar} ${style[msg.role]}`}>
                                                    {msg.role === 'ai' ? <FaAtom size={20} /> : <RiUser3Line size={20} />}
                                                </div>
                                                <div className={style.bubble}>
                                                    {msg.role === 'ai' ? (
                                                        <div className={style.markdownContent}>
                                                            <ReactMarkdown>{typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content)}</ReactMarkdown>
                                                        </div>
                                                    ) : (
                                                        typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content)
                                                    )}
                                                </div>
                                            </div>
                                        ))}
                                        {isTyping && (
                                            <div className={`${style.messageRow} ${style.ai}`}>
                                                <div className={`${style.msgAvatar} ${style.ai}`}>
                                                    <FaAtom size={20} className={style.rotating} />
                                                </div>
                                                <div className={style.bubble}>
                                                    <div className={style.typingIndicator}>
                                                        <span></span><span></span><span></span>
                                                    </div>
                                                </div>
                                            </div>
                                        )}
                                        <div ref={messagesEndRef} />
                                    </div>
                                </div>
                            )}
                        </div>

                        <div className={style.inputContainer}>
                            <div className={style.inputWrapper}>
                                <textarea
                                    ref={textareaRef}
                                    className={style.textInput}
                                    placeholder="Envie uma mensagem para a Yasmin... (Enter para enviar, Shift+Enter para nova linha)"
                                    rows={1}
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyDown={handleKeyDown}
                                />
                                <button
                                    className={`${style.actionBtn} ${input.trim() ? style.sendBtn : ''}`}
                                    onClick={() => handleSend()}
                                    disabled={!input.trim() || isTyping}
                                    style={{ cursor: !input.trim() || isTyping ? 'not-allowed' : 'pointer' }}
                                >
                                    <RiSendPlane2Fill size={20} />
                                </button>
                            </div>
                            <p className={style.disclaimer}>
                                A Yasmin pode cometer erros. Verifique sempre informações importantes com a secretaria.
                            </p>
                        </div>

                    </div>
                </div>
            </main>
        </div>
    );
}
