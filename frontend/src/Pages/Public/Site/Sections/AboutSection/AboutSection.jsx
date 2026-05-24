import style from './AboutSection.module.css';
import aboutImg from '../../../../../assets/images/escola02.jpg';
import { FaCheck } from "react-icons/fa6";
import { Link } from 'react-router-dom';
import { useScrollReveal } from '../../../../../hooks/useScrollReveal';

export default function AboutSection() {
    const sectionRef = useScrollReveal();

    return (
        <section className={style.AboutSection} ref={sectionRef}>
            <div className={`${style.Container} reveal`}>
                {/* Image Col */}
                <div className={`${style.ImageCol} reveal-left`}>
                    <img src={aboutImg} alt="Sobre Nós" className={style.MainImage} />
                    <div className={style.FloatingBadge}>
                        <div className={style.BadgeIcon}>
                            <FaCheck />
                        </div>
                        <div className={style.BadgeText}>
                            <h4>+4 Anos</h4>
                            <span>de Experiência</span>
                        </div>
                    </div>
                </div>

                {/* Text Col */}
                <div className={`${style.TextCol} reveal-right`}>
                    <span className={style.SubTitle}>Sobre Nós</span>
                    <h2 className={style.Title}>Quem Somos?</h2>
                    <p className={style.Description}>
                        O Instituto Politécnico do Maiombe é um instituto localizado na Provincia do Icole e Bengo, no Seleque bairro do Maiombe
                    </p>

                    <ul className={style.CheckList}>
                        <li>
                            <div className={style.CheckIcon}><FaCheck /></div>
                            <div>
                                <strong>Ensino Orientado à Prática</strong>
                                <p>O IPM tem uma forte força tarefa que ajudam os alunos a conseguirem alcançar seus objectivos.</p>
                            </div>
                        </li>
                        <li>
                            <div className={style.CheckIcon}><FaCheck /></div>
                            <div>
                                <strong>Corpo Docente Qualificado</strong>
                                <p>Professores com ampla experiência acadêmica</p>
                            </div>
                        </li>
                    </ul>


                </div>
            </div>
        </section>
    );
}
