import style from './ServicesSection.module.css';
import { FaComputer, FaCalculator, FaNetworkWired } from "react-icons/fa6";
import { BsGraphUpArrow } from "react-icons/bs";
import { useScrollReveal } from '../../../../../hooks/useScrollReveal';

const courses = [
    {
        title: "Informática de Gestão",
        description: "Domine o planeamento, arquitetura desenvolvimento e administração de sistemas com foco empresarial.",
        icon: <FaComputer />,
        glowColor: "rgba(138, 180, 248, 0.4)"
    },
    {
        title: "Gestão Empresarial",
        description: "Desenvolva visão estratégica para liderar negócios e otimizar processos.",
        icon: <BsGraphUpArrow />,
        glowColor: "rgba(162, 115, 255, 0.3)"
    },
    {
        title: "Contabilidade de Gestão",
        description: "Especialize-se em análise financeira, custos e tomada de decisão contábil.",
        icon: <FaCalculator />,
        glowColor: "rgba(25, 211, 141, 0.3)"
    },
    {
        title: "Informática",
        description: "Fundamentos sólidos de tecnologia, programação e suporte técnico.",
        icon: <FaNetworkWired />,
        glowColor: "rgba(138, 180, 248, 0.4)"
    }
];

export default function ServicesSection() {
    const sectionRef = useScrollReveal();

    return (
        <section className={style.services} id="servicos" ref={sectionRef}>
            <div className={style.container}>
                <div className={`${style.header} reveal`}>
                    <h2 className={style.title}>Nossos Cursos</h2>
                    <p className={style.subtitle}>Formação Profissional de Excelência para o Mercado Global</p>
                </div>

                <div className={style.grid}>
                    {courses.map((course, index) => (
                        <div
                            key={index}
                            className={`${style.card} reveal ${
                                index === 0 ? 'reveal-left' :
                                index === courses.length - 1 ? 'reveal-right' : ''
                            } delay-${(index + 1) * 100}`}
                        >
                            <div className={style.iconWrapper} style={{ '--glow': course.glowColor }}>
                                {course.icon}
                            </div>
                            <h3 className={style.cardTitle}>{course.title}</h3>
                            <p className={style.cardDescription}>{course.description}</p>
                            {/*  <div className={style.cardFooter}>
                                <button className={style.learnMore}>Saiba mais</button>
                            </div>
                            */}
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
