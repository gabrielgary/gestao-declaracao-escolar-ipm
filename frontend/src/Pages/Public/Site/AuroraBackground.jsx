import style from './AuroraBackground.module.css';

const AuroraBackground = ({ children }) => {
    return (
        <div className={style.auroraContainer}>
            <div className={style.auroraWrapper}>
                <div className={style.auroraItem + ' ' + style.aurora1}></div>
                <div className={style.auroraItem + ' ' + style.aurora2}></div>
                <div className={style.auroraItem + ' ' + style.aurora3}></div>
                <div className={style.auroraItem + ' ' + style.aurora4}></div>
            </div>
            <div className={style.content}>
                {children}
            </div>
        </div>
    );
};

export default AuroraBackground;
