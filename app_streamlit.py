import streamlit as st
import pandas as pd
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash 

st.set_page_config(page_title="TechFix Admin", layout="wide")

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if url and key:
    supabase: Client = create_client(url, key)
else:
    st.error("Configure as credenciais SUPABASE_URL e SUPABASE_KEY no ficheiro .env")
    st.stop()

# Inicialização do estado de sessão
if "autenticado" not in st.session_state: 
    st.session_state["autenticado"] = False
if "username" not in st.session_state: 
    st.session_state["username"] = ""

def ecra_autenticacao():
    st.title("🔒 Acesso ao Sistema - TechFix")
    
    with st.form("form_login"):
        username_login = st.text_input("Login")
        password_login = st.text_input("Senha", type="password")
        if st.form_submit_button("Entrar"):
            try:
                resposta = supabase.table("admins").select("password_hash").eq("username", username_login).execute()
                if resposta.data and check_password_hash(resposta.data[0]["password_hash"], password_login):
                    st.session_state["autenticado"] = True
                    st.session_state["username"] = username_login
                    st.rerun()
                else:
                    st.error("Credenciais inválidas.")
            except Exception as e: 
                st.error(f"Erro: {e}")

# ==========================================
# BARREIRA DE AUTENTICAÇÃO
# ==========================================
if not st.session_state["autenticado"]:
    ecra_autenticacao()
    st.stop()

# ==========================================
# SISTEMA PRINCIPAL
# ==========================================
st.sidebar.markdown(f"**Bem-vindo, {st.session_state['username']}**")
if st.sidebar.button("Terminar Sessão"):
    st.session_state["autenticado"] = False
    st.rerun()

st.title("Painel Administrativo - TechFix")

aba1, aba2, aba3, aba4, aba5 = st.tabs(["Consultar", "Cadastrar", "Editar/Excluir", "Indicadores", "Administradores"])

def obter_dados(tabela, select="*"):
    try: 
        return supabase.table(tabela).select(select).execute().data
    except: 
        return []

st.sidebar.header("Filtros")
f_nome = st.sidebar.text_input("Nome do Cliente")
f_status = st.sidebar.selectbox("Estado", ["Todos", "Aberto", "Em análise", "Aguardando peça", "Concluído", "Entregue"])

with aba1:
    st.header("Ordens de Serviço")
    dados_os = obter_dados("ordens_servico", "*, clientes(nome, email, celular_whatsapp)")
    if dados_os:
        df = pd.json_normalize(dados_os)
        if f_nome: 
            df = df[df['clientes.nome'].str.contains(f_nome, case=False, na=False)]
        if f_status != "Todos": 
            df = df[df['status'] == f_status]
        st.dataframe(df)
        st.download_button("Exportar CSV", df.to_csv(index=False).encode('utf-8'), "os.csv", "text/csv")

# ==========================================
# ABA 2: CADASTRAR E LISTAR CLIENTES
# ==========================================
with aba2:
    st.header("Cadastrar Ordem de Serviço")
    clientes = obter_dados("clientes")
    
    if clientes:
        opcoes = {f"{c['nome']} ({c['email']})": c['id'] for c in clientes}
        cli_sel = st.selectbox("Selecione o Cliente", list(opcoes.keys()))
        mod_os = st.text_input("Modelo")
        prob_os = st.text_area("Problema")
        
        if st.button("Guardar OS"):
            if mod_os and prob_os:
                supabase.table("ordens_servico").insert({
                    "cliente_id": opcoes[cli_sel], 
                    "modelo_computador": mod_os, 
                    "problema_relatado": prob_os, 
                    "status": "Aberto"
                }).execute()
                st.success("OS registada com sucesso!")
            else:
                st.warning("Preencha todos os campos da OS.")
        
        st.divider()
        
        # Secção: Listagem de clientes
        st.subheader("Clientes Cadastrados")
        df_clientes = pd.DataFrame(clientes)
        st.dataframe(df_clientes, hide_index=True, use_container_width=True)

        st.divider()

        # Secção: Excluir cliente
        st.subheader("Excluir Cadastro de Cliente")
        cliente_excluir = st.selectbox("Selecione o Cliente a Excluir", list(opcoes.keys()), key="del_cli")
        
        confirmar_del_cli = st.checkbox(f"Confirmar exclusão de {cliente_excluir}")
        if st.button("Excluir Cliente", type="primary"):
            if confirmar_del_cli:
                try:
                    supabase.table("clientes").delete().eq("id", opcoes[cliente_excluir]).execute()
                    st.success(f"Cliente removido com sucesso!")
                    st.rerun()
                except Exception as e:
                    # Caso haja restrição de chave estrangeira (ex: o cliente tem uma OS associada)
                    st.error(f"Erro ao excluir. Verifique se existem ordens de serviço vinculadas a este cliente. Detalhe: {e}")
            else:
                st.warning("Marque a caixa de confirmação para poder excluir.")

    else:
        st.info("Nenhum cliente cadastrado na base de dados.")

with aba3:
    st.header("Gestão de Registos")
    dados_os = obter_dados("ordens_servico")
    if dados_os:
        os_id = st.selectbox("ID da OS", [os['id'] for os in dados_os])
        col1, col2 = st.columns(2)
        with col1:
            novo_st = st.selectbox("Alterar Estado", ['Aberto', 'Em análise', 'Aguardando peça', 'Concluído', 'Entregue'])
            if st.button("Atualizar Estado"):
                supabase.table("ordens_servico").update({"status": novo_st}).eq("id", os_id).execute()
                st.success("Atualizado!")
        with col2:
            if st.checkbox("Confirmar exclusão") and st.button("Excluir Ordem"):
                supabase.table("ordens_servico").delete().eq("id", os_id).execute()
                st.success("Removida!")

with aba4:
    st.header("Dashboard")
    dados_os = obter_dados("ordens_servico")
    if dados_os:
        contagem = pd.DataFrame(dados_os)['status'].value_counts()
        cols = st.columns(len(contagem))
        for i, (est, tot) in enumerate(contagem.items()): 
            cols[i].metric(est, tot)
        st.bar_chart(contagem)

with aba5:
    st.header("Gestão de Administradores")
    
    st.subheader("Administradores Cadastrados")
    dados_admins = obter_dados("admins", "id, username") 
    
    if dados_admins:
        df_admins = pd.DataFrame(dados_admins)
        st.dataframe(df_admins, hide_index=True, use_container_width=True)
    else:
        st.info("Nenhum administrador encontrado.")

    st.divider()

    col_add, col_edit = st.columns(2)

    with col_add:
        st.subheader("Cadastrar Novo")
        with st.form("form_add_admin"):
            novo_user = st.text_input("Username")
            nova_senha = st.text_input("Password", type="password")
            
            if st.form_submit_button("Cadastrar Administrador"):
                if novo_user and nova_senha:
                    try:
                        hash_senha = generate_password_hash(nova_senha)
                        supabase.table("admins").insert({
                            "username": novo_user,
                            "password_hash": hash_senha
                        }).execute()
                        st.success(f"Administrador '{novo_user}' cadastrado com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao cadastrar. Detalhes: {e}")
                else:
                    st.warning("Preencha todos os campos.")

    with col_edit:
        st.subheader("Editar ou Excluir")
        if dados_admins:
            opcoes_admins = {admin["username"]: admin["id"] for admin in dados_admins}
            admin_selecionado = st.selectbox("Selecione o Administrador", list(opcoes_admins.keys()))
            
            nova_senha_edit = st.text_input("Nova Password", type="password", help="Preencha apenas se desejar alterar a senha")
            if st.button("Atualizar Password"):
                if nova_senha_edit:
                    try:
                        hash_edit = generate_password_hash(nova_senha_edit)
                        supabase.table("admins").update({"password_hash": hash_edit}).eq("id", opcoes_admins[admin_selecionado]).execute()
                        st.success(f"Password de '{admin_selecionado}' atualizada com sucesso!")
                    except Exception as e:
                        st.error(f"Erro ao atualizar: {e}")
                else:
                    st.warning("Introduza a nova password antes de atualizar.")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            confirmar_del = st.checkbox(f"Confirmar exclusão de {admin_selecionado}")
            if st.button("Excluir Administrador", type="primary"):
                if confirmar_del:
                    if admin_selecionado == st.session_state["username"]:
                        st.error("Ação não permitida: Você não pode excluir a sua própria conta enquanto estiver logado.")
                    else:
                        try:
                            supabase.table("admins").delete().eq("id", opcoes_admins[admin_selecionado]).execute()
                            st.success(f"Administrador '{admin_selecionado}' removido com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao excluir: {e}")
                else:
                    st.warning("Marque a caixa de confirmação para poder excluir.")