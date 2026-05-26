from langchain.tools import tool
from fpdf import FPDF
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DJANGO_API_URL = os.getenv("DJANGO_BACKEND_URL", "http://localhost:8000")

class PDF(FPDF):
    def header(self):
        try:
            self.set_font('Arial', 'B', 15)
        except:
            self.set_font('Helvetica', 'B', 15)
        self.cell(0, 10, 'SISTEMA DE GESTAO ESCOLAR - DECLARACAO OFICIAL', 0, 1, 'C')
        self.ln(10)

@tool
def generate_declaration_pdf(matricula: str) -> str:
    """
    Gera um arquivo PDF de declaração para um aluno usando o número de matrícula.
    Retorna o caminho do arquivo gerado.
    """
    try:
        # 1. Buscar dados reais do aluno
        url = f"{DJANGO_API_URL}/api/v1/alunos/?search={matricula}"
        response = requests.get(url)
        
        if response.status_code != 200:
            return f"Erro ao acessar o sistema escolar para obter dados do aluno {matricula}."
            
        data = response.json()
        if data['count'] == 0:
            return f"Aluno com matricula {matricula} nao encontrado para emissao de documento."
            
        aluno = data['results'][0]
        nome = aluno['nome_completo']
        curso = aluno.get('id_turma_codigo', 'Curso Geral')
        # Algumas APIs podem não ter o 'ano', vamos usar um default ou extrair da turma
        ano = "atual" 
        
        # 2. Gerar o PDF
        pdf = PDF()
        pdf.add_page()
        try:
            pdf.set_font('Arial', '', 12)
        except:
            pdf.set_font('Helvetica', '', 12)
        
        texto = f"""
        Declaramos para os devidos efeitos que o(a) aluno(a) {nome}, 
        regularmente matriculado(a) sob o numero {matricula}, no curso de {curso}, 
        frequenta atualmente o estabelecimento de ensino neste ano lectivo.
        
        A presente declaracao e emitida por solicitacao do interessado aos {datetime.now().strftime('%d/%m/%Y')}.
        """
        
        pdf.multi_cell(0, 10, texto)
        
        output_dir = "yasmin_output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        filename = f"{output_dir}/declaracao_{matricula}.pdf"
        pdf.output(filename)
        
        return f"Documento gerado com sucesso: {filename}. O aluno {nome} esta devidamente declarado."
    except Exception as e:
        return f"Erro ao gerar PDF: {str(e)}"
