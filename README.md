# Guia de Instalação e Execução - TechFix

Este documento fornece as instruções passo a passo para configurar o ambiente, instalar as dependências e executar as aplicações do projeto TechFix.

---

## 1. Pré-requisitos
* Python 3.8 ou superior instalado no sistema.
* Gerenciador de pacotes `pip`.
* Um servidor de banco de dados configurado localmente ou em nuvem.

## 2. Preparação do Ambiente
* Navegue até o diretório principal do projeto chamado `techfix`.
* É altamente recomendado o uso de um ambiente virtual para isolar as dependências.
* Crie o ambiente virtual executando o comando `python -m venv venv` no terminal.
* Ative o ambiente virtual (no Windows utilize `venv\Scripts\activate` e no Linux/MacOS utilize `source venv/bin/activate`).

## 3. Instalação das Dependências
* O repositório inclui um arquivo de configuração de pacotes chamado `requirements.txt`.
* Com o ambiente virtual ativado, execute o seguinte comando no terminal para instalar todas as bibliotecas requeridas:
  ```bash
  pip install -r requirements.txt