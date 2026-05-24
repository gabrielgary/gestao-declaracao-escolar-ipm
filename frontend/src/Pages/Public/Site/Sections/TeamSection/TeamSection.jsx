import style from './TeamSection.module.css';
import p1 from '../../../../../assets/images/escola01.jpg'; // Placeholder - ideally distinct avatars
import p2 from '../../../../../assets/images/escola02.jpg';

export default function TeamSection() {
    // Placeholder data
    const team = [
        { name: 'Dr. Romeu', role: 'Director Geral', img: p1 },
        { name: 'Dr. Gabriel Rufino', role: 'Director Pedagógica', img: p2 },
        { name: 'Eng. Ramos Panzo', role: 'Coord. da Área de Informática', img: p1 },
        { name: 'Prf. Franscisco', role: 'Director do GIVA', img: p2 },
    ];

    return (
        <section className={style.TeamSection}>
            <div className={style.Container}>
                <div className={style.Header}>
                    <h2 className={style.Title}>Conheça a Nossa Liderança</h2>
                    <p style={{ color: '#64748b' }}>Profissionais dedicados ao sucesso da instituição.</p>
                </div>

                <div className={style.TeamGrid}>
                    {team.map((member, index) => (
                        <div key={index} className={style.TeamCard}>
                            <div className={style.ImageWrapper}>
                                <img src={member.img} alt={member.name} className={style.ProfileImg} />
                            </div>
                            <h3>{member.name}</h3>
                            <span>{member.role}</span>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
