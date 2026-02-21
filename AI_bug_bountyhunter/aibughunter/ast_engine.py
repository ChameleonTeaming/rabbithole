import ast
import os
from aibughunter.utils import Logger

class ASTScanner(ast.NodeVisitor):
    def __init__(self, file_path):
        self.file_path = file_path
        self.findings = []
        self.code_lines = []

    def scan(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.code_lines = f.readlines()
                f.seek(0)
                tree = ast.parse(f.read(), filename=self.file_path)
            
            self.visit(tree)
            return self.findings
        except SyntaxError as e:
            Logger.warning(f"Syntax Error parsing {self.file_path}: {e}")
            return []
        except Exception as e:
            Logger.error(f"AST Scan failed for {self.file_path}: {e}")
            return []

    def _get_line_content(self, lineno):
        if 0 <= lineno - 1 < len(self.code_lines):
            return self.code_lines[lineno - 1].strip()
        return ""

    def visit_Call(self, node):
        """
        Visits every function call in the code.
        Checks for: eval, exec, os.system, app.run(debug=True), cursor.execute(insecure)
        """
        func_name = self._get_func_name(node.func)

        # 1. Dangerous Functions
        dangerous_funcs = ["eval", "exec", "os.system", "subprocess.call", "subprocess.Popen"]
        if func_name in dangerous_funcs:
            # Check if using literal_eval (safe)
            if func_name == "ast.literal_eval":
                pass 
            else:
                self.findings.append({
                    "type": "dangerous_function",
                    "file": self.file_path,
                    "line": node.lineno,
                    "content": self._get_line_content(node.lineno),
                    "details": f"Usage of {func_name} detected via AST",
                    "severity": "HIGH"
                })

        # 2. Flask Debug Mode
        if "run" in func_name: # Matches app.run, generic.run
            for keyword in node.keywords:
                if keyword.arg == "debug":
                    # Check if value is True (Constant)
                    if isinstance(keyword.value, ast.Constant) and keyword.value.value is True:
                        self.findings.append({
                            "type": "flask_debug",
                            "file": self.file_path,
                            "line": node.lineno,
                            "content": self._get_line_content(node.lineno),
                            "details": "Flask debug mode enabled (AST confirmed)",
                            "severity": "HIGH"
                        })

        # 3. SQL Injection (cursor.execute with concatenation)
        if "execute" in func_name:
            if node.args:
                arg0 = node.args[0]
                # Check for string concatenation (BinOp with Add) e.g. "SELECT..." + var
                if isinstance(arg0, ast.BinOp) and isinstance(arg0.op, ast.Add):
                     self.findings.append({
                        "type": "sql_injection",
                        "file": self.file_path,
                        "line": node.lineno,
                        "content": self._get_line_content(node.lineno),
                        "details": "SQL query construction using concatenation detected via AST",
                        "severity": "CRITICAL"
                    })
                # Check for f-strings (JoinedStr) e.g. f"SELECT... {var}"
                elif isinstance(arg0, ast.JoinedStr):
                    self.findings.append({
                        "type": "sql_injection",
                        "file": self.file_path,
                        "line": node.lineno,
                        "content": self._get_line_content(node.lineno),
                        "details": "SQL query construction using f-string detected via AST",
                        "severity": "CRITICAL"
                    })

        self.generic_visit(node)

    def _get_func_name(self, node):
        """Helper to recursively get function name (e.g., 'os.system' from Attribute)."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_func_name(node.value)}.{node.attr}"
        return ""

class AdvancedAnalyzer:
    def __init__(self, target_dir):
        self.target_dir = target_dir
        self.findings = []

    def scan(self):
        Logger.header(f"Starting Advanced AST Scan on: {self.target_dir}")
        
        if os.path.isfile(self.target_dir):
            if self.target_dir.endswith(".py"):
                scanner = ASTScanner(self.target_dir)
                self.findings.extend(scanner.scan())
        else:
            for root, _, files in os.walk(self.target_dir):
                if "venv" in root or ".git" in root or "__pycache__" in root:
                    continue
                for file in files:
                    if file.endswith(".py"):
                        scanner = ASTScanner(os.path.join(root, file))
                        self.findings.extend(scanner.scan())
        return self.findings
