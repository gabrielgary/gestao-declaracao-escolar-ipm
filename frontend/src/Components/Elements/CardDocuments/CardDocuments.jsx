import {FaEye,FaCartPlus} from 'react-icons/fa6'
import style from './CardDocuments.module.css'
export default function CardDocuments() {
    return (
        <div className={style.resourceCard} data-title="${livro.title_book}}">
            <div className={style.resourceImage}>
                <object data={'PostgreSQLNotesForProfessionals'} type="">
                </object>
                <div className={style.mirror}>

                </div>
            </div>
            <div className={style.resourceInfo}>
                <h3 className={style.resourceTitle}>Html5 & Css3</h3>
                <p className={style.resourceAuthor}>{"stateCategoria"} </p>
                <div className={style.resourceFooter}>
                    <div className={style.resourceType}>Livro</div>
                    <div className={style.resourceActions}>
                        <a href=""><FaEye size={15} /></a>
                        <a href=""><FaCartPlus /></a>
                    </div>
                </div>
            </div>
        </div>
    )
}