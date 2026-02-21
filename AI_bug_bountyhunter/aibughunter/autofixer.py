import os
import re
from aibughunter.utils import Logger

class AutoFixer:
    def __init__(self, findings=None):
        self.findings = findings if findings else []
        self.applied_fixes = 0

    def apply_fixes(self):
        """Applies fixes to all findings in the list."""
        Logger.header("Starting Auto-Remediation")
        findings_by_file = self._group_by_file(self.findings)
        
        for file_path, file_findings in findings_by_file.items():
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                new_content = self._apply_patches_to_content(content, file_findings, file_path)
                
                if new_content != content:
                    with open(file_path, 'w') as f:
                        f.write(new_content)
                    self.applied_fixes += 1
                    Logger.info(f"Applied fixes to {file_path}")
                    
            except Exception as e:
                Logger.error(f"Failed to fix {file_path}: {str(e)}")

        if self.applied_fixes > 0:
            Logger.success(f"Auto-Remediation Complete. Fixed issues in {self.applied_fixes} files.")

    def preview_fix(self, file_path, finding):
        """Returns (original_code, fixed_code) for a single finding."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Apply just this one fix
            new_content = self._apply_patches_to_content(content, [finding], file_path)
            return content, new_content
        except Exception as e:
            return str(e), str(e)

    def _group_by_file(self, findings):
        grouped = {}
        for f in findings:
            path = f.get('file')
            if path:
                if path not in grouped:
                    grouped[path] = []
                grouped[path].append(f)
        return grouped

    def _apply_patches_to_content(self, content, findings, file_path):
        imports_to_add = set()
        modified_content = content
        
        env_path = os.path.join(os.path.dirname(file_path), ".env")

        for finding in findings:
            ftype = finding['type']
            
            if ftype == 'flask_debug':
                modified_content = re.sub(r'debug\s*=\s*True', 'debug=False', modified_content)

            elif ftype == 'django_allowed_hosts':
                pattern = r'ALLOWED_HOSTS\s*=\s*\[.*\[\'"\*\'"\].*\]'
                if re.search(pattern, modified_content):
                    modified_content = re.sub(pattern, "ALLOWED_HOSTS = ['127.0.0.1', 'localhost']", modified_content)

            elif ftype == 'insecure_random':
                if 'random.choice' in modified_content:
                    modified_content = modified_content.replace('random.choice', 'secrets.choice')
                    imports_to_add.add('secrets')

            elif ftype == 'dangerous_function':
                if 'eval(' in modified_content:
                    # Match eval( not preceded by literal_ or .
                    # Using a simpler replacement since lookbehind is tricky in re.sub sometimes
                    # We iterate to find all eval(
                    # But actually, finding['line'] could tell us WHERE to look if we passed it.
                    # For now, regex replacement:
                    modified_content = re.sub(r'(?<!literal_)eval\(', 'ast.literal_eval(', modified_content)
                    imports_to_add.add('ast')

            elif ftype == 'hardcoded_secret':
                match = re.search(r'(?i)([a-z0-9_]*(?:api_key|secret|password|token)[a-z0-9_]*)\s*=\s*["\']([a-zA-Z0-9_\-!@#$%^&*]{8,})["\']', modified_content)
                if match:
                    var_name = match.group(1)
                    secret_val = match.group(2)
                    self._append_to_env(env_path, var_name, secret_val)
                    modified_content = modified_content.replace(match.group(0), f'{var_name} = os.getenv("{var_name}")')
                    imports_to_add.add('os')
                    imports_to_add.add('dotenv_loader')

            elif ftype == 'sql_injection':
                # 1. F-STRING
                f_pattern = r'\.execute\(f(["\'])(.*?)\{([a-zA-Z_0-9]+)\}(.*?)\1\)'
                if re.search(f_pattern, modified_content):
                    modified_content = re.sub(f_pattern, r'.execute("\2?", (\3,))', modified_content)
                
                # 2. INLINE CONCATENATION: .execute("..." + var)
                # Matches .execute( QUOTE ... QUOTE + VAR )
                concat_match = re.search(r'\.execute\((["\'])(.*?)\1\s*\+\s*([a-zA-Z_0-9]+)\)', modified_content)
                if concat_match:
                    quote = concat_match.group(1)
                    query = concat_match.group(2)
                    var = concat_match.group(3)
                    new_code = f'.execute({quote}{query}?{quote}, ({var},))'
                    modified_content = modified_content.replace(concat_match.group(0), new_code)

                # 3. VARIABLE ASSIGNMENT
                else:
                    sql_match = re.search(r'query\s*=\s*(["\'])(SELECT.*?)\s*[\'"]\s*\+\s*([a-zA-Z_]+)\s*\+\s*[\'"][\'"]', modified_content)
                    if not sql_match:
                        sql_match = re.search(r'query\s*=\s*(["\'])(SELECT.*?)\1\s*\+\s*([a-zA-Z_]+)\s*\+\s*\1.*?\1', modified_content)
                    if sql_match:
                        quote_char = sql_match.group(1)
                        query_start = sql_match.group(2)
                        var_name = sql_match.group(3)
                        if query_start.endswith("'" ) or query_start.endswith('"'):
                            query_start = query_start[:-1]
                        new_line = f'query = {quote_char}{query_start}?{quote_char}'
                        modified_content = modified_content.replace(sql_match.group(0), new_line)
                        exec_pattern = r'cursor\.execute\(query\)'
                        if re.search(exec_pattern, modified_content):
                            modified_content = re.sub(exec_pattern, f'cursor.execute(query, ({var_name},))', modified_content)
                
        if imports_to_add:
            lines = modified_content.splitlines()
            last_import_idx = 0
            has_dotenv = False
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    last_import_idx = i
                if 'load_dotenv' in line:
                    has_dotenv = True
            for imp in imports_to_add:
                if imp == 'dotenv_loader':
                    if not has_dotenv:
                        lines.insert(last_import_idx + 1, "from dotenv import load_dotenv; load_dotenv()")
                elif f"import {imp}" not in modified_content:
                    lines.insert(last_import_idx + 1, f"import {imp}")
            modified_content = "\n".join(lines)
        return modified_content

    def _append_to_env(self, env_path, key, value):
        try:
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    if f"{key}=" in f.read(): return
            with open(env_path, 'a') as f:
                f.write(f"\n{key}={value}\n")
        except Exception as e:
            Logger.error(f"Failed to write .env: {e}")
