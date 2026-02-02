"""
Redis configuration templates for deploy-vps plugin.
Generates redis.conf and redis-password.conf templates.
"""


def generate_redis_conf_template() -> str:
    """Generate redis.conf.template file content."""
    return '''# Redis Configuration for Production

# Memory Management
maxmemory 512mb
maxmemory-policy allkeys-lru

# Persistence Settings
appendonly yes
appendfsync everysec
save 900 1
save 300 10
save 60 10000

# Network
bind 0.0.0.0
port 6379

# Logging
loglevel notice

# Include password configuration (keeps password out of process list)
include /usr/local/etc/redis/redis-password.conf
'''


def generate_redis_password_conf_template() -> str:
    """Generate redis-password.conf.template file content."""
    return '''requirepass {{REDIS_PASSWORD}}
'''
