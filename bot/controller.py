import subprocess
from pathlib import Path
from typing import List, Dict

class ServiceController:
    def __init__(self, services: List[Dict]):
        # expect each dict to have at least 'name' and 'path', optional 'compose_file'
        self.services = {s['name']: s for s in services}

    def _run_compose(self, project: Dict, args: List[str]) -> subprocess.CompletedProcess:
        # fix default filename typo here
        compose_file = project.get('compose_file', 'docker-compose.yml')
        compose_path = Path(project['path']) / compose_file

        if not compose_path.exists():
            raise FileNotFoundError(f"Compose file not found: {compose_path}")

        cmd = ["docker", "compose", "-f", str(compose_path)] + args
        result = subprocess.run(cmd, capture_output=True, text=True)

        # optional: surface any non-zero exit code as an exception
        if result.returncode != 0:
            raise RuntimeError(
                f"Command `{ ' '.join(cmd) }` failed with exit code {result.returncode}:\n"
                f"{result.stderr.strip()}"
            )
        return result

    def status(self, name: str) -> str:
        proj = self.services.get(name)
        if not proj:
            return f"Service '{name}' not found"
        return self._run_compose(proj, ["ps"]).stdout

    def start(self, name: str) -> str:
        proj = self.services.get(name)
        if not proj:
            return f"Service '{name}' not found"
        return self._run_compose(proj, ["up", "-d"]).stdout

    def stop(self, name: str) -> str:
        proj = self.services.get(name)
        if not proj:
            return f"Service '{name}' not found"
        return self._run_compose(proj, ["stop"]).stdout

    def restart(self, name: str) -> str:
        proj = self.services.get(name)
        if not proj:
            return f"Service '{name}' not found"
        stop_out = self.stop(name)
        start_out = self.start(name)
        return f"Stopped:\n{stop_out}\nStarted:\n{start_out}"

    def list_services(self) -> List[str]:
        return list(self.services.keys())
