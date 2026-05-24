import style from './InfrastructureSection.module.css';
import { Link } from 'react-router-dom';
import { FaBook, FaWifi, FaComputer, FaFlask } from "react-icons/fa6";
import { useScrollReveal } from '../../../../../hooks/useScrollReveal';
import img1 from '../../../../../assets/images/escola01.jpg';
import img2 from '../../../../../assets/images/escola02.jpg';

export default function InfrastructureSection() {
    const sectionRef = useScrollReveal();

    return (
        <section className={style.InfrastructureSection} ref={sectionRef}>
            <div className={style.OverlayPattern}></div>
            <div className={style.Container}>

                <div className={`${style.TextContent} reveal-left`}>
                    <h2>Infraestruturas e Recursos</h2>
                    <p>
                        O IPM é uma instituição com várias vantagens. Nós instruimos, e os nossos alunos aplicam isso no mundo real.
                    </p>

                    <div className={style.FacilitiesGrid}>
                        <div className={style.FacilityItem}>
                            <h4><FaBook /> Biblioteca Digital</h4>
                            <p>Acesso ilimitado a  obras desde livros até documentação na area da tecnologia, administração serviços sociais .</p>
                        </div>
                        <div className={style.FacilityItem}>
                            <h4><FaComputer /> Lab. de Informática</h4>
                            <p>Equipamentos limitados, cerca de 20 computadores em toda a instituição.</p>
                        </div>
                        <div className={style.FacilityItem}>
                            <h4><FaWifi /> Campus</h4>
                            <p>Campus acolhedor, no IPM sempre visamos a mostrar aos nossos aluno como se comportarem.</p>
                        </div>

                    </div>

                    <Link to="/public/library" className={style.LibraryBtn}>
                        Acessar Biblioteca <FaBook />
                    </Link>
                </div>

                <div className={`${style.ImageGrid} reveal-right delay-300`}>
                    <img src={img1} alt="Laboratório" />
                    <img src={img2} alt="Biblioteca" />
                </div>

            </div>
        </section>
    );
}
