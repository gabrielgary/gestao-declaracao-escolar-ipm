
#Django settings for core project.


from pathlib import Path
from datetime import timedelta
import os
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
load_dotenv(os.path.join(BASE_DIR, '.env'))


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    # Apenas para desenvolvimento se o .env estiver faltando
    SECRET_KEY = 'django-insecure-substitua-isso-no-env'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

#ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost 127.0.0.1 192.168.216.221').split(' ')
ALLOWED_HOSTS=['https://gestao-declaracao-escolar-ipm.onrender.com/admin']
SITE_URL = os.environ.get('SITE_URL', 'https://ipm.onrender.com')

# Segurança (Produção/HTTPS) - Controlado pelo .env
USE_HTTPS = os.environ.get('USE_HTTPS', 'False') == 'True'

if USE_HTTPS:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_HSTS_SECONDS = 31536000 # 1 Ano
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
else:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False


# Application definition

INSTALLED_APPS = [
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'unfold.contrib.import_export',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'rest_framework_simplejwt',
    'apis.apps.ApisConfig',
]

# CORS Configuration
#CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', 'http://192.168.216.221:8000,http://localhost:3000,http://localhost:5173').split(',')
CORS_ALLOW_ALL_ORIGINS=True
CORS_ALLOW_CREDENTIALS = True

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

X_FRAME_OPTIONS = 'SAMEORIGIN'

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'postgres'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''), # Vazio se não houver no env
        'HOST': os.environ.get('DB_HOST', ''),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'postgres'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', ''),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}
"""

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'Africa/Luanda'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS=[
    os.path.join(BASE_DIR,STATIC_URL)
]
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Email Configuration for Real Email Sending (SMTP)
# As informações abaixo agora vêm do arquivo .env
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', 'False') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Workaround para erro de verificação de certificado SSL no ambiente local
if DEBUG:
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context




# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'apis.permissions.authentication.SchoolJWTAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
}
LOGIN="dashboard-academico/"
# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}


# =============================================================================
# DJANGO UNFOLD CONFIGURATION - Tema Verde Sofisticado
# =============================================================================

UNFOLD = {
 
    "SITE_TITLE": "Sistema de Gestão de Declarações",
    "SITE_HEADER": "Gestão de Declarações",
    "SITE_URL": "http://localhost:5173",
    "SITE_SYMBOL": "school", # Símbolo do Material Symbols
    "SHOW_HISTORY": True, # Mostra botão de histórico
    "SHOW_VIEW_ON_SITE": False, # Mostra botão ver no site
    #"THEME": "dark", # Tema padrão dark
    
    "SITE_ICON": {
        "light": lambda request: static("image/favicon.ico"),
        "dark": lambda request: static("image/favicon.ico"),
    },
    
    # SIDEBAR
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Dashboard",
                "separator": True,
                "items": [
                    {
                        "title": "Dashboards",
                        "icon": "dashboard",
                        "link": lambda request: "/dashboard-academico/",
                    },
                    {
                        "title": "Visão Geral",
                        "icon": "dashboard",
                        "link": lambda request: "/admin",
                    },
                ],
            },
            {
                "title": "Configuração da Instituição",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Departamentos",
                        "icon": "corporate_fare",
                        "link": lambda request: "/admin/apis/departamento/",
                    },
                    {
                        "title": "Secções",
                        "icon": "workspaces",
                        "link": lambda request: "/admin/apis/seccao/",
                    },
                    {
                        "title": "Áreas de Formação",
                        "icon": "account_tree",
                        "link": lambda request: "/admin/apis/areaformacao/",
                    },
                ],
            },
            {
                "title": "Pessoas",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Funcionários",
                        "icon": "badge",
                        "link": lambda request: "/admin/apis/funcionario/",
                    },
                    {
                        "title": "Cargos e Perfil",
                        "icon": "work",
                        "link": lambda request: "/admin/apis/cargo/",
                    },
                    {
                        "title": "Alunos",
                        "icon": "school",
                        "link": lambda request: "/admin/apis/aluno/",
                    },
                    {
                        "title": "Encarregados",
                        "icon": "supervisor_account",
                        "link": lambda request: "/admin/apis/encarregado/",
                    },
                ],
            },
            {
                "title": "Matrículas & Secretaria",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Inscrições (Candidatos)",
                        "icon": "how_to_reg",
                        "link": lambda request: "/admin/apis/inscricao/",
                    },
                    {
                        "title": "Matrículas",
                        "icon": "assignment_ind",
                        "link": lambda request: "/admin/apis/matricula/",
                    },
                ],
            },
            {
                "title": "Gestão Académica",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Cursos",
                        "icon": "menu_book",
                        "link": lambda request: "/admin/apis/curso/",
                    },
                    {
                        "title": "Classes e Períodos",
                        "icon": "stairs",
                        "link": lambda request: "/admin/apis/classe/",
                    },
                    {
                        "title": "Matrizes Curriculares",
                        "icon": "account_tree",
                        "link": lambda request: "/admin/apis/matrizcurricular/",
                    },
                    {
                        "title": "Disciplinas",
                        "icon": "subject",
                        "link": lambda request: "/admin/apis/disciplina/",
                    },
                    {
                        "title": "Prof. vs Disciplina",
                        "icon": "co_present",
                        "link": lambda request: "/admin/apis/professordisciplina/",
                    },
                    {
                        "title": "Turmas",
                        "icon": "groups",
                        "link": lambda request: "/admin/apis/turma/",
                    },
                    {
                        "title": "Salas",
                        "icon": "meeting_room",
                        "link": lambda request: "/admin/apis/sala/",
                    },
                ],
            },
            {
                "title": "Avaliações",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Notas & Pautas",
                        "icon": "grade",
                        "link": lambda request: "/admin/apis/nota/lancamento-massivo/",
                    },
                    {
                        "title": "Notas 13ª Classe",
                        "icon": "star",
                        "link": lambda request: "/admin/apis/nota/lancamento-13-classe/",
                    },
                    {
                        "title": "Registo de Notas",
                        "icon": "checklist",
                        "link": lambda request: "/admin/apis/nota/",
                    },
                    {
                        "title": "Faltas",
                        "icon": "event_busy",
                        "link": lambda request: "/admin/apis/faltaaluno/",
                    },
                ],
            },
            {
                "title": "Documentos Oficiais",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Solicitações Recebidas",
                        "icon": "description",
                        "link": lambda request: "/admin/apis/solicitacaodocumento/",
                    },
                    {
                        "title": "Documentos Emitidos",
                        "icon": "insert_drive_file",
                        "link": lambda request: "/admin/apis/documento/",
                    },
                ],
            },
            {
                "title": "Financeiro",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Faturas & Propinas",
                        "icon": "receipt",
                        "link": lambda request: "/admin/apis/fatura/",
                    },
                    {
                        "title": "Pagamentos",
                        "icon": "payment",
                        "link": lambda request: "/admin/apis/pagamento/",
                    },
                ],
            },
            {
                "title": "Biblioteca",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Acervo de Livros",
                        "icon": "book",
                        "link": lambda request: "/admin/apis/livro/",
                    },
                    {
                        "title": "Categorias",
                        "icon": "category",
                        "link": lambda request: "/admin/apis/categoria/",
                    },
                ],
            },
            {
                "title": "Sistema & Manutenção",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Definições Gerais",
                        "icon": "settings",
                        "link": lambda request: "/admin/apis/configuracaosistema/",
                    },
                    {
                        "title": "Notificações",
                        "icon": "notifications",
                        "link": lambda request: "/admin/apis/notificacao/",
                    },
                    {
                        "title": "Auditoria de Ações",
                        "icon": "history",
                        "link": lambda request: "/admin/apis/historico/",
                    },
                    {
                        "title": "Registo de Acessos",
                        "icon": "login",
                        "link": lambda request: "/admin/apis/historicologin/",
                    },
                ],
            },
        ],
    },
    
    # TEMA - Emerald Forest Professional
    "COLORS": {
        "primary": {
            "50": "236 253 245",
            "100": "209 250 229",
            "200": "167 243 208",
            "300": "110 231 183",
            "400": "52 211 153",
            "500": "16 185 129",   # Emerald Base
            "600": "5 150 105",
            "700": "4 120 87",
            "800": "6 95 70",
            "900": "6 78 59",
            "950": "2 44 34",
        },
        "font": {
            "subtle": "156 163 175", # cinza suave para textos secundários
        }
    },
    
    "STYLES": [
        lambda request: static("css/admin_custom.css"),
    ],
    
    # TABS
    "TABS": [
        {
            "models": [
                "apis.funcionario",
                "apis.aluno",
                "apis.encarregado",
            ],
            "items": [
                {
                    "title": "Funcionários",
                    "link": lambda request: "/admin/apis/funcionario/",
                },
                {
                    "title": "Alunos",
                    "link": lambda request: "/admin/apis/aluno/",
                },
                {
                    "title": "Encarregados",
                    "link": lambda request: "/admin/apis/encarregado/",
                },
            ],
        },
    ],

    # EXTENSIONS
    "EXTENSIONS": {
        "modeltranslation": {
            "flags": {
                "en": "🇬🇧",
                "pt": "🇦🇴",
            },
        },
    },
    
    # THEME
    #"THEME": "auto",  # light, dark, auto
    # DASHBOARD
    "DASHBOARD_CALLBACK": "apis.dashboard.dashboard_callback",
   
}

# Import static helper
from django.templatetags.static import static
