# Copyright 2023 by XiaHan. All rights reserved.
# This file is part of the ChatTester,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.
import javalang
from pydantic import BaseModel, Field
from typing import List, Optional
from chattester import javalang_utils

from chattester.javalang_utils import get_method_start_end, get_method_text

class SourceFile(BaseModel):
    path: str
    type: str
    codetext: str


class SourcePos(BaseModel):
    line: int
    col: int

class SourceRange(BaseModel):
    start_pos: Optional[SourcePos]
    end_pos: Optional[SourcePos]

class LineRange(BaseModel):
    start_line: int
    end_line: int

class MethodInfo(BaseModel):
    source: SourceFile
    range: LineRange
    text: str
    name: str
    modifiers: List[str]
    declaration: str

    @staticmethod
    def _get_method_decl(node: javalang.ast.Node) -> str:
        decl = []
        decl.append(node.name)

        decl.append("(")
        for i, param in enumerate(node.parameters):
            decl.append(f"{param.type.name} {param.name}")
            if i != len(node.parameters) - 1:
                decl.append(", ")
        decl.append(")")
        return "".join(decl)

    @staticmethod
    def from_node(source: SourceFile, tree: javalang.ast.Node, node: javalang.ast.Node, lex=None) -> "MethodInfo":
        codelines = source.codetext.splitlines(keepends=True)

        startpos, endpos, startline, endline = get_method_start_end(tree, node)
        method_text, startline, endline, lex = get_method_text(codelines, startpos, endpos, startline, endline, lex)
        

        return MethodInfo(
            source=source,
            range=LineRange(start_line=startline, end_line=endline),
            text=method_text,
            name=node.name,
            modifiers=node.modifiers,
            declaration=MethodInfo._get_method_decl(node),
        )


class FieldInfo(BaseModel):
    source: SourceFile
    range: LineRange
    text: str
    name: str

    @staticmethod
    def from_node(source: SourceFile, tree: javalang.ast.Node, node: javalang.ast.Node) -> "FieldInfo":
        lex = None
        codelines = source.codetext.splitlines(keepends=True)

        sub_node = node
        for path, field_node in node.filter(javalang.tree.VariableDeclarator):
            sub_node = field_node
        startpos, endpos, startline, endline = get_method_start_end(tree, sub_node)
        field_text, startline, endline, lex = get_method_text(codelines, startpos, endpos, startline, endline, lex)
        
        return FieldInfo(
            source=source,
            range=LineRange(start_line=node.position.line, end_line=node.position.line + 1),
            text=codelines[node.position.line],
            name=sub_node.name,
        )

class ClassInfo(BaseModel):
    source: SourceFile
    range: LineRange
    text: str
    name: str
    fields: List[FieldInfo]
    methods: List[MethodInfo]

    @staticmethod
    def from_node(source: SourceFile, tree: javalang.ast.Node, node: javalang.ast.Node) -> "ClassInfo":
        lex = None
        codelines = source.codetext.splitlines(keepends=True)

        startpos, endpos, startline, endline = get_method_start_end(tree, node)
        class_text, startline, endline, lex = get_method_text(codelines, startpos, endpos, startline, endline, lex)
        
        fields = []
        for path, field_node in node.filter(javalang.tree.FieldDeclaration):
            fields.append(FieldInfo.from_node(source, tree, field_node))

        methods = []
        for path, method_node in node.filter(javalang.tree.MethodDeclaration):
            methods.append(MethodInfo.from_node(source, tree, method_node))

        for path, method_node in node.filter(javalang.tree.ConstructorDeclaration):
            methods.append(MethodInfo.from_node(source, tree, method_node))
        
        return ClassInfo(
            source=source,
            range=LineRange(start_line=startline, end_line=endline),
            text=class_text,
            name=node.name,
            fields=fields,
            methods=methods,
        )



class UnitTestPair(BaseModel):
    focal_class: ClassInfo
    focal_method: MethodInfo
    test_path: str
    package_info: str
    imports: List[str]