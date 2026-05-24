
import style from './NavBarMenu.module.css'
import {
    FaUserGraduate,
    FaAtom,

    FaFile,
    FaClockRotateLeft
} from 'react-icons/fa6';
import { Link } from 'react-router-dom'
import { BsCart3, BsFolder, BsHouse, BsPeople } from "react-icons/bs";
import { FiTrendingUp } from "react-icons/fi";
import { RiBillLine } from "react-icons/ri";
import { HiOutlineDocumentReport } from "react-icons/hi";
import { CiFileOn, CiSettings } from 'react-icons/ci';
import favicon from '../../../assets/images/favicon.ico'

//import { useAuth } from '../../../Context/AuthContext';
import { FaGraduationCap } from 'react-icons/fa6';

export default function NavBarMenu() {
   // const { user } = useAuth();
    /*const isProfessor = user?.cargo?.toLowerCase().includes('professor') || user?.cargo?.toLowerCase().includes('docente');
    const isAdmin = user?.cargo?.toLowerCase().includes('administrador');
*/
    return (
        <>
            <aside className={style.Sidebar}>
                <div className={style.Logo}>
                    <div className={style.LogoIcon}><img src={favicon} alt="" /></div>
                    <h2>Gestão de Declarações</h2>
                </div>

                <div className={style.MenuSection}>
                    <h3>Menu</h3>
                    <ul>
                        <li>
                            <Link to={"/admin/dashboard"}>
                                <BsHouse />
                                <span>Dashboard</span>
                            </Link>
                        </li>

                        {/*(isProfessor || isAdmin) && (
                            <li>
                                <Link to={"/admin/notas"}>
                                    <FaGraduationCap />
                                    <span>Lançar Notas</span>
                                </Link>
                            </li>
                        )*/}

                        <li>
                            <Link to={"/admin/ask"}>
                                <BsCart3 />
                                <span>Solicitações</span>
                                <span className={style.Badge}></span>
                            </Link>
                        </li>
                        <li>
                            <Link to={"/admin/library"}>
                                <BsFolder />
                                <span>Biblioteca</span>
                            </Link>
                        </li>
                        <li>
                            <Link to={"/agent/yasmin"}>
                                <FaAtom />                              
                                <span>Yasmin</span>
                            </Link>
                        </li>
                        <li>
                            <Link to={'/admin/funcionario'}>
                                <span className={style.icon}>
                                    <BsPeople />
                                </span>
                                <span className={style.txt}>Funcionarios</span>
                            </Link>
                        </li>
                        <li>
                            <Link to={'/admin/parent'}>
                                <span className={style.icon}>
                                    <BsPeople />
                                </span>
                                <span className={style.txt}>Encarregados</span>
                            </Link>
                        </li>
                        <li>
                            <Link to={"/admin/student"}>
                                <FaUserGraduate />
                                <span>Alunos</span>
                            </Link>
                        </li>
                        <li>
                            <Link to={"/admin/turmas"}>
                                <BsPeople />
                                <span>Turmas</span>
                            </Link>
                        </li>
                    </ul>
                </div>

                <div className={style.MenuSection}>
                    <h3>Documentos</h3>
                    <ul>
                        <li>
                            <Link to={"/admin/declaracao"}>
                                <FaFile /> Declarações
                            </Link>
                        </li>
                        <li>
                            <Link to={"/admin/boletim"}>
                                <CiFileOn /> Boletins
                            </Link>
                        </li>
                        <li>
                            <Link to={"/admin/certificado"}>
                                <RiBillLine /> Certificados
                            </Link>
                        </li>


                    </ul>
                </div>

                <div className={style.MenuSection}>
                    <ul>
                        <li>
                            <Link to={"/admin/history"}>
                                <FaClockRotateLeft /> Histórico
                            </Link>
                        </li>
                        <li>
                            <Link to={"/admin/setting"}>
                                <CiSettings /> Configurações
                            </Link>
                        </li>
                        <li>
                            <Link to={"/admin/reports"}>
                                <HiOutlineDocumentReport /> Relatórios
                            </Link>
                        </li>

                    </ul >
                </div >

            </aside >


        </>
    )
}