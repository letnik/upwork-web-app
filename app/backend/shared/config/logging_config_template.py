# Конфігурація логування для сервісу
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "json": {
            "format": "%(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "detailed",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "detailed",
            "filename": "logs/service.log",
            "maxBytes": 52428800,  # 50MB
            "backupCount": 10
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "detailed",
            "filename": "logs/service_error.log",
            "maxBytes": 20971520,  # 20MB
            "backupCount": 20
        },
        "security_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "WARNING",
            "formatter": "detailed",
            "filename": "logs/service_security.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 30
        },
        "performance_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "detailed",
            "filename": "logs/service_performance.log",
            "maxBytes": 20971520,  # 20MB
            "backupCount": 10
        },
        "api_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "detailed",
            "filename": "logs/service_api.log",
            "maxBytes": 31457280,  # 30MB
            "backupCount": 5
        },
        "database_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "detailed",
            "filename": "logs/service_database.log",
            "maxBytes": 20971520,  # 20MB
            "backupCount": 10
        }
    },
    "loggers": {
        "": {
            "level": "INFO",
            "handlers": ["console", "file", "error_file"]
        },
        "security": {
            "level": "WARNING",
            "handlers": ["security_file"],
            "propagate": False
        },
        "performance": {
            "level": "INFO",
            "handlers": ["performance_file"],
            "propagate": False
        },
        "api": {
            "level": "INFO",
            "handlers": ["api_file"],
            "propagate": False
        },
        "database": {
            "level": "INFO",
            "handlers": ["database_file"],
            "propagate": False
        }
    }
}
