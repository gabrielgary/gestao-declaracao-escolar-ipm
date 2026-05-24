
import { BsLayoutSidebar } from 'react-icons/bs'
import style from './MenuClient.module.css'
import { Link } from 'react-router-dom'
import { useState } from 'react'
export default function MenuClient({ children }) {
    const [toggleMenu, setToggleMenu] = useState(false);

    return (
        <nav className={style.NavBarMenuClient +` ${toggleMenu?style.extendsMenu:''}`}>
            <div className={style.btnExpandir}>
                <span onClick={() => setToggleMenu((prev) => prev = !prev)}>
                    <BsLayoutSidebar/>
                </span>
            </div>
            {children}
        </nav>
    )
}