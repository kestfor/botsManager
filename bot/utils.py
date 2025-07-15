import logging
import re


def parse_docker_ps(output: str) -> str:
    lines = output.strip().splitlines()
    if not lines or len(lines) < 2:
        return "ℹ️ Нет запущенных сервисов."

    # Разбиваем заголовок и строки по 2+ пробелам
    header = lines[0]
    names = re.split(r"\s{2,}", header)

    emoji_map = {
        'Up': '✅',
        'Exited': '❌',
        'Restarting': '🔄',
    }

    result = []
    # Обрабатываем каждую строку-ресурс
    for line in lines[1:]:
        fields = re.split(r"\s{2,}", line)
        # дополняем, если полей меньше
        if len(fields) < len(names):
            fields += [''] * (len(names) - len(fields))
        info = dict(zip(names, fields))

        state = info.get('STATUS') or info.get('State', '')
        em = 'ℹ️'
        for key, icon in emoji_map.items():
            if state.startswith(key):
                em = icon
                break

        name = info.get('NAME') or info.get('Name', '')
        ports = info.get('PORTS', '')

        block = [f"{em} <b>{name}</b>", f"• <i>State:</i> {state}"]
        if ports:
            block.append(f"• <i>Ports:</i> {ports}")
        result.append("\n".join(block))

    return "\n\n".join(result)
