import style from './HeroSection.module.css';
import { FaArrowRight } from 'react-icons/fa6';
import {Link} from 'react-router-dom'
import img from '../../../../../assets/images/Online learning-amico.svg'
export default function HeroSection() {
    return (
        <section className={style.hero}>
            <div className={style.container}>
                <div className={style.badge}>
                    <span>Nova era de excelência educacional</span>
                </div>

                <h1 className={style.title}>
                    Transforme o seu <br />
                    <span className={style.gradientText}>Futuro Profissional</span>
                </h1>

                <p className={style.description}>
                    No Instituto Politécnico do Maiombe, oferecemos excelência educacional com cursos projetados
                    para impulsionar a sua carreira no mercado global de trabalho.
                </p>

                <div className={style.ctaGroup}>
                    <Link className={style.primaryBtn} to={"/public/library"}>
                        Explorar Biblioteca
                        <FaArrowRight />
                    </Link>
           
                </div>
            </div>

            <div className={style.visualElement}>
                <div className={style.glowCircle}></div>
                <div className={style.floatingCard}>
                    <div className={style.cardHeader}>
                        <div className={style.dot}></div>
                        <div className={style.line}></div>
                    </div>
                    <div className={style.cardBody}>
                        <div className={style.skeletonLine}>
                            <img src={img} alt="" />
                        </div>
                      
                    </div>
                </div>
            </div>
        </section>
    );
}
