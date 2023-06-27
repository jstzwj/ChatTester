

import os
from typing import List, Optional
import glob

import javalang

from chattester.javalang_utils import get_method_start_end, get_method_text
from chattester.source import ClassInfo, LineRange, MethodInfo, SourceFile, SourceRange


class ProjectUnitTestExtractor:
    def __init__(self, project_path: str) -> None:
        self.project_path = project_path
    
    def _get_all_test_source(self) -> List[str]:
        files = glob.glob(os.path.join(self.project_path, "**/src/test/**/*.java"), recursive=True)
        return list(files)
    
    def _get_method_decl(self, node) -> str:
        decl = []
        decl.append(node.name)

        decl.append("(")
        for i, param in enumerate(node.parameters):
            decl.append(f"{param.type.name} {param.name}")
            if i != len(node.parameters) - 1:
                decl.append(", ")
        decl.append(")")
        return "".join(decl)

    def _extract_focal_methods(self, file_path: str) -> List[MethodInfo]:
        with open(file_path, "r", encoding="utf-8") as f:
            codetext = f.read()
        codelines = codetext.splitlines(keepends=True)
        source = SourceFile(path=file_path, type="java")

        tree = javalang.parse.parse(codetext)

        out = []
        lex = None
        for path, node in tree.filter(javalang.tree.MethodDeclaration):
            if len(node.annotations) > 0:
                if any([a.name == "Test" for a in node.annotations]):
                    startpos, endpos, startline, endline = get_method_start_end(tree, node)
                    method_text, startline, endline, lex = get_method_text(codelines, startpos, endpos, startline, endline, lex)
                    
                    out.append(
                        MethodInfo(
                            source=source,
                            range=LineRange(start_line=startline, end_line=endline),
                            text=method_text,
                            name=node.name,
                            declaration=self._get_method_decl(node),
                        )
                    )
        return out
    
    def _get_focal_file(self, test_path: str) -> Optional[str]:
        test_path = os.path.normpath(test_path)
        focal_file_path = test_path.replace("src/test", "src/main")
        if os.path.exists(focal_file_path):
            return focal_file_path
        else:
            return None
    
    def _get_focal_class(self, file_path: str) -> ClassInfo:
        with open(file_path, "r", encoding="utf-8") as f:
            codetext = f.read()
        codelines = codetext.splitlines(keepends=True)
        source = SourceFile(path=file_path, type="java")

        tree = javalang.parse.parse(codetext)