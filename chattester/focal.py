# Copyright 2023 by XiaHan. All rights reserved.
# This file is part of the ChatTester,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import os
from typing import List, Optional
import glob

import javalang
import tqdm

from chattester.javalang_utils import get_method_start_end, get_method_text
from chattester.source import ClassInfo, LineRange, MethodInfo, SourceFile, SourceRange, UnitTestPair


class ProjectUnitTestExtractor:
    def __init__(self, project_path: str) -> None:
        self.project_path = project_path
    
    def _get_all_test_source(self) -> List[str]:
        files = glob.glob(os.path.join(self.project_path, "**/src/test/**/*.java"), recursive=True)
        return list(files)

    def _extract_test_methods(self, file_path: str) -> List[MethodInfo]:
        with open(file_path, "r", encoding="utf-8") as f:
            codetext = f.read()
        source = SourceFile(path=file_path, type="java", codetext=codetext)

        tree = javalang.parse.parse(codetext)

        out = []
        lex = None
        for path, node in tree.filter(javalang.tree.MethodDeclaration):
            if len(node.annotations) > 0:
                if any([a.name == "Test" for a in node.annotations]):
                    out.append(
                        MethodInfo.from_node(source=source, tree=tree, node=node, lex=lex)
                    )
        return out
    
    def _extract_methods(self, file_path: str) -> List[MethodInfo]:
        with open(file_path, "r", encoding="utf-8") as f:
            codetext = f.read()
        source = SourceFile(path=file_path, type="java", codetext=codetext)

        tree = javalang.parse.parse(codetext)

        out = []
        lex = None
        for path, node in tree.filter(javalang.tree.MethodDeclaration):
            out.append(
                MethodInfo.from_node(source=source, tree=tree, node=node, lex=lex)
            )
        return out
    
    def _extract_package_info(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            codetext = f.read()
        codelines = codetext.splitlines(keepends=True)
        source = SourceFile(path=file_path, type="java", codetext=codetext)

        try:
            tree = javalang.parse.parse(codetext)
        except:
            print("Failed to parse: " + file_path)
            return

        out = None
        lex = None
        for path, node in tree.filter(javalang.tree.PackageDeclaration):
            startpos, endpos, startline, endline = get_method_start_end(tree, node)
            package_text = codelines[startline - 1].strip()
            out = package_text
        return out
    
    def _extract_imports(self, file_path: str) -> List[str]:
        with open(file_path, "r", encoding="utf-8") as f:
            codetext = f.read()
        codelines = codetext.splitlines(keepends=True)
        source = SourceFile(path=file_path, type="java", codetext=codetext)

        try:
            tree = javalang.parse.parse(codetext)
        except:
            print("Failed to parse: " + file_path)
            return

        out = []
        lex = None
        for path, node in tree.filter(javalang.tree.Import):
            startpos, endpos, startline, endline = get_method_start_end(tree, node)
            import_text = codelines[startline - 1].strip()
            out.append(import_text)
        return out
    
    def _get_focal_file(self, test_path: str) -> Optional[str]:
        test_path = os.path.normpath(test_path).replace("\\", "/")
        if "src/test" not in test_path:
            return None
        focal_file_path = test_path.replace("src/test", "src/main")
        if focal_file_path.endswith("Test.java"):
            focal_file_path = focal_file_path.replace("Test.java", ".java")
        if os.path.exists(focal_file_path):
            return focal_file_path
        else:
            return None
    
    def _get_focal_class(self, file_path: str) -> Optional[ClassInfo]:
        file_path = os.path.normpath(file_path).replace("\\", "/")
        with open(file_path, "r", encoding="utf-8") as f:
            codetext = f.read()
        source = SourceFile(path=file_path, type="java", codetext=codetext)

        tree = javalang.parse.parse(codetext)

        core_class_name = file_path.split("/")[-1].replace(".java", "")
        
        out = None
        for path, node in tree.filter(javalang.tree.ClassDeclaration):
            if node.name != core_class_name:
                continue
            out = ClassInfo.from_node(source, tree, node)
        return out
    
    def get_all_tests(self) -> List[UnitTestPair]:
        out = []
        test_files = self._get_all_test_source()
        for test_file in tqdm.tqdm(test_files): 
            focal_file = self._get_focal_file(test_file)
            if focal_file is None:
                continue
            
            package_info = self._extract_package_info(focal_file)
            imports = self._extract_imports(focal_file)

            focal_class = self._get_focal_class(focal_file)
            focal_methods = self._extract_methods(focal_file)
            test_methods = self._extract_test_methods(test_file)

            if focal_class is None:
                continue

            for method in test_methods:
                if method.name.startswith("test"):
                    possible_focal_method_name = method.name[4:].lower()
                else:
                    possible_focal_method_name = method.name
                
                focal_method = None
                for each_focal_method in focal_methods:
                    if each_focal_method.name.lower() == possible_focal_method_name:
                        focal_method = each_focal_method
                        break
                
                if focal_method is None:
                    continue
                pair = UnitTestPair(
                    focal_class=focal_class,
                    focal_method=focal_method,
                    test_path=test_file,
                    package_info=package_info,
                    imports=imports,
                )
                out.append(pair)

        return out