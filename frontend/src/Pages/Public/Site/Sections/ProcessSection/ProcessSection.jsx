import style from './ProcessSection.module.css';

export default function ProcessSection() {
    return (
        <section className={style.ProcessSection}>
            <div className={style.Container}>
                <div className={style.Header}>
                    <span className={style.SubTitle}>Nosso Processo</span>
                    <h2 className={style.Title}>Porque Escolher o IPM para o Seu Crescimento?</h2>
                </div>

                <div className={style.StepsGrid}>
                    <div className={style.StepCard}>
                        <span className={style.StepNumber}>01</span>
                        <h3>Inscrição Simplificada</h3>
                        <p>Processo de admissão rápido e digital para você focar no que importa: seu aprendizado.</p>
                    </div>

                    <div className={style.StepCard}>
                        <span className={style.StepNumber}>02</span>
                        <h3>Formação Prática</h3>
                        <p>Currículo focado em projetos reais e laboratórios equipados com tecnologia de ponta.</p>
                    </div>

                    <div className={style.StepCard}>
                        <span className={style.StepNumber}>03</span>
                        <h3>Estágios Garantidos</h3>
                        <p>Parcerias com as melhores empresas para garantir sua inserção no mercado de trabalho.</p>
                    </div>

                    <div className={style.StepCard}>
                        <span className={style.StepNumber}>04</span>
                        <h3>Suporte Contínuo</h3>
                        <p>Acompanhamento pedagógico e de carreira durante toda a sua jornada acadêmica.</p>
                    </div>
                </div>
            </div>
        </section>
    );
}
