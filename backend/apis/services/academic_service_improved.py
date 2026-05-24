from django.db.models import Avg, Q
from apis.models import Nota, FaltaAluno, Aluno, Disciplina, MatrizCurricularDisciplina, MatrizCurricular, Matricula
import logging

logger = logging.getLogger(__name__)

class AcademicService:
    """
    Serviço para gestão de notas, faltas e desempenho académico
    Versão melhorada com tratamento robusto de erros e fallbacks
    """
    
    @staticmethod
    def calcular_media_disciplina(aluno_id, disciplina_id):
        """
        Calcula a média de um aluno em uma disciplina específica
        """
        try:
            notas = Nota.objects.filter(
                id_aluno_id=aluno_id, 
                id_disciplina_id=disciplina_id,
                valor__isnull=False
            )
            if not notas.exists():
                return 0
                
            media = notas.aggregate(Avg('valor'))['valor__avg']
            return round(media, 2) if media else 0
        except Exception as e:
            logger.error(f"Erro ao calcular média da disciplina {disciplina_id}: {str(e)}")
            return 0

    @staticmethod
    def obter_resumo_academico(aluno_id):
        """
        Retorna um resumo completo do desempenho do aluno
        """
        try:
            aluno = Aluno.objects.select_related('id_turma', 'id_turma__id_classe').get(id_aluno=aluno_id)
            notas = Nota.objects.filter(
                id_aluno=aluno,
                valor__isnull=False
            ).select_related('id_disciplina')
            faltas = FaltaAluno.objects.filter(id_aluno=aluno).count()
            
            media_geral = notas.aggregate(Avg('valor'))['valor__avg'] or 0
            
            # Agrupar por disciplina
            disciplinas_stats = {}
            for nota in notas:
                if nota.id_disciplina:
                    disc_nome = nota.id_disciplina.nome
                    if disc_nome not in disciplinas_stats:
                        disciplinas_stats[disc_nome] = []
                    disciplinas_stats[disc_nome].append(float(nota.valor))
                    
            resumo_disciplinas = [
                {
                    'disciplina': nome,
                    'media': round(sum(vals)/len(vals), 2),
                    'total_avaliacoes': len(vals)
                }
                for nome, vals in disciplinas_stats.items()
            ]
            
            return {
                'aluno': aluno.nome_completo,
                'media_geral': round(media_geral, 2),
                'total_faltas': faltas,
                'desempenho_por_disciplina': resumo_disciplinas,
                'situacao': 'Aprovado' if media_geral >= 10 else 'Reprovado'
            }
        except Aluno.DoesNotExist:
            logger.error(f"Aluno {aluno_id} não encontrado")
            return None
        except Exception as e:
            logger.error(f"Erro ao obter resumo acadêmico do aluno {aluno_id}: {str(e)}")
            return None

    @staticmethod
    def get_boletim_aluno(aluno, classe=None):
        """
        Calcula as notas detalhadas (MAC, PP, PT) e médias por trimestre.
        Retorna estrutura pronta para a Declaração de Aproveitamento e Boletim.
        Versão melhorada com tratamento robusto de erros.
        """
        try:
            logger.info(f"Gerando boletim para aluno: {aluno.nome_completo if aluno else 'Unknown'}")
            
            # Validar entrada
            if not aluno:
                logger.error("Aluno não fornecido")
                return []
                
            # 1. Buscar informações do aluno com relacionamentos
            try:
                aluno_obj = Aluno.objects.select_related(
                    'id_turma', 
                    'id_turma__id_classe', 
                    'id_turma__id_curso',
                    'id_turma__id_matriz_curricular'
                ).get(id_aluno=aluno.id_aluno if hasattr(aluno, 'id_aluno') else aluno)
            except (Aluno.DoesNotExist, AttributeError):
                logger.error("Aluno não encontrado ou ID inválido")
                return []

            # 2. Determinar classe para busca
            classe_alvo = classe
            if not classe_alvo:
                classe_alvo = aluno_obj.id_turma.id_classe if aluno_obj.id_turma and aluno_obj.id_turma.id_classe else None

            # 3. Buscar matriz curricular (simplificado)
            matriz = None
            if aluno_obj.id_turma and aluno_obj.id_turma.id_matriz_curricular:
                matriz = aluno_obj.id_turma.id_matriz_curricular
            elif classe_alvo and aluno_obj.id_turma and aluno_obj.id_turma.id_curso:
                matriz = MatrizCurricular.objects.filter(
                    id_curso=aluno_obj.id_turma.id_curso,
                    id_classe=classe_alvo,
                    ativo=True
                ).first()

            # 4. Buscar notas do aluno (otimizado)
            notas_query = Nota.objects.filter(
                id_aluno=aluno_obj,
                valor__isnull=False
            ).select_related('id_disciplina')

            # Se tiver turma, filtrar por turma também
            if aluno_obj.id_turma:
                notas_query = notas_query.filter(id_turma=aluno_obj.id_turma)

            notas_aluno = notas_query.order_by('id_disciplina__nome', 'trimestre')
            
            if not notas_aluno.exists():
                logger.warning(f"Nenhuma nota encontrada para o aluno {aluno_obj.nome_completo}")
                return []

            # 5. Processar disciplinas e notas
            if matriz:
                # Usar matriz curricular se existir
                disciplinas_matriz = MatrizCurricularDisciplina.objects.filter(
                    id_matriz_curricular=matriz
                ).select_related('id_disciplina')
                
                resultados = []
                for m_disc in disciplinas_matriz:
                    resultado_disciplina = AcademicService._processar_disciplina(
                        m_disc.id_disciplina, 
                        notas_aluno.filter(id_disciplina=m_disc.id_disciplina),
                        coeficiente=float(m_disc.coeficiente)
                    )
                    if resultado_disciplina:
                        resultados.append(resultado_disciplina)
            else:
                # Fallback: usar disciplinas das notas do aluno
                disciplinas_unicas = {}
                for nota in notas_aluno:
                    if nota.id_disciplina:
                        disc_id = nota.id_disciplina.id_disciplina
                        if disc_id not in disciplinas_unicas:
                            disciplinas_unicas[disc_id] = nota.id_disciplina
                
                resultados = []
                for disciplina in disciplinas_unicas.values():
                    notas_disc = notas_aluno.filter(id_disciplina=disciplina)
                    resultado_disciplina = AcademicService._processar_disciplina(
                        disciplina, 
                        notas_disc,
                        coeficiente=1.0
                    )
                    if resultado_disciplina:
                        resultados.append(resultado_disciplina)

            logger.info(f"Boletim gerado com {len(resultados)} disciplinas para {aluno_obj.nome_completo}")
            return resultados

        except Exception as e:
            logger.error(f"Erro crítico ao gerar boletim: {str(e)}")
            return []

    @staticmethod
    def _processar_disciplina(disciplina, notas_disciplina, coeficiente=1.0):
        """
        Processa as notas de uma disciplina e retorna estrutura padronizada
        """
        try:
            if not disciplina:
                return None
                
            # Estrutura por trimestre
            grades = {
                '1': {'MAC': None, 'PP': None, 'PT': None, 'MT': None},
                '2': {'MAC': None, 'PP': None, 'PT': None, 'MT': None},
                '3': {'MAC': None, 'PP': None, 'PT': None, 'MT': None}
            }
            
            teve_nota = {'1': False, '2': False, '3': False}

            # Processar cada nota
            for nota in notas_disciplina:
                if not nota.tipo_nota or not nota.trimestre:
                    continue
                    
                # Normalizar trimestre
                t_raw = str(nota.trimestre)
                t_key = t_raw.split('º')[0].strip() if 'º' in t_raw else t_raw.strip()
                
                if t_key in grades and nota.tipo_nota in grades[t_key]:
                    grades[t_key][nota.tipo_nota] = float(nota.valor)
                    teve_nota[t_key] = True

            # Calcular Médias Trimestrais
            for t in grades:
                if teve_nota[t]:
                    v_mac = grades[t]['MAC'] if grades[t]['MAC'] is not None else 0.0
                    v_pp = grades[t]['PP'] if grades[t]['PP'] is not None else 0.0
                    v_pt = grades[t]['PT'] if grades[t]['PT'] is not None else 0.0
                    
                    mt = (v_mac + v_pp + v_pt) / 3
                    grades[t]['MT'] = round(mt, 1)

            # Média Final
            valores_mt = [grades[t]['MT'] for t in grades if grades[t]['MT'] is not None]
            media_final = sum(valores_mt) / len(valores_mt) if valores_mt else 0.0

            # Status da disciplina
            status_disciplina = '---'
            if len(valores_mt) == 3:
                status_disciplina = 'Aprovado' if round(media_final) >= 10 else 'Reprovado'

            return {
                'id_disciplina': disciplina.id_disciplina,
                'disciplina': disciplina.nome,
                'coeficiente': coeficiente,
                'trimestres': grades,
                'media_final': f"{media_final:.1f}",
                'media_final_valor': media_final,
                'media_final_extenso': AcademicService._nota_para_extenso(media_final),
                'resultado': status_disciplina,
                'count_mt': len(valores_mt)
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar disciplina {disciplina.nome if disciplina else 'Unknown'}: {str(e)}")
            return None

    @staticmethod
    def _nota_para_extenso(nota):
        """
        Converte nota numérica para extenso (português)
        """
        try:
            nomes = {
                0: 'Zero', 1: 'Um', 2: 'Dois', 3: 'Três', 4: 'Quatro', 5: 'Cinco',
                6: 'Seis', 7: 'Sete', 8: 'Oito', 9: 'Nove', 10: 'Dez',
                11: 'Onze', 12: 'Doze', 13: 'Treze', 14: 'Catorze', 15: 'Quinze',
                16: 'Dezasseis', 17: 'Dezassete', 18: 'Dezoito', 19: 'Dezanove', 20: 'Vinte'
            }
            inteiro = int(round(nota))
            return nomes.get(inteiro, str(inteiro))
        except Exception:
            return str(int(round(nota))) if nota else 'Zero'

    @staticmethod
    def get_notas_trimestre(aluno_id, trimestre, classe=None):
        """
        Obtém notas de um trimestre específico para um aluno
        """
        try:
            aluno = Aluno.objects.get(id_aluno=aluno_id)
            notas = Nota.objects.filter(
                id_aluno=aluno,
                trimestre__icontains=trimestre,
                valor__isnull=False
            ).select_related('id_disciplina')
            
            resultados = []
            for nota in notas:
                if nota.id_disciplina:
                    resultados.append({
                        'disciplina': nota.id_disciplina.nome,
                        'tipo_nota': nota.tipo_nota,
                        'valor': float(nota.valor),
                        'trimestre': nota.trimestre
                    })
                    
            return resultados
        except Exception as e:
            logger.error(f"Erro ao obter notas do trimestre {trimestre}: {str(e)}")
            return []

    @staticmethod
    def validar_dados_notas():
        """
        Valida a integridade dos dados de notas no sistema
        Retorna relatório de problemas
        """
        problemas = []
        
        try:
            # Verificar notas sem disciplina
            notas_sem_disciplina = Nota.objects.filter(id_disciplina__isnull=True).count()
            if notas_sem_disciplina > 0:
                problemas.append(f"{notas_sem_disciplina} notas sem disciplina")
            
            # Verificar notas sem tipo
            notas_sem_tipo = Nota.objects.filter(tipo_nota__isnull=True).count()
            if notas_sem_tipo > 0:
                problemas.append(f"{notas_sem_tipo} notas sem tipo definido")
            
            # Verificar notas sem trimestre
            notas_sem_trimestre = Nota.objects.filter(trimestre__isnull=True).count()
            if notas_sem_trimestre > 0:
                problemas.append(f"{notas_sem_trimestre} notas sem trimestre")
            
            # Verificar valores inválidos
            notas_invalidas = Nota.objects.filter(Q(valor__lt=0) | Q(valor__gt=20)).count()
            if notas_invalidas > 0:
                problemas.append(f"{notas_invalidas} notas com valores fora do intervalo (0-20)")
                
        except Exception as e:
            problemas.append(f"Erro na validação: {str(e)}")
            
        return problemas
