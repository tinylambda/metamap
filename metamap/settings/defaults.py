"""
Django settings for metamap project.

Generated by 'django-admin startproject' using Django 4.0.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
import atexit
import configparser
import copy
import os
import tempfile
from pathlib import Path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
from core.utils.config import ConfigWriterWithRepeatKeys

OS_CPU_COUNT = os.cpu_count()

TEMPDIR = tempfile.gettempdir()


BASE_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = (BASE_DIR / "..").resolve()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-h2*(lfkp=u-@8#cmsx_ouq+r*aq#csvlls-a^1#s6bc9)oqtl4"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "channels",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_prometheus",
    "django_data",
    "ninja",
    "ninja_extra",
    "account",
    "core",
    "access",
    "server",
]

MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.middleware.CoreMiddleware",
    # "core.middleware.simple_middleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]

MAIN_MODULE_NAME = "metamap"

ROOT_URLCONF = f"{MAIN_MODULE_NAME}.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# https://docs.djangoproject.com/en/4.0/ref/settings/#wsgi-application

WSGI_APPLICATION = f"{MAIN_MODULE_NAME}.wsgi.application"

# https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/

ASGI_APPLICATION = f"{MAIN_MODULE_NAME}.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                "redis://127.0.0.1:6379/0",
                "redis://127.0.0.1:6379/1",
            ],
            "expiry": 60,
            "group_expiry": 86400,
            "capacity": 100,
            "channel_capacity": {},
        },
    },
}

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = "static/"

# Where the static files go to when executing python manage.py collectstatic
# https://docs.djangoproject.com/en/4.0/ref/settings/#std:setting-STATIC_ROOT

STATIC_ROOT = f"/{TEMPDIR}/{MAIN_MODULE_NAME}/static_root/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Use custom user model
# https://docs.djangoproject.com/en/4.0/topics/auth/customizing/#substituting-a-custom-user-model
AUTH_USER_MODEL = "account.User"

# Logging
# https://docs.djangoproject.com/en/4.0/topics/logging/#logging

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "{levelname} {asctime} {module} {filename} {lineno} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        }
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}


WSGI_APPLICATION_REPR = WSGI_APPLICATION.replace(".application", ":application")

WSGI_SERVICE_PROCESSES = max(OS_CPU_COUNT - 1, 1)

WSGI_SERVICE_THREADS_PER_PROCESS = 32

ASGI_SERVICE_PROCESSES = max(OS_CPU_COUNT - 1, 1)

# This is the content of Gunicorn conf file, a valid Python file
# https://docs.gunicorn.org/en/stable/settings.html#settings
GUNICORN_CONFIG = f"""
# The socket to bind. can bind to multiple addresses
bind = ['127.0.0.1:8000', ]

# The maximum number of pending connections.
backlog = 2048

# The number of worker processes for handling requests.
workers = {WSGI_SERVICE_PROCESSES}

# The type of workers to use.
worker_class = 'sync'

# The number of worker threads for handling requests.
# If you try to use the sync worker type and set the threads setting to more than 1, 
# the gthread worker type will be used instead.
threads = {WSGI_SERVICE_THREADS_PER_PROCESS}

# The maximum number of simultaneous clients.
# This setting only affects the Eventlet and Gevent worker types.
worker_connections = 1000

# The maximum number of requests a worker will process before restarting.
max_requests = 0

# The maximum jitter to add to the max_requests setting. to avoid all workers restarting at the same time.
max_requests_jitter = 0

# Workers silent for more than this many seconds are killed and restarted.
timeout = 30

# After receiving a restart signal, workers have this much time to finish serving requests
graceful_timeout = 30

# The number of seconds to wait for requests on a Keep-Alive connection. 
# When Gunicorn is deployed behind a load balancer, it often makes sense to set this to a higher value.
# sync worker does not support persistent connections and will ignore this option.
keepalive = 60

# A WSGI application path in pattern $(MODULE_NAME):$(VARIABLE_NAME).
wsgi_app = '{WSGI_APPLICATION_REPR}'

# Restart workers when code changes. This setting is intended for development
reload = False

# The implementation that should be used to power reload.
reload_engine = 'auto'

# Extends reload option to also watch and reload on additional files
reload_extra_files = []

# Install a trace function that spews every line executed by the server.
# This is the nuclear option.
spew = False

# Check the configuration and exit. 
# The exit status is 0 if the configuration is correct, and 1 if the configuration is incorrect.
check_config = False

# Print the configuration settings as fully resolved. Implies check_config.
print_config = False

# The Access log file to write to. '-' means log to stdout.
accesslog = '-'

# Disable redirect access logs to syslog.
disable_redirect_access_to_syslog = False

# The access log format. (https://docs.gunicorn.org/en/stable/settings.html#access-log-format)
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# The Error log file to write to.
# Using '-' for FILE makes gunicorn log to stderr.
errorlog = '-'

# The granularity of Error log outputs.
loglevel = 'info'

# Redirect stdout/stderr to specified file in errorlog.
capture_output = False

# The logger you want to use to log events in Gunicorn.
logger_class = 'gunicorn.glogging.Logger'

# The log config file to use. Gunicorn uses the standard Python logging module’s Configuration file format.
logconfig = None

# The log config dictionary to use, using the standard Python logging module’s dictionary configuration format.
logconfig_dict = {{}}

# Address to send syslog messages. (https://docs.gunicorn.org/en/stable/settings.html#syslog-addr)
syslog_addr = 'udp://localhost:514'

# Send Gunicorn logs to syslog.
syslog = False

# Makes Gunicorn use the parameter as program-name in the syslog entries.
syslog_prefix = None

# Syslog facility name
syslog_facility = 'user'

# Enable stdio inheritance.
enable_stdio_inheritance = False

# host:port of the statsd server to log to.
statsd_host = None

# A comma-delimited list of datadog statsd (dogstatsd) tags to append to statsd metrics.
dogstatsd_tags = ''

# Prefix to use when emitting statsd metrics (a trailing . is added, if not provided).
statsd_prefix = ''

# A base to use with setproctitle for process naming.
proc_name = '{MAIN_MODULE_NAME}'

# Internal setting that is adjusted for each type of application.
default_proc_name = 'gunicorn'

# The maximum size of HTTP request line in bytes.
limit_request_line = 4094

# Limit the number of HTTP headers fields in a request.
limit_request_fields = 100

# Limit the allowed size of an HTTP request header field.
limit_request_field_size = 8190

# Load application code before the worker processes are forked.
# By preloading an application you can save some RAM resources as well as speed up server boot times. 
# Although, if you defer application loading to each worker process, 
# you can reload your application code easily by restarting workers.
preload_app = True

# Disables the use of sendfile().
# If not set, the value of the SENDFILE environment variable is used to enable or disable its usage.
sendfile = None

# Set the SO_REUSEPORT flag on the listening socket.
reuse_port = True

# Change directory to specified directory before loading apps.
chdir = '{str(BASE_DIR)}'

# Daemonize the Gunicorn process.
daemon = False

# Set environment variables in the execution environment.
# Should be a list of strings in the key=value format.
raw_env = []

# A filename to use for the PID file.
# If not set, no PID file will be written.
pidfile = None

# A directory to use for the worker heartbeat temporary file.
# If not set, the default temporary directory will be used.
worker_tmp_dir = None

# Switch worker processes to run as this user.
# user = 'felix'

# Switch worker process to run as this group.
# group = 'felix'

# A bit mask for the file mode on files written by Gunicorn.
# umask = 0022

# If true, set the worker process’s group access list with all of the groups 
# of which the specified username is a member, plus the specified group id.
# initgroups = False

# Directory to store temporary request data as they are read.
# If not specified, Gunicorn will choose a system generated temporary directory.
# This may disappear in the near future.
tmp_upload_dir = None

# A dictionary containing headers and values that the front-end proxy uses to indicate HTTPS requests.
secure_scheme_headers = {{
    'X-FORWARDED-PROTOCOL': 'ssl', 
    'X-FORWARDED-PROTO': 'https', 
    'X-FORWARDED-SSL': 'on',
}}

# Front-end’s IPs from which allowed to handle set secure headers. (comma separate).
# Set to * to disable checking of Front-end IPs
forwarded_allow_ips = '*'

# A comma-separated list of directories to add to the Python path.
pythonpath = None

# Load a PasteDeploy config file. 
paste = None

# Enable detect PROXY protocol
proxy_protocol = False

# Front-end’s IPs from which allowed accept proxy requests (comma separate).
# Set to * to disable checking of Front-end IPs 
proxy_allow_ips = '*'

# Set a PasteDeploy global config variable in key=value form.
raw_paste_global_conf = []

# Strip spaces present between the header name and the the :.
strip_header_spaces = False
"""
GUNICORN_CONFIG_FILENAME = os.path.join(
    BASE_DIR, "run", f"gunicorn_{MAIN_MODULE_NAME}.py"
)

UWSGI_CONFIG = ConfigWriterWithRepeatKeys()
UWSGI_CONF_FILENAME = os.path.join(BASE_DIR, "run", f"uwsgi.{MAIN_MODULE_NAME}.ini")

UWSGI_INSTANCE_CONFIG = {
    "env": f"DJANGO_SETTINGS_MODULE={MAIN_MODULE_NAME}.settings",
    "chdir": str(BASE_DIR),
    "module": f"{WSGI_APPLICATION_REPR}",
    "master": "true",
    "pidfile": os.path.join(BASE_DIR, "run", f"uwsgi.{MAIN_MODULE_NAME}.pid"),
    "http": ["127.0.0.1:8000"],
    "socket": "127.0.0.1:0",
    "harakiri": "20",
    "vacuum": "true",
    "processes": f"{WSGI_SERVICE_PROCESSES}",
    # 'threads': f'{WSGI_SERVICE_THREADS_PER_PROCESS}',
    "enable-threads": "false",  # Running uWSGI with the threads options will automatically enable threading support
    "no-threads-wait": "true",
    "max-requests": "5000",
    "max-requests-delta": "3",
    "lazy-apps": "true",
    "touch-chain-reload": os.path.join(
        BASE_DIR, "run", f"uwsgi.{MAIN_MODULE_NAME}.touch"
    ),
    "disable-logging": "false",
    "log-master": "true",  # delegate logging to master process
    "stats": "127.0.0.1:9191",
    "stats-http": "true",
    "static-map": [f"/static={STATIC_ROOT}"],
}

UWSGI_CONFIG.add_section("uwsgi")
for setting_key in UWSGI_INSTANCE_CONFIG:
    setting_value = UWSGI_INSTANCE_CONFIG[setting_key]
    UWSGI_CONFIG.set("uwsgi", setting_key, setting_value)


CIRCUSD_CONFIG = configparser.ConfigParser(interpolation=None)
CIRCUSD_CONF_FILENAME = os.path.join(BASE_DIR, "run", f"circusd.{MAIN_MODULE_NAME}.ini")
CIRCUSD_PID_FILENAME = os.path.join(BASE_DIR, "run", f"circusd.{MAIN_MODULE_NAME}.pid")
CIRCUSD_LOG_ROOT_DIR = f"/tmp/log/{MAIN_MODULE_NAME}/circus"

CIRCUSD_STATIC_CONFIG_LIST = [
    {
        "name": "circus",
        "settings": {
            "endpoint": "tcp://127.0.0.1:5555",
            "endpoint_owner": "None",
            "pubsub_endpoint": "tcp://127.0.0.1:5556",
            "statsd": "False",
            "stats_endpoint": "tcp://127.0.0.1:5557",
            "stats_close_outputs": "False",
            "check_delay": "5",
            "stream_backend": "thread",
            "warmup_delay": "0",
            "debug": "False",
            "debug_gc": "False",
            "pidfile": os.path.join(BASE_DIR, "run", f"circusd.{MAIN_MODULE_NAME}.pid"),
            "umask": "002",
            "loglevel": "INFO",
            "logoutput": "-",
            "loggerconfig": "",
        },
    },
]

for CIRCUSD_STATIC_CONFIG in CIRCUSD_STATIC_CONFIG_LIST:
    section_name = CIRCUSD_STATIC_CONFIG["name"]
    settings = CIRCUSD_STATIC_CONFIG["settings"]

    CIRCUSD_CONFIG.add_section(section_name)
    for setting_key in settings:
        setting_value = settings[setting_key]
        CIRCUSD_CONFIG.set(section_name, setting_key, setting_value)


CIRCUS_WATCHER_DEFAULT_SETTINGS = {
    "cmd": "/bin/cat",
    "args": "",
    "shell": "False",
    "shell_args": "None",
    "working_dir": str(BASE_DIR),
    # 'uid': '',  # current uid is the default
    # 'gid': '',  # current gid is the default
    "copy_env": "True",  # If true, the local env vars will be copied and passed to the workers when spawning them.
    "copy_path": "False",  # If true, sys.path is passed to the subprocess env using PYTHONPATH. copy_env has to be True
    "warmup_delay": "1",
    "autostart": "False",
    "numprocesses": "1",
    "stderr_stream.class": "FileStream",
    "stderr_stream.filename": os.path.join(
        CIRCUSD_LOG_ROOT_DIR, "{watcher_name:s}.error.log"
    ),
    "stderr_stream.time_format": "%Y-%m-%d %H:%M:%S",
    "stderr_stream.max_bytes": "1073741824",
    "stderr_stream.backup_count": "5",
    "stdout_stream.class": "FileStream",
    "stdout_stream.filename": os.path.join(
        CIRCUSD_LOG_ROOT_DIR, "{watcher_name:s}.info.log"
    ),
    "stdout_stream.time_format": "%Y-%m-%d %H:%M:%S",
    "stdout_stream.max_bytes": "1073741824",
    "stdout_stream.backup_count": "5",
    "close_child_stdin": "True",
    "close_child_stdout": "False",
    "close_child_stderr": "False",
    "send_hup": "False",
    "stop_signal": "INT",
    "stop_children": "False",
    "max_retry": "2",
    "graceful_timeout": "30",
    "priority": "10",
    "singleton": "True",
    "use_sockets": "False",
    # 'max_age': '100000',  # Default disabled
    # 'max_age_variance': ,  # Variate above
    "virtualenv": os.path.join(
        BASE_DIR, "venv"
    ),  # root of a virtualenv directory. need copy_env to be True
    # 'virtualenv_py_ver': '',  # specify python version, must be used with virtualenv
    "respawn": "True",  # If set to False, the processes handled by a watcher will not be respawned automatically.
    # 'use_papa': 'False',
}

CIRCUS_SOCKETS = [
    {
        "name": f"{MAIN_MODULE_NAME}_ASGI",
        "settings": {
            "host": "127.0.0.1",
            "port": "20000",
        },
    }
]

CIRCUS_ENVS = [
    {"name": f"{MAIN_MODULE_NAME}_HTTP", "settings": {}},
    {"name": f"{MAIN_MODULE_NAME}_ASGI", "settings": {}},
]

CIRCUS_WATCHERS = [
    {
        "name": f"gunicorn",
        "settings": {
            "cmd": "python manage.py gunicorn start",
            "stop_signal": "INT",
            "singleton": "True",
            "autostart": "True",
            "use_sockets": "False",
        },
    },
    {
        "name": f"daphne",
        "settings": {
            "cmd": f"python manage.py daphne start --fd $(circus.sockets.{MAIN_MODULE_NAME}_ASGI) "
            f"--app {MAIN_MODULE_NAME}.asgi:application",
            "use_sockets": "True",
            "singleton": "False",
            "autostart": "True",
            "numprocesses": f"{ASGI_SERVICE_PROCESSES}",
            "priority": "1",
        },
    },
]

for CIRCUS_SOCKET in CIRCUS_SOCKETS:
    name = CIRCUS_SOCKET["name"]
    settings = CIRCUS_SOCKET["settings"]
    section_name = f"socket:{name}"

    CIRCUSD_CONFIG.add_section(section_name)
    for setting_key in settings:
        setting_value = settings[setting_key]
        CIRCUSD_CONFIG.set(section_name, setting_key, setting_value)

for CIRCUS_ENV in CIRCUS_ENVS:
    name = CIRCUS_ENV["name"]
    settings = CIRCUS_ENV["settings"]
    section_name = f"env:{name}"
    for setting_key in settings:
        setting_value = settings[setting_key]
        CIRCUSD_CONFIG.set(section_name, setting_key, setting_value)

for CIRCUS_WATCHER in CIRCUS_WATCHERS:
    name = CIRCUS_WATCHER["name"]
    watcher_settings = CIRCUS_WATCHER["settings"]
    settings = copy.copy(CIRCUS_WATCHER_DEFAULT_SETTINGS)
    settings.update(watcher_settings)
    section_name = f"watcher:{name}"
    render_context = {"watcher_name": name}

    CIRCUSD_CONFIG.add_section(section_name)
    for setting_key in settings:
        setting_value = settings[setting_key]
        setting_value = setting_value.format(**render_context)
        CIRCUSD_CONFIG.set(section_name, setting_key, setting_value)


ETCD_KWARGS = {
    "host": "localhost",
    "port": 2379,
}

# Where to register all types of services
SERVICE_ROOT = f"/{MAIN_MODULE_NAME}/services/"

# Distributed locks used in this project
SERVICE_LOCK_ROOT = f"/{MAIN_MODULE_NAME}/locks/"

# How many seconds a service's lease
SERVICE_LEASE_DEFAULT_SECONDS = 20

# A live service will refresh its lease when TTL is less than
SERVICE_LEASE_REFRESH_WHEN_SMALLER_THAN = 5

# Used for generating nginx configuration files for http and websocket service
# Use python manage.py nginx create to generate the configuration files and copy them to your nginx conf.d directory
NGINX_HTTP_CONF_FILENAME = os.path.join(
    BASE_DIR, "run", f"nginx-http-{MAIN_MODULE_NAME}.conf"
)

NGINX_WEBSOCKET_CONF_FILENAME = os.path.join(
    BASE_DIR, "run", f"nginx-websocket-{MAIN_MODULE_NAME}.conf"
)

NGINX_HTTP_SERVER_NAME = "game-http.domain.com"

NGINX_WEBSOCKET_SERVER_NAME = "game-ws.domain.com"


PROMETHEUS_METRIC_NAMESPACE = "metamap"

PROMETHEUS_LATENCY_BUCKETS = (
    0.01,
    0.025,
    0.05,
    0.075,
    0.1,
    float("inf"),
)


@atexit.register
def cleanup():
    """
    Will be called before the worker process exits
    Add more cleanup as you need.
    """
    pass
