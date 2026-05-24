
import os
import sys
import django
from django.utils import timezone
from datetime import timedelta

# Setup Django Environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apis.models import Aluno, Turma, Classe, Curso, Periodo, SolicitacaoDocumento, Fatura, Funcionario, Sala
from apis.services.document_service import DocumentService

def run_tests():
    print("🚀 Iniciando Testes de Integração - Fluxo Dia 9 (Documentos & Pagamentos)...")

    # 1. Setup de Dados de Teste
    print("\n[1] Criando dados de teste...")
    try:
        # Criar dados básicos se não existirem (usando get_or_create para evitar duplicação)
        sala, _ = Sala.objects.get_or_create(numero_sala="101", defaults={'capacidade': 30, 'localizacao': 'Bloco A'})
        periodo, _ = Periodo.objects.get_or_create(periodo="Manhã", defaults={'horario_inicio': '07:00:00', 'horario_fim': '12:00:00'})
        classe, _ = Classe.objects.get_or_create(nivel=10, defaults={'descricao': 'Décima Classe', 'ciclo': 'I Ciclo'})
        curso, _ = Curso.objects.get_or_create(nome_curso="Informática", defaults={'codigo_curso': 'INF', 'descricao': 'Curso Técnico'})
        
        turma, _ = Turma.objects.get_or_create(
            codigo_turma="INF10A",
            defaults={
                'id_classe': classe, 'id_curso': curso, 'id_periodo': periodo, 
                'id_sala': sala, 'ano': '2026', 'ano_lectivo': '2026'
            }
        )

        aluno, created = Aluno.objects.get_or_create(
            numero_bi="000TESTE000",
            defaults={
                'nome_completo': "Aluno Teste Integração",
                'email': "teste@escola.com",
                'id_turma': turma,
                'genero': 'M',
                'estado_civil': 'Solteiro'
            }
        )
        if created: print("   > Aluno de teste criado.")

        funcionario, created = Funcionario.objects.get_or_create(
            numero_bi="000FUNC000",
            defaults={
                'nome_completo': "Funcionário Teste", 
                'cargo': 'Secretário'
            }
        )
        if created: print("   > Funcionário de teste criado.")

    except Exception as e:
        print(f"❌ Erro no setup de dados: {e}")
        return

    # 2. Cenário A: Solicitação via RUP (Aluno/Encarregado)
    print("\n[2] Testando Cenário A: Solicitação RUP (Manual)...")
    try:
        solicitacao, fatura = DocumentService.criar_solicitacao(
            aluno_id=aluno.id_aluno,
            tipo_documento="DECLARAÇÃO",
            canal_pagamento="fisico_rup",
            classe_id=classe.id_classe
        )
        
        if solicitacao.status_solicitacao == 'pendente':
            print("   ✅ Solicitação criada com status 'pendente'.")
        else:
            print(f"   ❌ Falha: Status incorreto: {solicitacao.status_solicitacao}")

        if solicitacao.rupe:
            print(f"   ✅ Código RUP gerado: {solicitacao.rupe}")
        else:
             print("   ❌ Falha: RUP não gerado.")

        # Gerar PDF do RUP
        path_rup = DocumentService.gerar_comprovativo_rup(solicitacao.id_solicitacao)
        if path_rup:
             print(f"   ✅ PDF do RUP gerado em: {path_rup}")
        else:
            print("   ❌ Falha ao gerar PDF do RUP.")
            
    except Exception as e:
        print(f"❌ Erro no Cenário A: {e}")


    # 3. Cenário B: Pagamento Instantâneo (Funcionário)
    print("\n[3] Testando Cenário B: Pagamento Instantâneo (Funcionário)...")
    try:
        # Criar nova solicitação
        sol_instant, _ = DocumentService.criar_solicitacao(
            aluno_id=aluno.id_aluno,
            tipo_documento="BOLETIM",
            canal_pagamento="confirmado_local",
            classe_id=classe.id_classe
        )
        print(f"   > Solicitação {sol_instant.id_solicitacao} criada (Pendente).")

        # Confirmar Pagamento
        path_final = DocumentService.confirmar_pagamento_funcionario(sol_instant.id_solicitacao, funcionario.id_funcionario)
        
        # Recarregar
        sol_instant.refresh_from_db()

        if sol_instant.status_solicitacao == 'impresso' or sol_instant.status_solicitacao == 'pago':
             # Note: logic might set it to 'impresso' or 'pago' depending on flow, let's verify
             print(f"   ✅ Status atualizado para: {sol_instant.status_solicitacao}")
        else:
             print(f"   ❌ Falha: Status não atualizado corretamente ({sol_instant.status_solicitacao})")

        if path_final and sol_instant.caminho_arquivo:
             print(f"   ✅ Documento Final gerado em: {path_final}")
        else:
             print("   ❌ Falha: Documento Final não gerado.")

    except Exception as e:
        print(f"❌ Erro no Cenário B: {e}")

    print("\n🏁 Testes Finalizados!")

if __name__ == "__main__":
    run_tests()
