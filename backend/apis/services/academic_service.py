from django.db.models import Avg
from apis.models import Nota, FaltaAluno, Aluno

class AcademicService:
    """
    Serviço para gestão de notas, faltas e desempenho académico
    """
    
    @staticmethod
    def calcular_media_disciplina(aluno_id, disciplina_id):
        """
        Calcula a média de um aluno em uma disciplina específica
        """
        notas = Nota.objects.filter(id_aluno_id=aluno_id, id_disciplina_id=disciplina_id)
        if not notas.exists():
            return 0
            
        media = notas.aggregate(Avg('valor'))['valor__avg']
        return round(media, 2)

    @staticmethod
    def obter_resumo_academico(aluno_id):
        """
        Retorna um resumo completo do desempenho do aluno
        """
        aluno = Aluno.objects.get(id_aluno=aluno_id)
        notas = Nota.objects.filter(id_aluno=aluno)
        faltas = FaltaAluno.objects.filter(id_aluno=aluno).count()
        
        media_geral = notas.aggregate(Avg('valor'))['valor__avg'] or 0
        
        # Agrupar por disciplina
        disciplinas_stats = {}
        for nota in notas:
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
            'situacao': 'Aprovado' if media_geral >= 10 else 'Reprovado' # Lógica simplificada
        }

    @staticmethod
    def get_boletim_aluno(aluno, classe=None):
        """
        Calcula as notas detalhadas (MAC, PP, PT) e médias por trimestre.
        Retorna estrutura pronta para a Declaração de Aproveitamento e Boletim.
        """
        from apis.models import MatrizCurricularDisciplina, Nota, MatrizCurricular, Matricula

        # 1. Identificar a Curso e a Matriz Curricular
        matriz = None
        target_turma = None
        
        # LOGICA CORRIGIDA: Priorizar a CLASSE SOLICITADA se fornecida
        if classe:
            # Tentar encontrar histórico de turma para esta classe
            from apis.models import HistoricoTurmaAluno
            historico = HistoricoTurmaAluno.objects.filter(id_aluno=aluno, id_classe=classe).order_by('-data_inicio').first()
            
            if historico and historico.id_turma and historico.id_turma.id_matriz_curricular:
                matriz = historico.id_turma.id_matriz_curricular
                target_turma = historico.id_turma
            
            # Se não achou histórico, tentar buscar Matriz Ativa para Curso + Classe
            if not matriz and aluno.id_turma:
                curso = aluno.id_turma.id_curso # Assume curso atual
                matriz = MatrizCurricular.objects.filter(id_curso=curso, id_classe=classe, ativo=True).first()
                if not matriz:
                    matriz = MatrizCurricular.objects.filter(id_curso=curso, id_classe=classe).first()
        
        # Se ainda não temos matriz (ou classe não foi fornecida), usar a da turma atual
        if not matriz and aluno.id_turma and aluno.id_turma.id_matriz_curricular:
            matriz = aluno.id_turma.id_matriz_curricular
            target_turma = aluno.id_turma
            if not classe:
                classe = aluno.id_turma.id_classe

        # Fallback antigas logicas se ainda nao tiver matriz
        if not matriz:
            curso = None
            if aluno.id_turma:
                curso = aluno.id_turma.id_curso
                target_turma = aluno.id_turma # Tentativa de fixar turma atual
                if not classe:
                    classe = aluno.id_turma.id_classe
            
            if not curso or not classe:
                ultima_matricula = Matricula.objects.filter(id_aluno=aluno).select_related('id_turma__id_curso', 'id_turma__id_classe').order_by('-data_matricula').first()
                if ultima_matricula and ultima_matricula.id_turma:
                    curso = curso or ultima_matricula.id_turma.id_curso
                    classe = classe or ultima_matricula.id_turma.id_classe
                    target_turma = ultima_matricula.id_turma # Fixar turma da matricula
            
            if curso and classe:
                matriz = MatrizCurricular.objects.filter(id_curso=curso, id_classe=classe, ativo=True).first()
                if not matriz:
                    matriz = MatrizCurricular.objects.filter(id_curso=curso, id_classe=classe).first()

        if not matriz:
            # Fallback: Se não tem matriz, busca todas as disciplinas que o aluno tem nota
            query_filters = {'id_aluno': aluno}
            if target_turma:
                query_filters['id_turma'] = target_turma
                
            notas_aluno = Nota.objects.filter(**query_filters).select_related('id_disciplina')
            if not notas_aluno.exists():
                return []
                
            resultados = []
            disciplinas_processadas = set()
            
            # Agrupar notas por disciplina
            for nota in notas_aluno:
                disc = nota.id_disciplina
                if disc.id_disciplina in disciplinas_processadas:
                    continue
                    
                disciplinas_processadas.add(disc.id_disciplina)
                
                # Buscar todas as notas desta disciplina
                notas_disc = [n for n in notas_aluno if n.id_disciplina_id == disc.id_disciplina]
                
                # Estrutura por trimestre (None indica que não foi lançada)
                grades = {
                    '1': {'MAC': None, 'PP': None, 'PT': None, 'MT': None},
                    '2': {'MAC': None, 'PP': None, 'PT': None, 'MT': None},
                    '3': {'MAC': None, 'PP': None, 'PT': None, 'MT': None}
                }
                
                teve_nota = {'1': False, '2': False, '3': False}

                for n in notas_disc:
                    # Normalizar trimestre (Ex: "1º Trimestre" -> "1", "1" -> "1")
                    t_raw = str(n.trimestre) if n.trimestre else ''
                    t_key = t_raw.split('º')[0].strip() if 'º' in t_raw else t_raw.strip()
                    
                    if t_key in grades and n.tipo_nota in grades[t_key]:
                        grades[t_key][n.tipo_nota] = float(n.valor)
                        teve_nota[t_key] = True

                # Calcular Médias Trimestrais (MT = (MAC + PP + PT) / 3)
                for t in grades:
                    g = grades[t]
                    if teve_nota[t]:
                        # Consideramos 0 para notas não lançadas se o trimestre teve algum lançamento
                        v_mac = g['MAC'] if g['MAC'] is not None else 0.0
                        v_pp = g['PP'] if g['PP'] is not None else 0.0
                        v_pt = g['PT'] if g['PT'] is not None else 0.0
                        
                        mt = (v_mac + v_pp + v_pt) / 3
                        g['MT'] = round(mt, 1)

                # Média Final
                soma_mt = sum(grades[t]['MT'] for t in grades if grades[t]['MT'] is not None)
                count_mt = sum(1 for t in grades if grades[t]['MT'] is not None)
                
                if count_mt > 0:
                    media_final = soma_mt / count_mt
                else:
                    media_final = 0.0

                def nota_para_extenso(n):
                    nomes = {
                        0: 'Zero', 1: 'Um', 2: 'Dois', 3: 'Três', 4: 'Quatro', 5: 'Cinco',
                        6: 'Seis', 7: 'Sete', 8: 'Oito', 9: 'Nove', 10: 'Dez',
                        11: 'Onze', 12: 'Doze', 13: 'Treze', 14: 'Catorze', 15: 'Quinze',
                        16: 'Dezasseis', 17: 'Dezassete', 18: 'Dezoito', 19: 'Dezanove', 20: 'Vinte'
                    }
                    inteiro = int(round(n))
                    return nomes.get(inteiro, str(inteiro))

                status_disciplina = '---'
                if count_mt == 3:
                    status_disciplina = 'Aprovado' if round(media_final) >= 10 else 'Reprovado'

                resultados.append({
                    'id_disciplina': disc.id_disciplina,
                    'disciplina': disc.nome,
                    'coeficiente': 1.0, # Default já que não temos matriz
                    'trimestres': grades,
                    'media_final': f"{media_final:.1f}",
                    'media_final_valor': media_final,
                    'media_final_extenso': nota_para_extenso(media_final),
                    'resultado': status_disciplina,
                    'count_mt': count_mt
                })
            
            return resultados

        disciplinas_matriz = MatrizCurricularDisciplina.objects.filter(
            id_matriz_curricular=matriz
        ).select_related('id_disciplina')

        resultados = []
        
        for m_disc in disciplinas_matriz:
            # CORRECAO: Filtrar notas pela turma alvo (Histórica ou Atual)
            if target_turma:
                notas_disc = Nota.objects.filter(id_aluno=aluno, id_disciplina=m_disc.id_disciplina, id_turma=target_turma)
            else:
                notas_disc = Nota.objects.filter(id_aluno=aluno, id_disciplina=m_disc.id_disciplina)
            
            # Estrutura por trimestre (None indica que não foi lançada)
            grades = {
                '1': {'MAC': None, 'PP': None, 'PT': None, 'MT': None},
                '2': {'MAC': None, 'PP': None, 'PT': None, 'MT': None},
                '3': {'MAC': None, 'PP': None, 'PT': None, 'MT': None}
            }
            
            teve_nota = {'1': False, '2': False, '3': False}

            for n in notas_disc:
                # Normalizar trimestre (Ex: "1º Trimestre" -> "1", "1" -> "1")
                t_raw = str(n.trimestre) if n.trimestre else ''
                t_key = t_raw.split('º')[0].strip() if 'º' in t_raw else t_raw.strip()
                
                if t_key in grades and n.tipo_nota in grades[t_key]:
                    grades[t_key][n.tipo_nota] = float(n.valor)
                    teve_nota[t_key] = True

            # Calcular Médias Trimestrais (MT = (MAC + PP + PT) / 3)
            for t in grades:
                g = grades[t]
                if teve_nota[t]:
                    # Consideramos 0 para notas não lançadas se o trimestre teve algum lançamento
                    v_mac = g['MAC'] if g['MAC'] is not None else 0.0
                    v_pp = g['PP'] if g['PP'] is not None else 0.0
                    v_pt = g['PT'] if g['PT'] is not None else 0.0
                    
                    mt = (v_mac + v_pp + v_pt) / 3
                    g['MT'] = round(mt, 1)

            # Média Final
            soma_mt = sum(grades[t]['MT'] for t in grades if grades[t]['MT'] is not None)
            count_mt = sum(1 for t in grades if grades[t]['MT'] is not None)
            
            if count_mt > 0:
                media_final = soma_mt / count_mt
            else:
                media_final = 0.0

            def nota_para_extenso(n):
                nomes = {
                    0: 'Zero', 1: 'Um', 2: 'Dois', 3: 'Três', 4: 'Quatro', 5: 'Cinco',
                    6: 'Seis', 7: 'Sete', 8: 'Oito', 9: 'Nove', 10: 'Dez',
                    11: 'Onze', 12: 'Doze', 13: 'Treze', 14: 'Catorze', 15: 'Quinze',
                    16: 'Dezasseis', 17: 'Dezassete', 18: 'Dezoito', 19: 'Dezanove', 20: 'Vinte'
                }
                inteiro = int(round(n))
                return nomes.get(inteiro, str(inteiro))

            status_disciplina = '---'
            if count_mt == 3:
                status_disciplina = 'Aprovado' if round(media_final) >= 10 else 'Reprovado'

            resultados.append({
                'id_disciplina': m_disc.id_disciplina.id_disciplina,
                'disciplina': m_disc.id_disciplina.nome,
                'coeficiente': float(m_disc.coeficiente),
                'trimestres': grades,
                'media_final': f"{media_final:.1f}",
                'media_final_valor': media_final,
                'media_final_extenso': nota_para_extenso(media_final),
                'resultado': status_disciplina,
                'count_mt': count_mt
            })

        return resultados

    @staticmethod
    def get_historico_certificado_tecnico(aluno):
        """
        Consolida o histórico académico completo do aluno (10ª à 13ª) para gerar o Certificado Técnico.
        
        Retorna um dicionário com:
          - componentes: [{component_name, disciplinas: [{disc, media_final, extenso}]}]
          - pc: Classificação Final do Plano Curricular (média de todas as disciplinas 10-12)
          - ec: Nota do Estágio Curricular (13ª classe)
          - pap: Nota da Prova de Aptidão Profissional (13ª classe)
          - cfc: (4*PC + PAP + EC) / 6
          - cfc_extenso: por extenso
        """
        from apis.models import HistoricoTurmaAluno, Nota, MatrizCurricularDisciplina

        # --- Utilitário: Nota por extenso ---
        def nota_para_extenso(n):
            nomes = {
                0: 'Zero', 1: 'Um', 2: 'Dois', 3: 'Três', 4: 'Quatro', 5: 'Cinco',
                6: 'Seis', 7: 'Sete', 8: 'Oito', 9: 'Nove', 10: 'Dez',
                11: 'Onze', 12: 'Doze', 13: 'Treze', 14: 'Catorze', 15: 'Quinze',
                16: 'Dezasseis', 17: 'Dezassete', 18: 'Dezoito', 19: 'Dezanove', 20: 'Vinte'
            }
            inteiro = int(round(n))
            return nomes.get(inteiro, str(inteiro)) + ' valores'

        # --- Utilitário: Calcular média final de uma disciplina numa turma ---
        def calcular_media_anual(aluno, disciplina_id, turma):
            """Calcula a média anual de uma disciplina via médias trimestrais."""
            notas_disc = Nota.objects.filter(
                id_aluno=aluno,
                id_disciplina_id=disciplina_id,
                id_turma=turma
            )
            grades = {'1': {}, '2': {}, '3': {}}
            teve_nota = {'1': False, '2': False, '3': False}

            for n in notas_disc:
                t_raw = str(n.trimestre) if n.trimestre else ''
                t_key = t_raw.split('º')[0].strip() if 'º' in t_raw else t_raw.strip()
                if t_key in grades and n.tipo_nota:
                    grades[t_key][n.tipo_nota] = float(n.valor)
                    teve_nota[t_key] = True

            mts = []
            for t in grades:
                if teve_nota[t]:
                    mac = grades[t].get('MAC', 0.0)
                    pp  = grades[t].get('PP', 0.0)
                    pt  = grades[t].get('PT', 0.0)
                    mts.append((mac + pp + pt) / 3)

            return round(sum(mts) / len(mts), 1) if mts else None

        # --- 1. Recolher histórico 10ª, 11ª, 12ª (Médias plurianuais por disciplina) ---
        historico_pc = HistoricoTurmaAluno.objects.filter(
            id_aluno=aluno,
            id_classe__nivel__in=[10, 11, 12]
        ).select_related('id_turma', 'id_turma__id_matriz_curricular', 'id_classe').order_by('id_classe__nivel')

        # dicionário: {disc_id: {name, componente, medias_anuais: []}}
        disciplinas_map = {}

        for hist in historico_pc:
            turma = hist.id_turma
            if not turma:
                continue

            # Obter disciplinas via Matriz Curricular da turma
            mcd_qs = None
            if turma.id_matriz_curricular:
                mcd_qs = MatrizCurricularDisciplina.objects.filter(
                    id_matriz_curricular=turma.id_matriz_curricular
                ).select_related('id_disciplina', 'id_disciplina__id_tipo_disciplina')
            
            if not mcd_qs:
                # Fallback: disciplinas com notas nessa turma
                notas_turma = Nota.objects.filter(id_aluno=aluno, id_turma=turma).select_related('id_disciplina__id_tipo_disciplina')
                proc = set()
                for n in notas_turma:
                    disc = n.id_disciplina
                    if disc and disc.id_disciplina not in proc:
                        proc.add(disc.id_disciplina)
                        media = calcular_media_anual(aluno, disc.id_disciplina, turma)
                        if media is not None:
                            if disc.id_disciplina not in disciplinas_map:
                                tipo_nome = disc.id_tipo_disciplina.nome_tipo if disc.id_tipo_disciplina else 'COMPONENTE TÉCNICA, TECNOLÓGICA E PRÁTICA'
                                disciplinas_map[disc.id_disciplina] = {
                                    'nome': disc.nome,
                                    'componente': tipo_nome.upper(),
                                    'medias_anuais': []
                                }
                            disciplinas_map[disc.id_disciplina]['medias_anuais'].append(media)
                continue

            for mcd in mcd_qs:
                disc = mcd.id_disciplina
                media = calcular_media_anual(aluno, disc.id_disciplina, turma)
                if media is not None:
                    if disc.id_disciplina not in disciplinas_map:
                        tipo_nome = disc.id_tipo_disciplina.nome_tipo if disc.id_tipo_disciplina else 'COMPONENTE TÉCNICA, TECNOLÓGICA E PRÁTICA'
                        disciplinas_map[disc.id_disciplina] = {
                            'nome': disc.nome,
                            'componente': tipo_nome.upper(),
                            'medias_anuais': []
                        }
                    disciplinas_map[disc.id_disciplina]['medias_anuais'].append(media)

        # --- 2. Calcular média plurianual e PC ---
        todas_medias_pc = []
        disciplinas_final = {}
        for disc_id, info in disciplinas_map.items():
            media_plurianual = round(sum(info['medias_anuais']) / len(info['medias_anuais']), 1) if info['medias_anuais'] else 0.0
            disciplinas_final[disc_id] = {
                'nome': info['nome'],
                'componente': info['componente'],
                'media_final': media_plurianual,
                'media_final_extenso': nota_para_extenso(media_plurianual),
            }
            todas_medias_pc.append(media_plurianual)

        pc = round(sum(todas_medias_pc) / len(todas_medias_pc), 1) if todas_medias_pc else 0.0

        # --- 3. Dados da 13ª Classe (EC e PAP) ---
        hist_13 = HistoricoTurmaAluno.objects.filter(
            id_aluno=aluno,
            id_classe__nivel=13
        ).select_related('id_turma').order_by('-data_inicio').first()

        ec_valor = 0.0
        pap_valor = 0.0
        disciplinas_13 = []

        if hist_13 and hist_13.id_turma:
            turma_13 = hist_13.id_turma
            notas_13 = Nota.objects.filter(id_aluno=aluno, id_turma=turma_13).select_related('id_disciplina')
            
            proc_13 = {}
            for n in notas_13:
                disc = n.id_disciplina
                if disc:
                    if disc.id_disciplina not in proc_13:
                        proc_13[disc.id_disciplina] = {'nome': disc.nome, 'valor': float(n.valor)}
                    else:
                        # Atualizar com a nota mais recente
                        proc_13[disc.id_disciplina]['valor'] = float(n.valor)

            for disc_id, info in proc_13.items():
                nome_upper = info['nome'].upper()
                # Identificar EC e PAP por palavras-chave
                if 'ESTÁGIO' in nome_upper or 'ESTAGIO' in nome_upper:
                    ec_valor = info['valor']
                elif 'PAP' in nome_upper or 'APTIDÃO' in nome_upper or 'APTIDAO' in nome_upper:
                    pap_valor = info['valor']
                else:
                    disciplinas_13.append({'nome': info['nome'], 'valor': info['valor']})

        # --- 4. Calcular CFC ---
        cfc = round((4 * pc + pap_valor + ec_valor) / 6, 1)

        # --- 5. Agrupar disciplinas por componente ---
        componentes_agrupados = {}
        for disc_id, info in disciplinas_final.items():
            comp = info['componente']
            if comp not in componentes_agrupados:
                componentes_agrupados[comp] = []
            componentes_agrupados[comp].append({
                'nome': info['nome'],
                'media_final': info['media_final'],
                'media_final_extenso': info['media_final_extenso'],
            })

        # Ordenar componentes por prioridade
        ordem_componentes = [
            'COMPONENTE SOCIOCULTURAL',
            'COMPONENTE CIENTÍFICA',
            'COMPONENTE TÉCNICA, TECNOLÓGICA E PRÁTICA',
        ]
        componentes_list = []
        for comp in ordem_componentes:
            if comp in componentes_agrupados:
                componentes_list.append({'nome': comp, 'disciplinas': componentes_agrupados[comp]})
        # Componentes não reconhecidos
        for comp, discs in componentes_agrupados.items():
            if comp not in ordem_componentes:
                componentes_list.append({'nome': comp, 'disciplinas': discs})

        return {
            'componentes': componentes_list,
            'pc': pc,
            'pc_extenso': nota_para_extenso(pc),
            'ec': ec_valor,
            'ec_extenso': nota_para_extenso(ec_valor),
            'pap': pap_valor,
            'pap_extenso': nota_para_extenso(pap_valor),
            'cfc': cfc,
            'cfc_extenso': nota_para_extenso(cfc),
            'disciplinas_13': disciplinas_13,
        }
