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

def submeter_os(nome, endereco, email, celular, modelo, problema):
    if not url or not key: return "Erro: Configure as credenciais no ficheiro .env"
    if not all([nome, endereco, email, celular, modelo, problema]):
        return "Erro: Todos os campos são obrigatórios."
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return "Erro: Formato de e-mail inválido."
    if not re.match(r"^[0-9]{10,13}$", celular):
        return "Erro: O telemóvel deve conter apenas números (10 a 13 caracteres)."

    try:
        resposta_cliente = supabase.table("clientes").select("id").eq("email", email).execute()

        if len(resposta_cliente.data) > 0:
            cliente_id = resposta_cliente.data[0]["id"]
        else:
            novo_cliente = {"nome": nome, "endereco": endereco, "email": email, "celular_whatsapp": celular}
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
    return "", "", "", "", "", "", ""

with gr.Blocks(title="TechFix - Atendimento") as interface:
    gr.Markdown("# TechFix Informática - Nova Ordem de Serviço")
    with gr.Row():
        with gr.Column():
            nome = gr.Textbox(label="Nome do Cliente")
            endereco = gr.Textbox(label="Endereço")
            email = gr.Textbox(label="E-mail")
            celular = gr.Textbox(label="Celular/WhatsApp")
        with gr.Column():
            modelo = gr.Textbox(label="Modelo do Computador")
            problema = gr.Textbox(label="Problema Apresentado", lines=5)

    mensagem_retorno = gr.Textbox(label="Estado", interactive=False)
    with gr.Row():
        btn_cadastrar = gr.Button("Cadastrar", variant="primary")
        btn_limpar = gr.Button("Limpar")

    btn_cadastrar.click(fn=submeter_os, inputs=[nome, endereco, email, celular, modelo, problema], outputs=mensagem_retorno)
    btn_limpar.click(fn=limpar_campos, inputs=[], outputs=[nome, endereco, email, celular, modelo, problema, mensagem_retorno])

if __name__ == "__main__":
    interface.launch(share=True)
