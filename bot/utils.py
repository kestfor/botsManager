import re

def parse_docker_ps(output: str) -> str:
    """
    Парсит вывод `docker compose ps` и возвращает строку с форматированием для Telegram.
    Добавляет эмодзи по статусам контейнеров.
    """
    lines = output.strip().splitlines()
    if not lines:
        return "ℹ️ Нет запущенных сервисов."

    # первая строка — заголовки, запоминаем позиции колонок
    header = lines[0]
    # находим границы колонок по позициям первых пробелов
    splits = [m.start() for m in re.finditer(r'\s{2,}', header)]
    cols = []
    last = 0
    for idx in splits + [len(header)]:
        cols.append((last, idx))
        last = idx
    # названия колонок
    names = [header[a:b].strip() for a, b in cols]

    emoji_map = {
        'Up': '✅',       # работающий
        'Exited': '❌',   # остановлен
        'Restarting': '🔄', # перезапуск
        # можно добавить свои статусы...
    }

    result = []
    # обрабатываем каждую строку-ресурс
    for line in lines[1:]:
        fields = [line[a:b].strip() for a, b in cols]
        info = dict(zip(names, fields))

        # Определяем эмодзи по началу статусной колонки
        state = info.get('State', info.get('STATUS', ''))
        em = 'ℹ️'
        for key, icon in emoji_map.items():
            if state.startswith(key):
                em = icon
                break

        name = info.get('Name', info.get('CONTAINER', '—'))
        cmd = info.get('Command', '')
        ports = info.get('Ports', '')

        # Формируем текст
        block = (
            f"{em} <b>{name}</b>\n"
            f"{'•'} <i>State:</i> {state}\n"
        )
        if ports:
            block += f"• <i>Ports:</i> {ports}\n"
        # можно добавить ещё поля по желанию
        result.append(block)

    return "\n".join(result)