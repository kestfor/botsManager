import logging
import re


def parse_docker_ps(output: str) -> str:
    lines = output.strip().splitlines()
    logging.debug(f"lines: {lines}")
    if not lines:
        return "ℹ️ Нет запущенных сервисов."

    header = lines[0]
    splits = [m.start() for m in re.finditer(r'\s{2,}', header)]
    cols = []
    last = 0
    for idx in splits + [len(header)]:
        cols.append((last, idx))
        last = idx
    names = [header[a:b].strip() for a, b in cols]

    emoji_map = {
        'Up': '✅',
        'Exited': '❌',
        'Restarting': '🔄',
    }

    result = []
    for line in lines[1:]:
        fields = [line[a:b].strip() for a, b in cols]
        info = dict(zip(names, fields))
        state = info.get('State', info.get('STATUS', ''))
        em = 'ℹ️'
        for key, icon in emoji_map.items():
            if state.startswith(key):
                em = icon
                break

        name = info.get('Name', info.get('CONTAINER', '—'))
        ports = info.get('Ports', '')

        block = (
            f"{em} <b>{name}</b>\n"
            f"• <i>State:</i> {state}\n"
        )
        if ports:
            block += f"• <i>Ports:</i> {ports}\n"
        result.append(block)

    return "\n".join(result)
