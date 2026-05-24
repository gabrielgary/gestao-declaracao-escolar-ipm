import style from './AuthGeneral.module.css'
import { useForm } from "react-hook-form";
import { Link, useNavigate } from 'react-router-dom'
import favicon from '../../../assets/images/favicon.ico'
import fundo_login from '../../../assets/images/backgroundLogin.png'
import fundo_login2 from '../../../assets/images/backgroundEncaregados.png'
import fundo_login3 from '../../../assets/images/img-login.jpg'
import { useAuth } from '../../../Context/AuthContext';
import { useState } from 'react';

export default function AuthGeneral({ userType = 'aluno', destination = '/student/dashboard' }) {
    const { register, handleSubmit, formState: { errors } } = useForm();
    const { login } = useAuth();
    const navigate = useNavigate();
    const [loginError, setLoginError] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    async function onSubmit(data) {
        setIsSubmitting(true);
        setLoginError('');
        const { email, password } = data;

        const result = await login(email, password, userType);

        if (result.success) {
            navigate(destination);
        } else {
            setLoginError(result.message || "Erro ao iniciar sessão.");
        }
        setIsSubmitting(false);
    }
     
    return (
        <>
            <div className={style.containerForm}>
                <div className={style.cardForm}>
                    <div className={style.form}>
                        <div className={style.infos}>
                            <div className={style.logo}>
                                <img src={favicon} alt="" width={30} /> <small className='s'>IPM</small>
                            </div>
                            <div className={style.mensage}>
                                <h1>Olá, <br /> Bem-Vindo de Volta</h1>
                                <p>
                                    Painel do {userType === 'funcionario' ? 'Administrador' : userType}
                                </p>
                                <small className=''>Oi, bem-vindo de volta ao nosso sistema ({userType === 'funcionario' ? 'Admin' : userType})</small>
                            </div>

                        </div>
                        <form onSubmit={handleSubmit(onSubmit)}>
                            <div className={style.inputController}>

                                <input type="text" placeholder='E-mail'  {...register("email", {
                                    required: "E-mail é um campo Obrigatório"
                                })}
                                autoComplete='email'
                                />
                                {
                                    errors && (

                                        <p className={style.errorRequiredInput}>{errors.email?.message}</p>
                                    )
                                }
                            </div>
                            <div className={style.inputController}>
                                <input type="password" placeholder='Palavra-Passe' {...register("password",
                                    {
                                        required: "Palavra-Passe é um campo Obrigatório"

                                    })} autoComplete='current-password' />
                                {
                                    errors && (

                                        <p className={style.errorRequiredInput}>{errors.password?.message}</p>
                                    )
                                }
                            </div>

                            {loginError && <p className={`text-red-500 text-sm mb-2 ${style.error}`}>{loginError}</p>}

                            <div className={style.forgotPassword}>
                                <small>  <Link to='/auth/forgot-password'>Esqueceu a senha?</Link></small>
                            </div>
                            <div className={style.inputController}>
                                <button type='submit' disabled={isSubmitting} className={`${userType==="aluno"?style.student:userType==="encarregado"?style.parent:userType==="funcionario"?style.admin:style.admin}`}>
                                    {isSubmitting ? 'A entrar...' : 'Iniciar Sessão'}
                                </button>
                            </div>
                        </form>
                    </div>
                    <div className={style.background}>
                        <div>
                            {
                                userType == "aluno" ? (

                                    <img src={fundo_login} alt="" />
                                ) : (
                                    userType == "encarregado" ? (

                                        <img src={fundo_login2} alt="" />
                                    ) : (
                                        <img src={fundo_login3} alt="" />

                                    )

                                )
                            }
                        </div>
                    </div>
                </div>
            </div>
        </>
    )
}
