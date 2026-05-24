import React from 'react';
import style from './AskStudent.module.css';
import '../../../../assets/style/global.style.css'
import MenuNavBarCliente from '../../../../Components/Elements/MenuNavBarCliente/MenuNavBarCliente'
import Header from '../../../../Components/Elements/Header/Header'
import { useAuth } from '../../../../Context/AuthContext';
import SolicitacaoFlow from '../../../../Components/Features/Documents/SolicitacaoFlow';

const AskStudent = () => {
  const { user, loading: authLoading } = useAuth();

  if (authLoading || !user) {
    return (
      <div className='containelGeralclient'>
        <MenuNavBarCliente user={'student'} />
        <main className='containelMainclient'>
          <Header text1="Estudante" text2="Nova Solicitação" />
          <div className={style.container}>
            <p style={{ textAlign: 'center', padding: '2rem' }}>Carregando...</p>
          </div>
        </main>
      </div>
    );
  }


  return (
    <div className='containelGeralclient'>
      <MenuNavBarCliente user={'student'} />
      <main className='containelMainclient'>
        <Header text1="Estudante" text2="Nova Solicitação" />
        <div className={style.container}>
          <header className={style.header}>
            <h1>Solicitar Novo Documento</h1>
            <p>Selecione o documento desejado e descreva o motivo da solicitação.</p>
          </header>

          <div className={style.formContainer}>
            <SolicitacaoFlow
              userType="aluno"
              onComplete={() => console.log("Solicitação completada")}
            />
          </div>
        </div>
      </main>
    </div>
  );
};

export default AskStudent;
