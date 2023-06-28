# Copyright 2023 by XiaHan. All rights reserved.
# This file is part of the ChatTester,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from typing import Optional
from langchain.memory import ConversationBufferMemory
from langchain import OpenAI, LLMChain, PromptTemplate
from langchain.chat_models import ChatOpenAI

from langchain.prompts.chat import (
    BaseChatPromptTemplate,
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)

from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

from chattester.source import UnitTestPair

def parse_java_code_from_answer(answer: str) -> Optional[str]:
    idx = answer.find("```java")
    if idx == -1:
        return None
    else:
        end_idx = answer.rfind("```")
        java_code = answer[idx + 7: end_idx]
        return java_code


JUNIT_IMPORT = """
import static org.junit.Assert.fail;
import java.io.IOException;
import java.io.StringReader;
import java.io.StringWriter;

import java.lang.reflect.Field;
import java.lang.reflect.Modifier;
import java.lang.reflect.Type;

import java.text.DateFormat;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;

import org.junit.Test;
"""

class ChatGPTUnitTestGenerator(object):
    def __init__(self, openai_api_key: str, openai_api_base: Optional[str] = None) -> None:
        self.model_name = "gpt-3.5-turbo"
        self.openai_api_key = openai_api_key
        self.openai_api_base = openai_api_base
        self.model = ChatOpenAI(
            model_name=self.model_name, 
            temperature=0.9, 
            max_tokens=2048,
            openai_api_key=self.openai_api_key,
            openai_api_base=self.openai_api_base,
        )
        self.memory = ConversationBufferMemory()
        self.llm_chain = ConversationChain(
            llm=self.model,
            memory=self.memory
        )
        self.role = "You are a professional who writes Java test methods."
        self.basic_prompt = PromptTemplate(
            input_variables=["focal", "role_instruction", "focal_method_name", "junit_version"],
            template="""```java
{focal}
```
{role_instruction}
Please write a test method for the "{focal_method_name}" based on the given information using {junit_version}. Please import all necessary packages.""",
        )

        self.intention_prompt = PromptTemplate(
            input_variables=["focal", "focal_method_name"],
            template="""```java
{focal}
```
Please infer the intention of the "{focal_method_name}".""")
        
        self.generation_prompt = PromptTemplate(
            input_variables=["intention", "role_instruction", "focal_method_name"],
            template="""
// Method intention
{intention}
{role_instruction}
Please write a test method for the "{focal_method_name}" with the given Method intention.""")

    def _get_focal_part(self, pair: UnitTestPair):
        fields = []
        for field in pair.focal_class.fields:
            fields.append(field.text)
        fields_str = "\n".join(fields)
        methods = []
        for method in pair.focal_class.methods:
            if method.name == pair.focal_method.name:
                continue
            methods.append(" ".join(method.modifiers) + " " + method.declaration + ";")
        methods_str = "\n".join(methods)
        template = f"""
// Focal Class
public class {pair.focal_class.name} {{
    {fields_str}
    {methods_str}
    // Focal method
    {pair.focal_method.text}
}}
"""
        return template

    def basic_generate(self, pair: UnitTestPair):
        focal_str = self._get_focal_part(pair)
        query = self.basic_prompt.format(
            focal=focal_str,
            role_instruction=self.role,
            focal_method_name=pair.focal_method.declaration,
            junit_version="Junit4",
        )
        # with open("out.txt", "w", encoding="utf-8") as f:
        #     f.write(query)
        answer = self.llm_chain.run(query)
        # with open("answer.txt", "w", encoding="utf-8") as f:
        #     f.write(answer)

        focal_imports = [i for i in pair.imports if "java" not in i]
        focal_imports = "\n".join(focal_imports)

        return f"""{pair.package_info}
{JUNIT_IMPORT}
{focal_imports}
{parse_java_code_from_answer(answer)}
"""