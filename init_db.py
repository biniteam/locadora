"""
Script de inicialização do banco de dados para produção
Executa automaticamente quando a aplicação inicia
"""
import sqlite3
import os
import streamlit as st
from datetime import datetime

def init_db_production():
    """
    Inicializa o banco de dados com verificações adicionais para produção
    """
    db_file = 'locadora_v2.db'

    # Verifica se o banco já existe
    db_exists = os.path.exists(db_file)

    if db_exists:
        st.info("✅ Banco de dados encontrado. Verificando estrutura...")
        # Verifica se o banco está corrompido
        try:
            conn = sqlite3.connect(db_file, detect_types=sqlite3.PARSE_DECLTYPES)
            c = conn.cursor()
            c.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = c.fetchall()
            conn.close()

            if not tables:
                st.warning("⚠️ Banco de dados vazio. Recriando estrutura...")
                db_exists = False
            else:
                st.success("✅ Estrutura do banco verificada com sucesso!")
                return True

        except sqlite3.DatabaseError as e:
            st.error(f"❌ Banco de dados corrompido: {e}")
            # Tenta restaurar backup se disponível
            backup_restored = try_restore_backup()
            if backup_restored:
                return True
            else:
                st.warning("⚠️ Criando novo banco de dados...")
                db_exists = False

    if not db_exists:
        st.info("🔄 Criando novo banco de dados...")

        conn = sqlite3.connect(db_file, detect_types=sqlite3.PARSE_DECLTYPES)
        c = conn.cursor()

        # Criar tabelas principais
        c.execute('''
            CREATE TABLE IF NOT EXISTS carros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                modelo TEXT,
                placa TEXT UNIQUE,
                cor TEXT,
                diaria REAL,
                preco_km REAL,
                km_atual INTEGER,
                status TEXT DEFAULT 'Disponível',
                numero_chassi TEXT,
                numero_renavam TEXT,
                ano_veiculo INTEGER,
                km_troca_oleo INTEGER DEFAULT 10000
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                cpf TEXT UNIQUE,
                cnh TEXT,
                validade_cnh DATE,
                telefone TEXT,
                endereco TEXT,
                observacoes TEXT,
                status TEXT DEFAULT 'Ativo'
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS reservas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                carro_id INTEGER,
                cliente_id INTEGER,
                data_inicio DATE,
                data_fim DATE,
                reserva_status TEXT DEFAULT 'Reservada',
                status TEXT,
                custo_lavagem REAL DEFAULT 0,
                valor_total REAL DEFAULT 0,
                km_saida INTEGER,
                km_volta INTEGER,
                km_franquia INTEGER DEFAULT 300,
                adiantamento REAL DEFAULT 0.0,
                valor_multas REAL DEFAULT 0.0,
                valor_danos REAL DEFAULT 0.0,
                valor_outros REAL DEFAULT 0.0,
                FOREIGN KEY(carro_id) REFERENCES carros(id),
                FOREIGN KEY(cliente_id) REFERENCES clientes(id)
            )
        ''')

        conn.commit()
        conn.close()

        # Criar backup inicial
        from database_backup import fazer_backup
        backup_file, _ = fazer_backup()
        if backup_file:
            st.success(f"✅ Banco criado e backup inicial salvo: {backup_file}")
        else:
            st.success("✅ Banco de dados criado com sucesso!")

        return True

def try_restore_backup():
    """
    Tenta restaurar o backup mais recente se disponível
    """
    try:
        from database_backup import listar_backups, restaurar_backup

        backups = listar_backups()
        if backups:
            latest_backup = backups[0]['file']  # Primeiro da lista (mais recente)
            sucesso, mensagem = restaurar_backup(latest_backup)
            if sucesso:
                st.success(f"✅ Backup restaurado: {mensagem}")
                return True
            else:
                st.error(f"❌ Erro na restauração: {mensagem}")
        else:
            st.warning("⚠️ Nenhum backup disponível para restauração")

    except Exception as e:
        st.error(f"❌ Erro ao tentar restaurar backup: {e}")

    return False

def check_db_health():
    """
    Verifica a saúde do banco de dados e retorna estatísticas
    """
    try:
        conn = sqlite3.connect('locadora_v2.db', detect_types=sqlite3.PARSE_DECLTYPES)
        c = conn.cursor()

        # Verificar tabelas
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in c.fetchall()]

        # Estatísticas básicas
        stats = {}
        for table in ['carros', 'clientes', 'reservas']:
            if table in tables:
                c.execute(f"SELECT COUNT(*) FROM {table}")
                stats[table] = c.fetchone()[0]
            else:
                stats[table] = 0

        # Verificar integridade
        c.execute("PRAGMA integrity_check")
        integrity = c.fetchone()[0]

        conn.close()

        return {
            'healthy': integrity == 'ok',
            'tables': tables,
            'stats': stats,
            'integrity': integrity
        }

    except Exception as e:
        return {
            'healthy': False,
            'error': str(e)
        }

# Executar inicialização quando o módulo é importado
if __name__ != "__main__":
    # Apenas executa em produção ou quando chamado via streamlit
    try:
        init_db_production()
    except Exception as e:
        st.error(f"Erro na inicialização do banco: {e}")

if __name__ == "__main__":
    # Para testes manuais
    print("Verificando banco de dados...")
    health = check_db_health()
    if health['healthy']:
        print("✅ Banco saudável!")
        print(f"Tabelas: {health['tables']}")
        print(f"Estatísticas: {health['stats']}")
    else:
        print(f"❌ Problemas no banco: {health.get('error', 'Desconhecido')}")
        init_db_production()
