import React from 'react';
import style from './SolicitacaoParent.module.css';

// padrão para todas as paginas
import '../../../../assets/style/global.style.css'
import MenuNavBarCliente from '../../../../Components/Elements/MenuNavBarCliente/MenuNavBarCliente'
import Header from '../../../../Components/Elements/Header/Header'
import SolicitacaoFlow from '../../../../Components/Features/Documents/SolicitacaoFlow';

const SolicitacaoParent = () => {
  return (
    <div className='containelGeralclient'>
      <MenuNavBarCliente user={'parent'} />
      <main className='containelMainclient'>
        <Header text1="Solicitações" text2="Centro de Serviços" />

        <div className={style.formContainer}>
          <div className={style.cardForm}>
            <header className={style.formHeader}>
              <h2>Nova Solicitação</h2>
              <p>Siga os passos abaixo para solicitar documentos oficiais ou serviços, confirmar os dados e efetuar o pagamento.</p>
            </header>

            <SolicitacaoFlow userType="encarregado" />
          </div>
        </div>
      </main>
    </div>
  );
};

export default SolicitacaoParent;

