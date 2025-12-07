# Sistema de Locadora de Veículos

Sistema completo de gerenciamento de locadora de veículos desenvolvido em Streamlit com banco de dados SQLite e **sistema de autenticação seguro**.

## Funcionalidades

### 🔐 Sistema de Autenticação
- **Login seguro** com hash de senha (bcrypt)
- **Níveis de usuário**: Administrador, Gerente, Funcionário, Visualizador
- **Controle de permissões** granular
- **Sessões seguras** com expiração automática
- **Logs de auditoria** completos
- **Proteção contra força bruta** (bloqueio após tentativas falhidas)

### 📊 Gestão da Locadora
- **Dashboard**: Painel com métricas gerais, agenda do dia e verificação rápida de disponibilidade
- **Gestão de Clientes**: Cadastro, edição e exclusão de clientes
- **Gestão da Frota**: Controle completo de veículos (carros)
- **Reservas**: Sistema de reserva e bloqueio de datas
- **Entrega**: Confirmação de entrega com geração automática de contratos
- **Devolução**: Processo completo de devolução com cálculo de custos
- **Histórico**: Relatórios detalhados e análises de faturamento
- **Relatórios**: Relatórios de disponibilidade da frota em Excel
- **Backup**: Sistema automático de backup e restauração

### 👥 Gerenciamento de Usuários (Apenas Administradores)
- Criar, editar e desativar usuários
- Definir níveis de acesso e permissões
- Visualizar logs de auditoria
- Monitorar atividades do sistema

## Tecnologias Utilizadas

- **Python 3.8+**
- **Streamlit**: Framework web para aplicações de dados
- **SQLite**: Banco de dados local
- **Pandas**: Manipulação e análise de dados
- **Matplotlib**: Geração de gráficos
- **OpenPyXL**: Manipulação de arquivos Excel
- **FPDF**: Geração de PDFs (contratos e recibos)
- **bcrypt**: Hash seguro de senhas

## 🔐 Segurança e Usuários

### Usuário Padrão
- **Usuário**: admin
- **Senha**: admin123
- **Nível**: Administrador

⚠️ **IMPORTANTE**: Altere a senha padrão imediatamente após o primeiro login!

### Níveis de Acesso
- **Administrador**: Acesso total, incluindo gerenciamento de usuários
- **Gerente**: Acesso completo exceto gerenciamento de usuários
- **Funcionário**: Acesso básico de operação
- **Visualizador**: Apenas leitura de dados

### Recursos de Segurança
- Hash de senha com bcrypt
- Sessões com expiração (8 horas)
- Bloqueio automático após 5 tentativas falhidas
- Logs completos de auditoria
- Controle granular de permissões

## Instalação e Execução Local

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes do Python)

### Passos para Instalação

1. Clone ou baixe o projeto:
```bash
git clone <url-do-repositorio>
cd locadora_strealit
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute a aplicação:
```bash
streamlit run app8.py
```

4. Acesse no navegador: `http://localhost:8501`

## Opções de Deploy

### 1. Streamlit Cloud (Recomendado) ⭐

**Vantagens:**
- Fácil deploy direto do GitHub
- Gratuito para uso básico
- Suporte nativo ao Streamlit
- Auto-scaling automático

**Limitações:**
- Banco SQLite pode ser perdido em reinícios
- Limite de recursos para plano gratuito
- Não suporta armazenamento persistente de arquivos

**Como fazer deploy:**
1. Faça upload do código para GitHub
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. Conecte sua conta GitHub
4. Selecione o repositório e o arquivo principal (`app8.py`)

### 2. Railway

**Vantagens:**
- Deploy direto do GitHub
- Suporte a bancos de dados
- Escalabilidade automática
- Plano gratuito generoso

**Como fazer deploy:**
1. Crie uma conta em [railway.app](https://railway.app)
2. Conecte seu repositório GitHub
3. Railway detectará automaticamente o projeto Python
4. Configure as variáveis de ambiente se necessário

### 3. Heroku

**Vantagens:**
- Plataforma robusta e madura
- Suporte completo a Python
- Add-ons para bancos de dados
- Boa documentação

**Como fazer deploy:**
1. Crie uma conta em [heroku.com](https://heroku.com)
2. Instale Heroku CLI
3. Crie um arquivo `Procfile`:
   ```
   web: streamlit run app8.py --server.port=$PORT --server.headless=true
   ```
4. Deploy via Git ou CLI

### 4. VPS (DigitalOcean, AWS, etc.)

**Vantagens:**
- Controle total sobre o ambiente
- Possibilidade de usar PostgreSQL/MySQL
- Escalabilidade personalizada
- Melhor para aplicações críticas

**Como fazer deploy:**
1. Escolha um provedor VPS (DigitalOcean, AWS EC2, etc.)
2. Configure o servidor Ubuntu/Debian
3. Instale Python e dependências
4. Configure Nginx como proxy reverso
5. Use PM2 ou systemctl para gerenciar a aplicação
6. Configure SSL com Certbot

## Configuração do Banco de Dados

### Desenvolvimento (SQLite Local)
O projeto já vem configurado para usar SQLite local (`locadora_v2.db`).

### Produção Recomendada
Para produção, considere migrar para:
- **PostgreSQL** (Railway, Heroku)
- **MySQL** (DigitalOcean, AWS)
- **SQLite com backup automático** (VPS)

### Migração para PostgreSQL
1. Instale psycopg2-binary
2. Altere as conexões no código de `sqlite3` para `psycopg2`
3. Configure a string de conexão para o banco PostgreSQL

## Estrutura do Projeto

```
locadora_strealit/
├── app8.py                 # Aplicação principal
├── pdfgenerator.py         # Módulo de geração de PDFs
├── requirements.txt        # Dependências Python
├── .streamlit/
│   └── config.toml        # Configurações Streamlit
├── locadora_v2.db         # Banco de dados SQLite
└── README.md              # Este arquivo
```

## Variáveis de Ambiente

Para produção, considere configurar:

```bash
# Streamlit
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Banco de dados (se usar PostgreSQL)
DATABASE_URL=postgresql://user:password@host:port/database
```

## Backup e Segurança

- **Backup do banco**: Configure backups automáticos do arquivo `.db`
- **Segurança**: Implemente autenticação se necessário
- **Monitoramento**: Configure logs e alertas

## Suporte

Para dúvidas ou problemas:
- Verifique os logs da aplicação
- Teste localmente antes do deploy
- Considere as limitações de cada plataforma

## Licença

Este projeto é propriedade da J.A. MARCELLO & CIA LTDA.
