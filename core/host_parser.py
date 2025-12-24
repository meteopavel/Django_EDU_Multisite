def parse_host_map(raw_map: str):
    host_map = {}
    raw_map = raw_map.strip().replace('\\', '')
    if not raw_map:
        return host_map
    for line in raw_map.splitlines():
        line = line.strip()
        if not line or ':' not in line:
            continue
        slug, hosts_str = line.split(':', 1)
        slug = slug.strip()
        hosts = [h.strip() for h in hosts_str.split(',') if h.strip()]
        for host_with_port in hosts:
            host = host_with_port.split(':')[0].lower()  # убираем порт!
            host_map[host] = slug
    return host_map

def get_allowed_hosts_from_map(raw_map: str):
    return list(parse_host_map(raw_map).keys())