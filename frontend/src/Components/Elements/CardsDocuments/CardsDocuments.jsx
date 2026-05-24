import { Link } from 'react-router-dom'
import style from './CardsDocuments.module.css'
export default function CardsDocments({ icon, text, url,text_display }) {
    return (
        <>
            <Link to={url} className={`${style.cardDocument} glass-card`}>
                {icon}
                <h3 className="text-gradient">{text}</h3>
                <button style={{
                    border:'1px dashed var(--primary)',
                    color:'var(--primary)',
                    boxShadow:'0px 0px 2px var(--primary)'
                }}> {text_display || "Solicitar"}</button>
            </Link>
        </>
    )

}