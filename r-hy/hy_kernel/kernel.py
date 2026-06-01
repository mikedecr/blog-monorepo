import ast
import sys
import traceback

import hy
from ipykernel.kernelbase import Kernel
from hy import __version__ as hy_version
from hy.compiler import hy_compile
from hy.reader import read_many


class HyKernel(Kernel):
    implementation = "hy"
    implementation_version = hy_version
    language = "hy"
    language_version = hy_version
    language_info = {
        "name": "hy",
        "mimetype": "text/x-hy",
        "file_extension": ".hy",
        "codemirror_mode": {"name": "scheme"},
        "pygments_lexer": "lisp",
    }
    banner = "Hy kernel - a Lisp dialect embedded in Python."

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.env = {}
        self.env.update(__builtins__ if isinstance(__builtins__, dict) else __builtins__.__dict__)
        self.env['hy'] = hy
        self.env['__name__'] = '__main__'

    def do_execute(self, code, silent, store_history=True, user_expressions=None, allow_stdin=False):
        self._result = None
        if not code.strip():
            return self._ok()

        old_displayhook = sys.displayhook
        sys.displayhook = self._displayhook

        try:
            tokens = read_many(code)
            _ast = hy_compile(tokens, "__main__", root=ast.Interactive)
            code_obj = compile(_ast, f"<hy-cell-{self.execution_count}>", "single")
            exec(code_obj, self.env)
        except Exception as e:
            tb = traceback.format_exc()
            if not silent:
                self.send_response(self.iopub_socket, "stream", {"name": "stderr", "text": tb})
            sys.displayhook = old_displayhook
            return self._error(e)

        sys.displayhook = old_displayhook

        if not silent and self._result is not None:
            self.send_response(self.iopub_socket, "execute_result", {
                "execution_count": self.execution_count,
                "data": {"text/plain": repr(self._result)},
                "metadata": {},
            })
        return self._ok()

    def _displayhook(self, value):
        if value is None:
            return
        self._result = value
        self.env["_"] = value

    def do_complete(self, code, cursor_pos):
        return {"status": "ok", "cursor_start": cursor_pos, "cursor_end": cursor_pos, "matches": []}

    def _ok(self):
        return {"status": "ok", "execution_count": self.execution_count, "payload": [], "user_expressions": {}}

    def _error(self, e):
        return {
            "status": "error",
            "execution_count": self.execution_count,
            "ename": type(e).__name__,
            "evalue": str(e),
            "traceback": traceback.format_exc().split("\n"),
        }


if __name__ == "__main__":
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=HyKernel)
