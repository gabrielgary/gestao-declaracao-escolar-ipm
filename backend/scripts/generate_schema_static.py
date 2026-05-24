import os
import re

def extract_models(directory):
    models_schema = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py') and file != '__init__.py' and file != 'base.py':
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Regex simples para capturar classes de modelos
                    classes = re.findall(r'class\s+(\w+)\s*\(.*Model.*\):', content)
                    for cls in classes:
                        # Tentar capturar campos
                        # Esta é uma abordagem heurística, mas útil em emergências
                        fields = re.findall(r'(\w+)\s*=\s*models\.(\w+Field)\((.*?)\)', content)
                        models_schema.append((cls, fields))
    return models_schema

def generate_sql(models_schema):
    sql = "-- Esquema de Banco de Dados Gerado por Análise Estática de Models\n"
    sql += "-- Nota: Este é um esquema representativo.\n\n"
    
    for cls, fields in models_schema:
        sql += f"CREATE TABLE {cls.lower()} (\n"
        sql_fields = []
        sql_fields.append("    id SERIAL PRIMARY KEY")
        for name, field_type, params in fields:
            # Mapeamento básico de tipos
            db_type = "TEXT"
            if "Char" in field_type: db_type = "VARCHAR(255)"
            elif "Integer" in field_type: db_type = "INTEGER"
            elif "Decimal" in field_type: db_type = "NUMERIC(10, 2)"
            elif "DateTime" in field_type: db_type = "TIMESTAMP"
            elif "Date" in field_type: db_type = "DATE"
            elif "Boolean" in field_type: db_type = "BOOLEAN"
            elif "ForeignKey" in field_type: db_type = "INTEGER REFERENCES ..." # Heurística simplificada
            
            sql_fields.append(f"    {name} {db_type}")
        
        sql += ",\n".join(sql_fields)
        sql += "\n);\n\n"
    return sql

apis_models_dir = 'apis/models'
schema = extract_models(apis_models_dir)
sql_content = generate_sql(schema)

output_path = '../docs/db_schema.sql'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(sql_content)

print(f"Esquema gerado com sucesso em {output_path}")
