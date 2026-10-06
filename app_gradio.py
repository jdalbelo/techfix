import gradio as gr
import os
import re
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

# Evita erro se a chave não estiver configurada no momento de gerar a interface
if url and key:
    supabase: Client = create_client(url, key)

def aplicar_mascara(telefone):
    """Aplica a máscara +55 (XX) XXXXX-XXXX em tempo real"""
    if not telefone:
        return "+55 "
    
    # Remove tudo que não for número
    num = re.sub(r'\D', '', telefone)
    
    # Garante que sempre comece com 55 (caso o usuário tente apagar)
    if not num.startswith("55"):
        num = "55" + num
        
    # Limita o tamanho máximo (55 + 2 do DDD + 9 números = 13 dígitos)
    num = num[:13]

    # Constrói a máscara
    if len(num) <= 2:
        return f"+{num}"
    elif len(num) <= 4:
        return f"+55 ({num[2:]}"
    elif len(num) <= 9:
        return f"+55 ({num[2:4]}) {num[4:]}"
    else:
        return f"+55 ({num[2:4]}) {num[4:9]}-{num[9:]}"

def submeter_os(nome, endereco, email, celular, modelo, problema):
    if not url or not key: return "Erro: Configure as credenciais no ficheiro .env"
    if not all([nome, endereco, email, celular, modelo, problema]):
        return "Erro: Todos os campos são obrigatórios."
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return "Erro: Formato de e-mail inválido."
    
    # Limpa a máscara para salvar e validar apenas os números
    celular_limpo = re.sub(r'\D', '', celular)
    
    # Verifica se contém os 12 ou 13 dígitos (55 + 2 DDD + 8 ou 9 Números)
    if not re.match(r"^[0-9]{12,13}$", celular_limpo):
        return "Erro: Informe o DDD e o número completo do telefone."

    try:
        resposta_cliente = supabase.table("clientes").select("id").eq("email", email).execute()

        if len(resposta_cliente.data) > 0:
            cliente_id = resposta_cliente.data[0]["id"]
        else:
            # Salva o número limpo apenas com dígitos na base de dados
            novo_cliente = {"nome": nome, "endereco": endereco, "email": email, "celular_whatsapp": celular_limpo}
            insercao = supabase.table("clientes").insert(novo_cliente).execute()
            cliente_id = insercao.data[0]["id"]

        nova_os = {
            "cliente_id": cliente_id,
            "modelo_computador": modelo,
            "problema_relatado": problema,
            "status": "Aberto"
        }
        resposta_os = supabase.table("ordens_servico").insert(nova_os).execute()
        return f"Sucesso! Ordem de Serviço criada com o número: {resposta_os.data[0]['id']}"
    except Exception as e:
        return f"Erro na base de dados: {str(e)}"

def limpar_campos():
    # O 4º campo (celular) volta para o estado inicial preenchido
    return "", "", "", "55", "", "", ""

with gr.Blocks(title="TechFix - Atendimento") as interface:
    gr.Markdown("# TechFix Informática - Nova Ordem de Serviço")
    with gr.Row():
        with gr.Column():
            nome = gr.Textbox(label="Nome do Cliente")
            endereco = gr.Textbox(label="Endereço")
            email = gr.Textbox(label="E-mail")
            # Adicionado o valor inicial +55
            celular = gr.Textbox(label="Celular/WhatsApp", value="+55 ", placeholder="+55 (XX) XXXXX-XXXX")
        with gr.Column():
            modelo = gr.Textbox(label="Modelo do Computador")
            problema = gr.Textbox(label="Problema Apresentado", lines=5)

    mensagem_retorno = gr.Textbox(label="Estado", interactive=False)
    with gr.Row():
        btn_cadastrar = gr.Button("Cadastrar", variant="primary")
        btn_limpar = gr.Button("Limpar")

    # Monitora a digitação no campo e aplica a máscara
    celular.change(fn=aplicar_mascara, inputs=celular, outputs=celular)

    btn_cadastrar.click(fn=submeter_os, inputs=[nome, endereco, email, celular, modelo, problema], outputs=mensagem_retorno)
    btn_limpar.click(fn=limpar_campos, inputs=[], outputs=[nome, endereco, email, celular, modelo, problema, mensagem_retorno])

if __name__ == "__main__":
    interface.launch(share=True)