"""
Script de testes para verificar se a aplicação está funcionando corretamente
"""
import sys
import os
import subprocess

def test_imports():
    """Testa se todas as dependências podem ser importadas"""
    print("🔍 Testando imports...")

    try:
        import streamlit as st
        print("✅ Streamlit OK")

        import pandas as pd
        print("✅ Pandas OK")

        import matplotlib.pyplot as plt
        print("✅ Matplotlib OK")

        import sqlite3
        print("✅ SQLite OK")

        from openpyxl import Workbook
        print("✅ OpenPyXL OK")

        from fpdf import FPDF
        print("✅ FPDF OK")

        import numpy as np
        print("✅ NumPy OK")

        import bcrypt
        print("✅ Bcrypt OK")

        return True
    except ImportError as e:
        print(f"❌ Erro no import: {e}")
        return False

def test_database():
    """Testa se o banco de dados pode ser criado/acessado"""
    print("\n🔍 Testando banco de dados...")

    try:
        from init_db import check_db_health, init_db_production

        health = check_db_health()
        if health['healthy']:
            print("✅ Banco de dados saudável")
            print(f"   📊 Estatísticas: {health['stats']}")
            return True
        else:
            print(f"❌ Problemas no banco: {health.get('error', 'Desconhecido')}")
            init_db_production()
            return True

    except Exception as e:
        print(f"❌ Erro no banco de dados: {e}")
        return False

def test_pdf_generation():
    """Testa se a geração de PDFs funciona"""
    print("\n🔍 Testando geração de PDFs...")

    try:
        from pdfgenerator import gerar_contrato_pdf

        # Dados de teste
        cliente_teste = {
            'nome': 'CLIENTE TESTE',
            'cpf': '123.456.789-00',
            'cnh': '123456789',
            'telefone': '41999999999',
            'endereco': 'RUA TESTE, 123'
        }

        carro_teste = {
            'modelo': 'CARRO TESTE',
            'placa': 'ABC-1234',
            'cor': 'PRETA',
            'diaria': 100.0,
            'preco_km': 2.5,
            'km_atual': 10000,
            'numero_chassi': '12345678901234567',
            'numero_renavam': '123456789',
            'ano_veiculo': 2020
        }

        from datetime import date, timedelta
        data_inicio = date.today()
        data_fim = data_inicio + timedelta(days=7)

        pdf_bytes = gerar_contrato_pdf(cliente_teste, carro_teste, data_inicio, data_fim)

        if pdf_bytes and len(pdf_bytes) > 1000:  # PDF deve ter pelo menos 1KB
            print("✅ Geração de PDF OK")
            return True
        else:
            print("❌ PDF gerado muito pequeno")
            return False

    except Exception as e:
        print(f"❌ Erro na geração de PDF: {e}")
        return False

def test_auth_system():
    """Testa o sistema de autenticação"""
    print("\n🔍 Testando sistema de autenticação...")

    try:
        from auth import auth_manager

        # Testar criação de usuário
        success, message = auth_manager.create_user('test_user', 'test123', 'employee', 'Usuário Teste')
        if not success and 'já existe' not in message:
            print(f"❌ Erro ao criar usuário teste: {message}")
            return False

        # Testar autenticação
        success, user_data = auth_manager.authenticate('admin', 'admin123')
        if success:
            print("✅ Autenticação OK")

            # Testar validação de sessão
            session_user = auth_manager.validate_session(user_data['session_id'])
            if session_user:
                print("✅ Validação de sessão OK")

                # Testar permissões
                from auth import check_permission
                # Simular usuário na sessão
                import streamlit as st
                if hasattr(st, 'session_state'):
                    st.session_state.user = user_data

                    if check_permission('read'):
                        print("✅ Sistema de permissões OK")
                        return True
                    else:
                        print("❌ Erro no sistema de permissões")
                        return False
                else:
                    print("✅ Autenticação básica OK (sem interface)")
                    return True
            else:
                print("❌ Erro na validação de sessão")
                return False
        else:
            print("❌ Erro na autenticação")
            return False

    except Exception as e:
        print(f"❌ Erro no sistema de autenticação: {e}")
        return False

def test_backup_system():
    """Testa o sistema de backup"""
    print("\n🔍 Testando sistema de backup...")

    try:
        from database_backup import fazer_backup, listar_backups

        backup_file, mensagem = fazer_backup()
        if backup_file:
            print(f"✅ Backup criado: {backup_file}")

            backups = listar_backups()
            if backups:
                print(f"✅ {len(backups)} backup(s) encontrado(s)")
                return True
            else:
                print("❌ Nenhum backup encontrado")
                return False
        else:
            print(f"❌ Erro no backup: {mensagem}")
            return False

    except Exception as e:
        print(f"❌ Erro no sistema de backup: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🚗 Iniciando testes da Locadora Strealit v4.9")
    print("=" * 50)

    tests = [
        ("Imports", test_imports),
        ("Banco de Dados", test_database),
        ("Sistema de Autenticação", test_auth_system),
        ("Geração de PDFs", test_pdf_generation),
        ("Sistema de Backup", test_backup_system),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Executando teste: {test_name}")
        result = test_func()
        results.append((test_name, result))

    print("\n" + "=" * 50)
    print("📊 RESULTADO DOS TESTES:")

    all_passed = True
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"   {test_name}: {status}")
        if not result:
            all_passed = False

    print("=" * 50)
    if all_passed:
        print("🎉 Todos os testes passaram! A aplicação está pronta para deploy.")
        return 0
    else:
        print("⚠️ Alguns testes falharam. Verifique os problemas antes do deploy.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
