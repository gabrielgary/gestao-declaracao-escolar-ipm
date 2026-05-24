
import style from './Cards.module.css'

export default function Cards({ icon, value, title, value_percentual }) {
    return (

        <div className={`${style.StatCard} glass-card`}>
            <div className={style.CardHeader}>
                <span className="text-gradient">{title}</span>
                {icon}
            </div>
            <h2>{value}</h2>
            <div className={value_percentual && value_percentual.includes('+') ? style.TrendUp : style.TrendDown}>
                {
                    value_percentual?(
                        <>
                        <span>{value_percentual}</span> vs mês passado
                        </>
                    ):(
                        <></>
                    )
                }
            </div>
        </div>

    )
}
