import React, { useEffect, useState } from 'react';
import style from './Children.module.css';

// padrão para todas as paginas
import '../../../../assets/style/global.style.css'
import { Link } from 'react-router-dom'
import MenuNavBarCliente from '../../../../Components/Elements/MenuNavBarCliente/MenuNavBarCliente'
import Header from '../../../../Components/Elements/Header/Header'
import { RiUser3Line, RiArrowRightSLine, RiUser6Line, RiGroupLine } from 'react-icons/ri'
import { useAuth } from '../../../../Context/AuthContext';
import api from '../../../../Services/api';
import Loading from '../../../../Components/Elements/Loading/Loading'
const Children = () => {
  const { user } = useAuth();
  const [childrenData, setChildrenData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchChildren = async () => {
      try {
        if (user?.id) {
          const response = await api.get(`/encarregados/${user.id}/educandos/`);
          setChildrenData(response.data);
          console.log(response.data);

        }
      } catch (error) {
        console.error("Erro ao carregar educandos:", error);
      } finally {

        setLoading(false);
      }
    };
    fetchChildren();
  }, [user]);
 
  const MEDIA_BASE = import.meta.env.VITE_API_BASE_URL 
    ? import.meta.env.VITE_API_BASE_URL.replace(/\/api\/v1\/?$/, '/media')
    : 'http://localhost:8000/media';

  const normalizeUrl = (url) => {
    if (!url) return null;
    if (typeof url !== 'string') return url.url || null;
    if (url.startsWith('http')) return url;
    const cleanPath = url.replace(/^\/media\//, '').replace(/^media\//, '');
    return `${MEDIA_BASE}/${cleanPath.replace(/^\//, '')}`;
  };

  return (
    <div className='containelGeralclient'>
      <MenuNavBarCliente user={'parent'} />
      <main className='containelMainclient'>
        <Header text1="Meus Educandos" text2="Gestão de Alunos" />

        <div className={style.childrenContainer}>
          <header className={style.sectionHeader}>
            <h1>Gestão de Educandos  <RiGroupLine /></h1>
            <p>Acompanhe o desempenho individual, assiduidade e situação administrativa de cada um dos seus educandos.</p>
          </header>

          <div className={style.childrenGrid}>
            {loading ? (
              <p><Loading /></p>
            ) : childrenData.length > 0 ? (
              childrenData.map((child) => (
                <Link
                  to="/parent/actionstudent"
                  key={child.id_aluno}
                  className={style.childCard}
                  onClick={() => localStorage.setItem('selectedStudent', JSON.stringify(child))}
                >
                  <div className={style.avatar}>
                    {child.img_path ? (
                      <img src={normalizeUrl(child.img_path)} alt={child.nome_completo} className={style.avatarImage} />
                    ) : (
                      <RiUser3Line />
                    )}
                  </div>

                  <div className={style.info}>
                    <h3>{child.nome_completo}</h3>
                    <p>{child.classe_nivel || 'Classe N/A'} - {child.curso_nome || 'Curso N/A'}</p>
                    <small className="text-gray-400">Turma: {child.turma_codigo || 'N/A'}</small>
                  </div>

                  <div className={style.stats}>
                    
               
                    <div className={style.statItem} style={{
                      
                      margin:'auto'
                    }}>
                      <span className={`${style.statValue} ${child.status_aluno === 'Activo' ? 'text-emerald-500' : 'text-red-500'}`}>
                        {child.status_aluno}
                      </span>
                      <span className={style.statLabel}>Status</span>
                    </div>
                  </div>

                  <div className={style.actions}>
                    <button className={style.btnAction}>
                      Ver Detalhes <RiArrowRightSLine />
                    </button>
                  </div>
                </Link>
              ))
            ) : (
              <p>Nenhum educando vinculado a este encarregado.</p>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default Children;

