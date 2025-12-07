"""
Sistema de Autenticação para Locadora Iguacu Veiculos
Inclui hash de senha, controle de sessão e níveis de usuário
"""
import streamlit as st
import sqlite3
import bcrypt
import hashlib
from datetime import datetime, timedelta
import secrets
from typing import Optional, Dict, Tuple

# Constantes de nível de usuário
USER_ROLES = {
    'admin': 'Administrador',
    'manager': 'Gerente',
    'employee': 'Funcionário',
    'viewer': 'Visualizador'
}

# Permissões por nível
ROLE_PERMISSIONS = {
    'admin': ['read', 'write', 'delete', 'manage_users', 'view_reports', 'backup'],
    'manager': ['read', 'write', 'delete', 'view_reports', 'backup'],
    'employee': ['read', 'write', 'view_reports'],
    'viewer': ['read']
}

class AuthManager:
    """Gerenciador de autenticação e controle de acesso"""

    def __init__(self, db_file='locadora_v2.db'):
        self.db_file = db_file
        self._init_auth_db()

    def _init_auth_db(self):
        """Inicializa tabelas de autenticação no banco"""
        conn = sqlite3.connect(self.db_file, detect_types=sqlite3.PARSE_DECLTYPES)
        c = conn.cursor()

        # Tabela de usuários
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'employee',
                full_name TEXT,
                email TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                login_attempts INTEGER DEFAULT 0,
                locked_until TIMESTAMP
            )
        ''')

        # Tabela de sessões
        c.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                ip_address TEXT,
                user_agent TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')

        # Tabela de logs de auditoria
        c.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT,
                resource TEXT,
                details TEXT,
                ip_address TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')

        conn.commit()

        # Criar usuário admin padrão se não existir
        if not self._user_exists('admin'):
            self.create_user('admin', 'admin123', 'admin', 'Administrador do Sistema', 'admin@locadora.com')

        conn.close()

    def _user_exists(self, username: str) -> bool:
        """Verifica se usuário existe"""
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = c.fetchone()
        conn.close()
        return result is not None

    def _hash_password(self, password: str) -> str:
        """Gera hash da senha usando bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verifica senha contra hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    def _generate_session_id(self) -> str:
        """Gera ID único para sessão"""
        return secrets.token_urlsafe(32)

    def _is_account_locked(self, user_id: int) -> bool:
        """Verifica se conta está bloqueada"""
        conn = sqlite3.connect(self.db_file, detect_types=sqlite3.PARSE_DECLTYPES)
        c = conn.cursor()
        c.execute("SELECT locked_until FROM users WHERE id = ?", (user_id,))
        result = c.fetchone()
        conn.close()

        if result and result[0]:
            locked_until = result[0]
            return locked_until > datetime.now()

        return False

    def _increment_login_attempts(self, user_id: int):
        """Incrementa tentativas de login"""
        conn = sqlite3.connect(self.db_file, detect_types=sqlite3.PARSE_DECLTYPES)
        c = conn.cursor()

        c.execute("SELECT login_attempts FROM users WHERE id = ?", (user_id,))
        attempts = c.fetchone()[0] or 0
        attempts += 1

        # Bloquear conta após 5 tentativas
        locked_until = None
        if attempts >= 5:
            locked_until = datetime.now() + timedelta(minutes=30)

        c.execute("""
            UPDATE users
            SET login_attempts = ?, locked_until = ?
            WHERE id = ?
        """, (attempts, locked_until, user_id))

        conn.commit()
        conn.close()

    def _reset_login_attempts(self, user_id: int):
        """Reseta tentativas de login após login bem-sucedido"""
        conn = sqlite3.connect(self.db_file, detect_types=sqlite3.PARSE_DECLTYPES)
        c = conn.cursor()
        c.execute("""
            UPDATE users
            SET login_attempts = 0, locked_until = NULL, last_login = ?
            WHERE id = ?
        """, (datetime.now(), user_id))
        conn.commit()
        conn.close()

    def create_user(self, username: str, password: str, role: str = 'employee',
                   full_name: str = '', email: str = '') -> Tuple[bool, str]:
        """Cria novo usuário"""
        if role not in USER_ROLES:
            return False, f"Nível de usuário inválido: {role}"

        if len(password) < 6:
            return False, "A senha deve ter pelo menos 6 caracteres"

        try:
            password_hash = self._hash_password(password)

            conn = sqlite3.connect(self.db_file, detect_types=sqlite3.PARSE_DECLTYPES)
            c = conn.cursor()

            c.execute("""
                INSERT INTO users (username, password_hash, role, full_name, email)
                VALUES (?, ?, ?, ?, ?)
            """, (username, password_hash, role, full_name, email))

            user_id = c.lastrowid

            # Log de auditoria
            self._log_action(user_id, 'user_created', 'users', f'Usuário {username} criado')

            conn.commit()
            conn.close()

            return True, f"Usuário {username} criado com sucesso"

        except sqlite3.IntegrityError:
            return False, f"Usuário {username} já existe"

        except Exception as e:
            return False, f"Erro ao criar usuário: {str(e)}"

    def authenticate(self, username: str, password: str, ip_address: str = '',
                    user_agent: str = '') -> Tuple[bool, Optional[Dict]]:
        """Autentica usuário e retorna dados se válido"""
        conn = sqlite3.connect(self.db_file, detect_types=sqlite3.PARSE_DECLTYPES)
        c = conn.cursor()

        c.execute("""
            SELECT id, password_hash, role, full_name, email, is_active, locked_until
            FROM users WHERE username = ?
        """, (username,))

        user = c.fetchone()
        conn.close()

        if not user:
            return False, None

        user_id, password_hash, role, full_name, email, is_active, locked_until = user

        # Verificar se conta está ativa
        if not is_active:
            return False, None

        # Verificar se conta está bloqueada
        if locked_until and locked_until > datetime.now():
            minutes_left = int((locked_until - datetime.now()).total_seconds() / 60)
            return False, {"error": f"Conta bloqueada. Tente novamente em {minutes_left} minutos."}

        # Verificar senha
        if not self._verify_password(password, password_hash):
            self._increment_login_attempts(user_id)
            return False, {"error": "Usuário ou senha incorretos"}

        # Login bem-sucedido - resetar tentativas
        self._reset_login_attempts(user_id)

        # Criar sessão
        session_id = self._generate_session_id()
        expires_at = datetime.now() + timedelta(hours=8)  # Sessão válida por 8 horas

        conn = sqlite3.connect(self.db_file, detect_types=sqlite3.PARSE_DECLTYPES)
        c = conn.cursor()
        c.execute("""
            INSERT INTO sessions (session_id, user_id, expires_at, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?)
        """, (session_id, user_id, expires_at, ip_address, user_agent))
        conn.commit()
        conn.close()

        # Log de auditoria
        self._log_action(user_id, 'login', 'auth', f'Login bem-sucedido para {username}')

        user_data = {
            'id': user_id,
            'username': username,
            'role': role,
            'full_name': full_name,
            'email': email,
            'session_id': session_id,
            'permissions': ROLE_PERMISSIONS.get(role, [])
        }

        return True, user_data

    def validate_session(self, session_id: str) -> Optional[Dict]:
        """Valida sessão ativa"""
        conn = sqlite3.connect(self.db_file, detect_types=sqlite3.PARSE_DECLTYPES)
        c = conn.cursor()

        c.execute("""
            SELECT s.user_id, u.username, u.role, u.full_name, u.email, s.expires_at
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.session_id = ? AND u.is_active = 1
        """, (session_id,))

        result = c.fetchone()
        conn.close()

        if not result:
            return None

        user_id, username, role, full_name, email, expires_at = result

        # Verificar se sessão expirou
        if expires_at < datetime.now():
            self.logout(session_id)
            return None

        return {
            'id': user_id,
            'username': username,
            'role': role,
            'full_name': full_name,
            'email': email,
            'session_id': session_id,
            'permissions': ROLE_PERMISSIONS.get(role, [])
        }

    def logout(self, session_id: str):
        """Encerra sessão"""
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
        conn.commit()
        conn.close()

    def _log_action(self, user_id: int, action: str, resource: str, details: str, ip_address: str = ''):
        """Registra ação no log de auditoria"""
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            c.execute("""
                INSERT INTO audit_logs (user_id, action, resource, details, ip_address)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, action, resource, details, ip_address))
            conn.commit()
            conn.close()
        except Exception:
            pass  # Não falhar se log não funcionar

    def get_users(self) -> list:
        """Retorna lista de usuários"""
        conn = sqlite3.connect(self.db_file, detect_types=sqlite3.PARSE_DECLTYPES)
        c = conn.cursor()
        c.execute("""
            SELECT id, username, role, full_name, email, is_active, created_at, last_login
            FROM users ORDER BY username
        """)
        users = c.fetchall()
        conn.close()

        return [{
            'id': u[0], 'username': u[1], 'role': u[2], 'full_name': u[3],
            'email': u[4], 'is_active': u[5], 'created_at': u[6], 'last_login': u[7]
        } for u in users]

    def update_user(self, user_id: int, updates: Dict) -> Tuple[bool, str]:
        """Atualiza dados do usuário"""
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()

            update_fields = []
            values = []

            if 'password' in updates:
                if len(updates['password']) < 6:
                    return False, "A senha deve ter pelo menos 6 caracteres"
                update_fields.append("password_hash = ?")
                values.append(self._hash_password(updates['password']))

            if 'role' in updates:
                if updates['role'] not in USER_ROLES:
                    return False, f"Nível de usuário inválido: {updates['role']}"
                update_fields.append("role = ?")
                values.append(updates['role'])

            if 'full_name' in updates:
                update_fields.append("full_name = ?")
                values.append(updates['full_name'])

            if 'email' in updates:
                update_fields.append("email = ?")
                values.append(updates['email'])

            if 'is_active' in updates:
                update_fields.append("is_active = ?")
                values.append(updates['is_active'])

            if not update_fields:
                return False, "Nenhum campo para atualizar"

            query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
            values.append(user_id)

            c.execute(query, values)
            conn.commit()
            conn.close()

            return True, "Usuário atualizado com sucesso"

        except Exception as e:
            return False, f"Erro ao atualizar usuário: {str(e)}"

    def delete_user(self, user_id: int) -> Tuple[bool, str]:
        """Remove usuário (desativa)"""
        try:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()

            # Verificar se é o último admin
            c.execute("SELECT COUNT(*) FROM users WHERE role = 'admin' AND is_active = 1 AND id != ?", (user_id,))
            admin_count = c.fetchone()[0]

            if admin_count == 0:
                conn.close()
                return False, "Não é possível remover o último administrador"

            # Desativar usuário ao invés de deletar
            c.execute("UPDATE users SET is_active = 0 WHERE id = ?", (user_id,))
            conn.commit()
            conn.close()

            return True, "Usuário desativado com sucesso"

        except Exception as e:
            return False, f"Erro ao remover usuário: {str(e)}"

    def get_audit_logs(self, limit: int = 100) -> list:
        """Retorna logs de auditoria"""
        conn = sqlite3.connect(self.db_file, detect_types=sqlite3.PARSE_DECLTYPES)
        c = conn.cursor()
        c.execute("""
            SELECT a.timestamp, u.username, a.action, a.resource, a.details, a.ip_address
            FROM audit_logs a
            LEFT JOIN users u ON a.user_id = u.id
            ORDER BY a.timestamp DESC LIMIT ?
        """, (limit,))
        logs = c.fetchall()
        conn.close()

        return [{
            'timestamp': l[0], 'username': l[1], 'action': l[2],
            'resource': l[3], 'details': l[4], 'ip_address': l[5]
        } for l in logs]

    def check_permission(self, user_permissions: list, required_permission: str) -> bool:
        """Verifica se usuário tem permissão"""
        return required_permission in user_permissions

# Instância global do gerenciador de autenticação
auth_manager = AuthManager()

def login_page():
    """Página de login"""
    st.title("🔐 Login - Locadora Iguacu Veiculos")

    # Verificar se já está logado
    if 'user' in st.session_state and st.session_state.user:
        user = auth_manager.validate_session(st.session_state.user['session_id'])
        if user:
            st.success(f"✅ Bem-vindo de volta, {user['full_name']}!")
            st.rerun()
            return

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("### Entre com suas credenciais")

        with st.form("login_form"):
            username = st.text_input("👤 Usuário", key="login_username")
            password = st.text_input("🔑 Senha", type="password", key="login_password")

            submitted = st.form_submit_button("🚀 Entrar", type="primary")

            if submitted:
                if not username or not password:
                    st.error("❌ Preencha usuário e senha")
                    return

                # Obter IP (simulado para desenvolvimento)
                ip_address = "127.0.0.1"  # Em produção, use request.remote_addr

                success, result = auth_manager.authenticate(username, password, ip_address)

                if success:
                    st.session_state.user = result
                    st.success(f"✅ Login realizado com sucesso! Bem-vindo, {result['full_name']}!")
                    st.balloons()
                    st.rerun()
                else:
                    if isinstance(result, dict) and 'error' in result:
                        st.error(f"❌ {result['error']}")
                    else:
                        st.error("❌ Usuário ou senha incorretos")

        st.markdown("---")
        st.markdown("**Usuário padrão:** admin / admin123")
        st.markdown("*Para alterar a senha, acesse Gerenciamento de Usuários após o login*")

def logout():
    """Faz logout do usuário"""
    if 'user' in st.session_state and st.session_state.user:
        auth_manager.logout(st.session_state.user['session_id'])
        st.session_state.user = None
        st.success("✅ Logout realizado com sucesso!")
        st.rerun()

def require_login():
    """Verifica se usuário está logado e redireciona se necessário"""
    if 'user' not in st.session_state or not st.session_state.user:
        login_page()
        return False

    # Validar sessão
    user = auth_manager.validate_session(st.session_state.user['session_id'])
    if not user:
        st.session_state.user = None
        login_page()
        return False

    # Atualizar dados da sessão
    st.session_state.user = user
    return True

def get_current_user():
    """Retorna usuário atual"""
    return st.session_state.get('user')

def check_permission(required_permission: str) -> bool:
    """Verifica permissão do usuário atual"""
    user = get_current_user()
    if not user:
        return False
    return auth_manager.check_permission(user['permissions'], required_permission)
