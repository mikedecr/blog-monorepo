import json
import sys
from pathlib import Path


def install_kernel():
    kernel_dir = (
        Path(sys.prefix) / "share" / "jupyter" / "kernels" / "hy"
    )

    answer = input(
        f"Install Hy kernel spec at {kernel_dir}? [y/N] "
    )
    if answer.lower() not in ("y", "yes"):
        print("Aborted.")
        return

    kernel_dir.mkdir(parents=True, exist_ok=True)

    kernel_json = {
        "argv": [
            sys.executable,
            "-m",
            "hy_kernel.kernel",
            "-f",
            "{connection_file}",
        ],
        "display_name": "Hy",
        "language": "hy",
        "metadata": {"debugger": False},
    }

    (kernel_dir / "kernel.json").write_text(
        json.dumps(kernel_json, indent=2) + "\n"
    )
    print(f"Installed Hy kernel spec at {kernel_dir}")
    print(f"Python: {sys.executable}")
