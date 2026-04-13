import style from './FooterSection.module.css';

export default function FooterSection() {
    return (
        <footer className={style.FooterSection}>
            <div className={style.Container}>
                <div className={style.TopRow}>
                    <div className={style.Col}>
                        <h3>Instituto Politécnico <br />Do Maiombe</h3>
                        <p className={style.Description}>
                            Excelência no ensino e formação profissional. Preparando o futuro de Angola, hoje.
                        </p>
                        <p className={style.Description}>Tel: +244 934 519 321<br />Email: ipm@gmail.com</p>
                    </div>
 

                      
                    <div className={style.Col}>
                        <h4>Cursos</h4>
                        <ul className={style.LinksList}>
                            <li>Informática de Gestão</li>
                            <li>Contabilidade de Gestão</li>
                            <li>Gestão Empresarial</li>
                            <li>Informática</li>
                        </ul>
                    </div>
 
                </div>

                <div className={style.BottomRow}>
                    <p>&copy; 2025 Instituto Politécnico do Maiombe. Todos os direitos reservados.</p>
                   
                </div>
            </div>
        </footer>
    );
}
