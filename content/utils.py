from django.conf import settings


def get_host_map():
    host_map = {}
    raw = settings.HOST_TO_DEPARTMENT_MAP
    raw = raw.strip().replace('\\', '')
    if not raw:
        return host_map
    for part in raw.splitlines():
        part = part.strip()
        if not part or ':' not in part:
            continue
        slug, hosts_str = part.split(':', 1)
        slug = slug.strip()
        hosts = [h.strip() for h in hosts_str.split(',') if h.strip()]
        for host in hosts:
            host_map[host.lower()] = slug
    return host_map
