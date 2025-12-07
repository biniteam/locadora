#!/usr/bin/env python3
"""
Script para executar a aplicação Locadora Strealit
"""
import streamlit as st

def main():
    """Executa a aplicação principal"""
    # Configurações da página
    st.set_page_config(
        page_title="Locadora Pro 4.9",
        layout="wide",
        page_icon="🚗"
    )

    # Importar e executar a aplicação principal
    # (O sistema de autenticação será carregado automaticamente)
    exec(open('app8.py').read())

if __name__ == "__main__":
    main()
