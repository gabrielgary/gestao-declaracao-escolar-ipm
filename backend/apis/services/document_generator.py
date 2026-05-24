"""
Módulo de Geração de Documentos Escolares
Funções especializadas para cada tipo de documento
"""

def gerar_boletim(aluno_id, trimestre=None, classe=None):
    """
    Gera boletim de notas com disciplinas, médias e faltas
    
    Args:
        aluno_id: ID do aluno
        trimestre: Número do trimestre (1, 2, 3) ou None para todos
        classe: Classe específica ou None para usar a do aluno
    
    Returns:
        dict: Dados estruturados para o template do boletim
    """
    from apis.models import Aluno, Nota, Disciplina
    from django.db.models import Avg
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # 1. Buscar dados do aluno
        aluno = Aluno.objects.select_related(
            'id_turma', 
            'id_turma__id_classe', 
            'id_turma__id_curso'
        ).get(id_aluno=aluno_id)
        
        # 2. Determinar qual trimestre gerar
        if trimestre:
            trimestres = [str(trimestre)]
        else:
            trimestres = ['1', '2', '3']
        
        # 3. Buscar notas do aluno
        notas_query = Nota.objects.filter(
            id_aluno=aluno,
            valor__isnull=False
        ).select_related('id_disciplina')
        
        # Filtrar por trimestre se especificado
        if trimestre:
            notas_query = notas_query.filter(trimestre__icontains=str(trimestre))
        
        # 4. Estruturar dados por disciplina e trimestre
        dados_boletim = {
            'aluno': aluno,
            'trimestre_selecionado': str(trimestre) if trimestre else 'Todos',
            'classe': classe or (aluno.id_turma.id_classe if aluno.id_turma else None),
            'curso': aluno.id_turma.id_curso if aluno.id_turma else None,
            'notas_finais': []
        }
        
        # 5. Processar cada disciplina
        disciplinas_processadas = set()
        
        for nota in notas_query:
            if nota.id_disciplina and nota.id_disciplina.id_disciplina not in disciplinas_processadas:
                disciplinas_processadas.add(nota.id_disciplina.id_disciplina)
                
                # Buscar todas as notas desta disciplina
                notas_disciplina = notas_query.filter(id_disciplina=nota.id_disciplina)
                
                # Estruturar notas por trimestre
                dados_disciplina = {
                    'disciplina': nota.id_disciplina.nome,
                    'trimestres': {}
                }
                
                for trim in trimestres:
                    # Buscar notas MAC, NPP, NPT deste trimestre
                    mac = notas_disciplina.filter(tipo_nota='MAC', trimestre__icontains=trim).first()
                    npp = notas_disciplina.filter(tipo_nota='PP', trimestre__icontains=trim).first()
                    npt = notas_disciplina.filter(tipo_nota='PT', trimestre__icontains=trim).first()
                    
                    # Calcular CT (Classificação Trimestral)
                    valores = []
                    if mac and mac.valor is not None:
                        valores.append(float(mac.valor))
                    if npp and npp.valor is not None:
                        valores.append(float(npp.valor))
                    if npt and npt.valor is not None:
                        valores.append(float(npt.valor))
                    
                    ct = round(sum(valores) / len(valores), 1) if valores else None
                    
                    dados_disciplina['trimestres'][trim] = {
                        'MAC': mac.valor if mac else None,
                        'NPP': npp.valor if npp else None,
                        'NPT': npt.valor if npt else None,
                        f'CT{trim}': ct
                    }
                
                dados_boletim['notas_finais'].append(dados_disciplina)
        
        logger.info(f"Boletim gerado para {aluno.nome_completo} - {len(dados_boletim['notas_finais'])} disciplinas")
        
        return dados_boletim
        
    except Aluno.DoesNotExist:
        logger.error(f"Aluno {aluno_id} não encontrado")
        raise ValueError(f"Aluno {aluno_id} não encontrado")
    except Exception as e:
        logger.error(f"Erro ao gerar boletim: {str(e)}")
        raise ValueError(f"Erro ao gerar boletim: {str(e)}")

def gerar_certificado(aluno_id):
    """
    Gera certificado de conclusão de curso com médias finais de todas as disciplinas
    
    Args:
        aluno_id: ID do aluno
    
    Returns:
        dict: Dados estruturados para o template do certificado
    """
    from apis.models import Aluno, Nota, Disciplina, MatrizCurricularDisciplina, MatrizCurricular
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # 1. Buscar dados do aluno
        aluno = Aluno.objects.select_related(
            'id_turma', 
            'id_turma__id_classe', 
            'id_turma__id_curso',
            'id_turma__id_matriz_curricular'
        ).get(id_aluno=aluno_id)
        
        # 2. Validar se o aluno pode receber certificado (deve estar na última classe)
        if not aluno.id_turma or not aluno.id_turma.id_classe:
            raise ValueError("Aluno não possui turma/classe associada")
        
        classe_aluno = aluno.id_turma.id_classe
        if classe_aluno.nivel not in [12, 13]:  # Últimas classes do ensino médio
            raise ValueError(f"Aluno na {classe_aluno.nivel}ª classe não pode receber certificado")
        
        # 3. Buscar todas as notas do aluno (todo o percurso escolar)
        notas_query = Nota.objects.filter(
            id_aluno=aluno,
            valor__isnull=False
        ).select_related('id_disciplina', 'id_turma__id_classe')
        
        # 4. Estruturar dados do certificado
        dados_certificado = {
            'aluno': aluno,
            'curso': aluno.id_turma.id_curso if aluno.id_turma else None,
            'ano_letivo': '2024/2025',  # Pode ser dinâmico
            'data_emissao': '16 de Junho de 2025',  # Pode ser dinâmico
            'componentes': {
                'sociocultural': [],
                'cientifica': [],
                'tecnica': []
            },
            'classificacoes_finais': {
                'pc': 0,  # Plano Curricular
                'ec': 0,  # Estágio Curricular  
                'pap': 0,  # Prova de Aptidão Profissional
                'final': 0  # Classificação Final do Curso
            }
        }
        
        # 5. Processar todas as disciplinas do percurso do aluno
        disciplinas_processadas = {}
        
        for nota in notas_query:
            if nota.id_disciplina and nota.id_disciplina.id_disciplina not in disciplinas_processadas:
                disciplinas_processadas[nota.id_disciplina.id_disciplina] = nota.id_disciplina
                
                # Calcular média anual de TODOS os trimestres de TODAS as classes
                media_anual = _calcular_media_anual_completa_disciplina(
                    nota.id_disciplina, 
                    notas_query.filter(id_disciplina=nota.id_disciplina)
                )
                
                if media_anual:
                    # Classificar a disciplina por componente (baseado no nome ou categoria)
                    componente = _classificar_componente_disciplina(nota.id_disciplina.nome)
                    
                    dados_disciplina = {
                        'disciplina': nota.id_disciplina.nome,
                        'media_final': round(media_anual, 0),  # Nota final arredondada
                        'media_extenso': _nota_para_extenso(media_anual)
                    }
                    
                    dados_certificado['componentes'][componente].append(dados_disciplina)
        
        # 6. Calcular médias das componentes
        todas_medias = []
        for componente, disciplinas in dados_certificado['componentes'].items():
            if disciplinas:
                media_componente = sum(d['media_final'] for d in disciplinas) / len(disciplinas)
                todas_medias.extend([d['media_final'] for d in disciplinas])
        
        # 7. Calcular PC (Plano Curricular) - média de todas as disciplinas
        if todas_medias:
            dados_certificado['classificacoes_finais']['pc'] = round(sum(todas_medias) / len(todas_medias))
        
        # 8. Simular EC e PAP (estes dados devem vir de outras fontes)
        # Por enquanto, vamos usar valores padrão ou buscar de modelos específicos
        dados_certificado['classificacoes_finais']['ec'] = 16  # Exemplo
        dados_certificado['classificacoes_finais']['pap'] = 18  # Exemplo
        
        # 9. Calcular classificação final: (4×PC + PAP + EC) ÷ 6
        pc = dados_certificado['classificacoes_finais']['pc']
        ec = dados_certificado['classificacoes_finais']['ec']
        pap = dados_certificado['classificacoes_finais']['pap']
        
        classificacao_final = round((4 * pc + pap + ec) / 6)
        dados_certificado['classificacoes_finais']['final'] = classificacao_final
        dados_certificado['classificacoes_finais']['final_extenso'] = _nota_para_extenso(classificacao_final)
        
        logger.info(f"Certificado gerado para {aluno.nome_completo} - Classificação final: {classificacao_final}")
        
        return dados_certificado
        
    except Aluno.DoesNotExist:
        logger.error(f"Aluno {aluno_id} não encontrado")
        raise ValueError(f"Aluno {aluno_id} não encontrado")
    except Exception as e:
        logger.error(f"Erro ao gerar certificado: {str(e)}")
        raise ValueError(f"Erro ao gerar certificado: {str(e)}")

def _calcular_media_anual_completa_disciplina(disciplina, notas_disciplina):
    """
    Calcula a média anual completa de uma disciplina considerando todos os trimestres de todas as classes
    """
    try:
        if not disciplina:
            return None
        
        # Agrupar notas por trimestre e calcular CT para cada um
        ct_valores = []
        
        for trimestre_num in ['1', '2', '3']:
            # Buscar notas MAC, NPP, NPT deste trimestre
            mac = notas_disciplina.filter(tipo_nota='MAC', trimestre__icontains=trimestre_num).first()
            npp = notas_disciplina.filter(tipo_nota='PP', trimestre__icontains=trimestre_num).first()
            npt = notas_disciplina.filter(tipo_nota='PT', trimestre__icontains=trimestre_num).first()
            
            # Calcular CT do trimestre
            valores_trimestre = []
            if mac and mac.valor is not None:
                valores_trimestre.append(float(mac.valor))
            if npp and npp.valor is not None:
                valores_trimestre.append(float(npp.valor))
            if npt and npt.valor is not None:
                valores_trimestre.append(float(npt.valor))
            
            if valores_trimestre:
                ct_trimestre = sum(valores_trimestre) / len(valores_trimestre)
                ct_valores.append(ct_trimestre)
        
        # Calcular média anual (CT1 + CT2 + CT3) / 3
        if ct_valores:
            media_anual = sum(ct_valores) / len(ct_valores)
        else:
            media_anual = 0.0
        
        return media_anual
        
    except Exception as e:
        logging.getLogger(__name__).error(f"Erro ao calcular média completa da disciplina {disciplina.nome}: {str(e)}")
        return None

def _classificar_componente_disciplina(nome_disciplina):
    """
    Classifica a disciplina em um dos três componentes de formação
    """
    nome_lower = nome_disciplina.lower()
    
    # Componente Sociocultural
    sociocultural = ['portuguesa', 'inglesa', 'francesa', 'educação física', 'formação de atitudes', 'filosofia', 'história', 'geografia']
    if any(soc in nome_lower for soc in sociocultural):
        return 'sociocultural'
    
    # Componente Científica
    cientifica = ['matemática', 'economia', 'direito', 'sociologia', 'informática', 'estatística', 'química', 'física', 'biologia']
    if any(cient in nome_lower for cient in cientifica):
        return 'cientifica'
    
    # Componente Técnica (padrão)
    return 'tecnica'

def gerar_declaracao_com_notas(aluno_id, classe=None):
    """
    Gera declaração de aproveitamento com médias anuais por disciplina
    
    Args:
        aluno_id: ID do aluno
        classe: Classe específica ou None para usar a do aluno
    
    Returns:
        dict: Dados estruturados para o template da declaração
    """
    from apis.models import Aluno, Nota, Disciplina, MatrizCurricularDisciplina, MatrizCurricular
    from django.db.models import Avg
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # 1. Buscar dados do aluno
        aluno = Aluno.objects.select_related(
            'id_turma', 
            'id_turma__id_classe', 
            'id_turma__id_curso',
            'id_turma__id_matriz_curricular'
        ).get(id_aluno=aluno_id)
        
        # 2. Determinar a classe
        classe_alvo = classe or (aluno.id_turma.id_classe if aluno.id_turma else None)
        
        if not classe_alvo:
            raise ValueError("Aluno não possui classe associada")
        
        # 3. Buscar matriz curricular da classe
        matriz = None
        if aluno.id_turma and aluno.id_turma.id_matriz_curricular:
            matriz = aluno.id_turma.id_matriz_curricular
        elif aluno.id_turma and aluno.id_turma.id_curso:
            matriz = MatrizCurricular.objects.filter(
                id_curso=aluno.id_turma.id_curso,
                id_classe=classe_alvo,
                ativo=True
            ).first()
        
        # 4. Buscar todas as notas do aluno (ano letivo completo)
        notas_query = Nota.objects.filter(
            id_aluno=aluno,
            valor__isnull=False
        ).select_related('id_disciplina')
        
        # Se tiver turma, filtrar por turma
        if aluno.id_turma:
            notas_query = notas_query.filter(id_turma=aluno.id_turma)
        
        # 5. Estruturar dados da declaração
        dados_declaracao = {
            'aluno': aluno,
            'classe': classe_alvo,
            'curso': aluno.id_turma.id_curso if aluno.id_turma else None,
            'ano_letivo': '2024',  # Pode ser dinâmico
            'disciplinas': []
        }
        
        # 6. Processar disciplinas
        if matriz:
            # Usar disciplinas da matriz curricular
            disciplinas_matriz = MatrizCurricularDisciplina.objects.filter(
                id_matriz_curricular=matriz
            ).select_related('id_disciplina')
            
            for m_disc in disciplinas_matriz:
                resultado_disciplina = _calcular_media_anual_disciplina(
                    m_disc.id_disciplina, 
                    notas_query.filter(id_disciplina=m_disc.id_disciplina),
                    float(m_disc.coeficiente)
                )
                if resultado_disciplina:
                    dados_declaracao['disciplinas'].append(resultado_disciplina)
        else:
            # Fallback: usar disciplinas das notas do aluno
            disciplinas_unicas = {}
            for nota in notas_query:
                if nota.id_disciplina:
                    disc_id = nota.id_disciplina.id_disciplina
                    if disc_id not in disciplinas_unicas:
                        disciplinas_unicas[disc_id] = nota.id_disciplina
            
            for disciplina in disciplinas_unicas.values():
                resultado_disciplina = _calcular_media_anual_disciplina(
                    disciplina, 
                    notas_query.filter(id_disciplina=disciplina),
                    1.0
                )
                if resultado_disciplina:
                    dados_declaracao['disciplinas'].append(resultado_disciplina)
        
        # 7. Calcular média geral anual
        if dados_declaracao['disciplinas']:
            soma_medias = sum(d['media_anual_valor'] for d in dados_declaracao['disciplinas'])
            media_geral = soma_medias / len(dados_declaracao['disciplinas'])
            dados_declaracao['media_geral'] = round(media_geral, 1)
            dados_declaracao['media_geral_extenso'] = _nota_para_extenso(media_geral)
        else:
            dados_declaracao['media_geral'] = 0
            dados_declaracao['media_geral_extenso'] = 'Zero'
        
        logger.info(f"Declaração gerada para {aluno.nome_completo} - {len(dados_declaracao['disciplinas'])} disciplinas")
        
        return dados_declaracao
        
    except Aluno.DoesNotExist:
        logger.error(f"Aluno {aluno_id} não encontrado")
        raise ValueError(f"Aluno {aluno_id} não encontrado")
    except Exception as e:
        logger.error(f"Erro ao gerar declaração com notas: {str(e)}")
        raise ValueError(f"Erro ao gerar declaração com notas: {str(e)}")

def _calcular_media_anual_disciplina(disciplina, notas_disciplina, coeficiente=1.0):
    """
    Calcula a média anual de uma disciplina: (CT1 + CT2 + CT3) / 3
    """
    try:
        if not disciplina:
            return None
        
        # Calcular CT para cada trimestre
        ct_valores = []
        
        for trimestre_num in ['1', '2', '3']:
            # Buscar notas MAC, NPP, NPT deste trimestre
            mac = notas_disciplina.filter(tipo_nota='MAC', trimestre__icontains=trimestre_num).first()
            npp = notas_disciplina.filter(tipo_nota='PP', trimestre__icontains=trimestre_num).first()
            npt = notas_disciplina.filter(tipo_nota='PT', trimestre__icontains=trimestre_num).first()
            
            # Calcular CT do trimestre
            valores_trimestre = []
            if mac and mac.valor is not None:
                valores_trimestre.append(float(mac.valor))
            if npp and npp.valor is not None:
                valores_trimestre.append(float(npp.valor))
            if npt and npt.valor is not None:
                valores_trimestre.append(float(npt.valor))
            
            if valores_trimestre:
                ct_trimestre = sum(valores_trimestre) / len(valores_trimestre)
                ct_valores.append(ct_trimestre)
        
        # Calcular média anual (CT1 + CT2 + CT3) / 3
        if ct_valores:
            media_anual = sum(ct_valores) / len(ct_valores)
        else:
            media_anual = 0.0
        
        return {
            'disciplina': disciplina.nome,
            'coeficiente': coeficiente,
            'ct1': ct_valores[0] if len(ct_valores) > 0 else None,
            'ct2': ct_valores[1] if len(ct_valores) > 1 else None,
            'ct3': ct_valores[2] if len(ct_valores) > 2 else None,
            'media_anual': round(media_anual, 1),
            'media_anual_valor': media_anual,
            'media_anual_extenso': _nota_para_extenso(media_anual),
            'resultado': 'Aprovado' if round(media_anual) >= 10 else 'Reprovado'
        }
        
    except Exception as e:
        logging.getLogger(__name__).error(f"Erro ao calcular média anual da disciplina {disciplina.nome}: {str(e)}")
        return None

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

def gerar_declaracao_sem_notas(aluno_id, efeito=""):
    """
    Gera declaração simples (matrícula, frequência, etc.) sem notas
    
    Args:
        aluno_id: ID do aluno
        efeito: Propósito da declaração (ex: Passaporte, Emprego)
    
    Returns:
        dict: Dados estruturados para o template da declaração simples
    """
    from apis.models import Aluno, FaltaAluno
    from django.utils import timezone
    import logging
    
    logger = logging.getLogger(__name__)
    hoje = timezone.now()
    
    try:
        # 1. Buscar dados do aluno
        aluno = Aluno.objects.select_related(
            'id_turma', 
            'id_turma__id_classe', 
            'id_turma__id_curso',
            'id_turma__id_curso__id_area_formacao'
        ).get(id_aluno=aluno_id)
        
        # 2. Validar se o aluno tem turma associada
        if not aluno.id_turma:
            raise ValueError("Aluno não possui turma associada")
        
        # 3. Lógica de Status Temporal (Frequenta vs Frequentou)
        # Se a turma for do ano actual, usa "Frequenta"
        ano_atual = hoje.year
        ano_turma = aluno.id_turma.ano_letivo or aluno.id_turma.ano or str(ano_atual)
        
        status_temporal = "Frequenta"
        if str(ano_atual) not in str(ano_turma):
            status_temporal = "Frequentou"
            
        # 4. Estruturar dados da declaração
        dados_declaracao = {
            'aluno': aluno,
            'turma': aluno.id_turma,
            'classe': aluno.id_turma.id_classe,
            'curso': aluno.id_turma.id_curso,
            'ano_letivo': ano_turma,
            'efeito': efeito,
            'status_temporal': status_temporal,
            'data_emissao': hoje.strftime('%d/%m/%Y'),
            'hoje': hoje,
            'tipo_declaracao': f'Declaração para fins de {efeito}' if efeito else 'Declaração de Frequência'
        }
        
        # 5. Buscar informações adicionais (faltas, etc.) - Usando o ano da sala
        # Extrair o primeiro ano se for "2024/2025"
        ano_busca = ano_turma.split('/')[0] if '/' in str(ano_turma) else ano_turma
        
        try:
            faltas_ano = FaltaAluno.objects.filter(
                id_aluno=aluno,
                data_falta__year=int(ano_busca)
            ).count()
        except (ValueError, TypeError):
            faltas_ano = 0
        
        dados_declaracao['total_faltas'] = faltas_ano
        
        logger.info(f"Declaração sem notas gerada para {aluno.nome_completo} - {aluno.id_turma.codigo_turma} ({status_temporal})")
        
        return dados_declaracao
        
    except Aluno.DoesNotExist:
        logger.error(f"Aluno {aluno_id} não encontrado")
        raise ValueError(f"Aluno {aluno_id} não encontrado")
    except Exception as e:
        logger.error(f"Erro ao gerar declaração sem notas: {str(e)}")
        raise ValueError(f"Erro ao gerar declaração sem notas: {str(e)}")
