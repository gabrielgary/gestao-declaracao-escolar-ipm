import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom'
import favicon from '../../../assets/images/favicon.ico'
import style from './MenuNavBarCliente.module.css'
import BoxMessage from '../../Utils/BoxMessage/BoxMessage';
import { FaAtom } from 'react-icons/fa6';

import {
    RiHome4Line,
    RiBarChartLine,
    RiCalendarLine,
    RiUserSearchLine,
    RiFileTextLine,
    RiFolderLine,
    RiLogoutBoxLine,
    RiMenuFoldLine,
    RiMenuUnfoldLine,
    RiTeamLine,
    RiFileEditLine,
    RiDownload2Line,
    RiChat3Line,
    RiLayoutLeftLine
} from 'react-icons/ri';

export default function MenuNavBarCliente({ user }) {
    const [toggleMenuNavBar, settoggleMenuNavBar] = useState(true)
   // const [toggleBoxMessage, settoggleBoxMessage] = useState(false)
    const location = useLocation()

    const isActive = (path) => location.pathname === path ? style.active : ''

    const studentLinks = [
        { to: '/student/dashboard', icon: <RiHome4Line />, label: 'Dashboards' },
        { to: '/student/grades', icon: <RiBarChartLine />, label: 'Minhas Notas' },
        //{ to: '/student/schedule', icon: <RiCalendarLine />, label: 'Horários' },
        { to: '/student/attendance', icon: <RiUserSearchLine />, label: 'Presenças' },
        { to: '/student/ask', icon: <RiFileTextLine />, label: 'Solicitações' },
        { to: '/student/document', icon: <RiFolderLine />, label: 'Documentos' },
        { to: '/student/yasmin', icon: <FaAtom />, label: 'Yasmin' },
    ]

    const parentLinks = [
        { to: '/parent/dashboard', icon: <RiHome4Line />, label: 'Dashboard' },
        { to: '/parent/children', icon: <RiTeamLine />, label: 'Meus Educandos' },
        { to: '/parent/ask', icon: <RiFileEditLine />, label: 'Solicitações' },
        { to: '/parent/document', icon: <RiDownload2Line />, label: 'Documentos' },
        { to: '/parent/yasmin', icon: <FaAtom />, label: 'Yasmin AI' },
    ];

    const links = user === 'student' ? studentLinks : parentLinks

    return (
        <>
 {/*toggleBoxMessage && (
                <BoxMessage msm={"Tem Certeza Que Deseja Sair"} setController={settoggleBoxMessage} />
            )*/}

            <div className={`${style.containerMenu} ${toggleMenuNavBar ? style.extends : style.shinks}`}>
                <div className={style.header}>
                    <div className={style.favicon}>
                        <img src={favicon} alt="Logo" />
                        <span className={style.title_favicon}>IPM</span>
                    </div>
                    <div className={style.BtnToggleMenu}>
                        <button onClick={() => settoggleMenuNavBar(toggleMenuNavBar)}>
                            {/*<RiLayoutLeftLine size={25} />*/}
                        </button>
                    </div>
                </div>

                <div className={style.menu}>
                    <h4>{user === 'student' ? 'ESTUDANTE' : 'ENCARREGADO'}</h4>
                    <nav>
                        {links.map((link) => (
                            <Link key={link.to} to={link.to} className={isActive(link.to)}>
                                <span className={style.icon}>{link.icon}</span>
                                <span className={style.txt}>{link.label}</span>
                            </Link>
                        ))}
                    </nav>
                </div>
                {

                /*
                <div className={style.usercontroller}>
                    <div>
                        <img src={favicon} alt="Avatar" width={30} />
                    </div>
                    <div>
                        <strong>Gabriel Pedro Aurélio</strong>
                        <span>gabrielpedroaurelio@gmail</span>
                    </div>
                </div>
                
                <div className={style.menu}>
                    <nav>
                        <Link to={'#'} onClick={(e) => { e.preventDefault(); settoggleBoxMessage(true) }}>
                            <span className={style.icon}>
                                <RiLogoutBoxLine />
                            </span>
                            <span className={style.txt}>Sair</span>
                        </Link>
                    </nav>
                </div>
                */}
            </div>
        </>
    )
}
