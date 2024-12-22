# Add schemes for CORS_ALLOWED_ORIGINS
def format_cors_origin(host):
    host = host.strip()
    if not host.startswith(('http://', 'https://')):
        # Check if host contains port number (like localhost:8000)
        is_local = any(local in host for local in ['localhost', '127.0.0.1', '0.0.0.0'])
        return f"http://{host}" if is_local else f"https://{host}"
    return host

def format_allowed_hosts(hosts):
    return list(set(host.strip().split(':')[0] for host in hosts.split(",")))
