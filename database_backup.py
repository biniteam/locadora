"""
Script para backup e restauração do banco de dados SQLite
"""
import sqlite3
import os
import shutil
from datetime import datetime
import streamlit as st

def fazer_backup():
    """
    Cria um backup do banco de dados com timestamp
    """
    try:
        db_origem = 'locadora_v2.db'

        # Verifica se o banco existe
        if not os.path.exists(db_origem):
            return None, "Banco de dados não encontrado"

        # Cria diretório de backup se não existir
        backup_dir = 'backups'
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        # Nome do arquivo de backup com timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f'{backup_dir}/locadora_backup_{timestamp}.db'

        # Faz cópia do arquivo
        shutil.copy2(db_origem, backup_file)

        return backup_file, f"Backup criado com sucesso: {backup_file}"

    except Exception as e:
        return None, f"Erro ao criar backup: {str(e)}"

def restaurar_backup(backup_file):
    """
    Restaura o banco de dados a partir de um backup
    """
    try:
        db_destino = 'locadora_v2.db'

        # Verifica se o backup existe
        if not os.path.exists(backup_file):
            return False, "Arquivo de backup não encontrado"

        # Faz backup do banco atual antes de restaurar
        if os.path.exists(db_destino):
            backup_atual = fazer_backup()
            if backup_atual[0]:
                print(f"Backup automático criado antes da restauração: {backup_atual[0]}")

        # Restaura o backup
        shutil.copy2(backup_file, db_destino)

        return True, f"Banco restaurado com sucesso de: {backup_file}"

    except Exception as e:
        return False, f"Erro ao restaurar backup: {str(e)}"

def listar_backups():
    """
    Lista todos os backups disponíveis
    """
    backup_dir = 'backups'
    if not os.path.exists(backup_dir):
        return []

    backups = []
    for file in os.listdir(backup_dir):
        if file.startswith('locadora_backup_') and file.endswith('.db'):
            filepath = os.path.join(backup_dir, file)
            # Extrai timestamp do nome do arquivo
            timestamp_str = file.replace('locadora_backup_', '').replace('.db', '')
            try:
                # Converte timestamp para datetime
                dt = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                backups.append({
                    'file': filepath,
                    'filename': file,
                    'datetime': dt,
                    'size': os.path.getsize(filepath)
                })
            except:
                continue

    # Ordena por data (mais recente primeiro)
    backups.sort(key=lambda x: x['datetime'], reverse=True)
    return backups

def limpar_backups_antigos(manter=5):
    """
    Remove backups antigos, mantendo apenas os mais recentes
    """
    backups = listar_backups()

    if len(backups) <= manter:
        return 0, "Nenhum backup removido"

    backups_para_remover = backups[manter:]
    removidos = 0

    for backup in backups_para_remover:
        try:
            os.remove(backup['file'])
            removidos += 1
        except:
            continue

    return removidos, f"{removidos} backup(s) antigo(s) removido(s)"

def obter_estatisticas_banco():
    """
    Retorna estatísticas básicas do banco de dados
    """
    try:
        conn = sqlite3.connect('locadora_v2.db')
        c = conn.cursor()

        # Conta registros em cada tabela
        stats = {}
        tabelas = ['carros', 'clientes', 'reservas']

        for tabela in tabelas:
            c.execute(f"SELECT COUNT(*) FROM {tabela}")
            stats[tabela] = c.fetchone()[0]

        conn.close()
        return stats

    except Exception as e:
        return {"erro": str(e)}

# Interface Streamlit para gerenciamento de backups
def interface_backup():
    """
    Interface do Streamlit para gerenciar backups
    """
    st.header("💾 Gerenciamento de Backup")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📦 Criar Backup Agora", type="primary"):
            with st.spinner("Criando backup..."):
                backup_file, mensagem = fazer_backup()
                if backup_file:
                    st.success(mensagem)
                else:
                    st.error(mensagem)

    with col2:
        if st.button("🧹 Limpar Backups Antigos"):
            removidos, mensagem = limpar_backups_antigos()
            if removidos > 0:
                st.success(mensagem)
            else:
                st.info(mensagem)

    with col3:
        stats = obter_estatisticas_banco()
        if "erro" not in stats:
            st.metric("Total de Registros",
                     sum(stats.values()))
        else:
            st.error("Erro ao obter estatísticas")

    # Lista de backups disponíveis
    st.subheader("Backups Disponíveis")
    backups = listar_backups()

    if backups:
        for backup in backups[:10]:  # Mostra apenas os 10 mais recentes
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])

            with col1:
                st.write(f"📁 {backup['filename']}")

            with col2:
                st.write(f"📅 {backup['datetime'].strftime('%d/%m/%Y %H:%M')}")

            with col3:
                tamanho_mb = backup['size'] / (1024 * 1024)
                st.write(f"💾 {tamanho_mb:.1f} MB")

            with col4:
                if st.button("🔄 Restaurar", key=f"restore_{backup['filename']}"):
                    with st.spinner("Restaurando backup..."):
                        sucesso, mensagem = restaurar_backup(backup['file'])
                        if sucesso:
                            st.success(mensagem)
                            st.rerun()
                        else:
                            st.error(mensagem)
    else:
        st.info("Nenhum backup encontrado")

if __name__ == "__main__":
    # Quando executado diretamente, cria um backup
    backup_file, mensagem = fazer_backup()
    print(mensagem)
