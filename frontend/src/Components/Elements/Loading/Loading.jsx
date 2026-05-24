import React from 'react';
import style from './Loading.module.css';

const Loading = ({ message = "Sistema de Gestão de Declarações Escolares", subMessage = "Processando informações..." }) => {
    return (
        <div className={style.loaderContainer}>
            <div className={style.loaderContent}>

                {/* Harmonic Spinner Structure */}
                <div className={style.spinnerWrapper}>
                    <div className={style.spinnerRingOne}></div>
                    <div className={style.spinnerRingTwo}></div>
                    <div className={style.spinnerRingThree}></div>
                    <div className={style.spinnerCore}></div>
                </div>

                {/* Typography with animations */}
                <div className={style.textWrapper}>
                    <div className={style.mainText}>{message}</div>
                    <div className={style.subText}>{subMessage}</div>
                </div>
            </div>
        </div>
    );
};

export default Loading;
