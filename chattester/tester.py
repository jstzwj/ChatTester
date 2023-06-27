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
            input_variables=["focal_class", "focal_method", "role_instruction", "focal_method_name", "junit_version"],
            template="""```java
// Focal class
{focal_class}
//Focal method
{focal_method}
```
{role_instruction}
Please write a test method for the "{focal_method_name}" based on the given information using {junit_version}.""",
        )

        self.intention_prompt = PromptTemplate(
            input_variables=["focal_class", "focal_method", "focal_method_name"],
            template="""```java
// Focal class
{focal_class}
//Focal method
{focal_method}
```
Please infer the intention of the "{focal_method_name}".""")
        
        self.generation_prompt = PromptTemplate(
            input_variables=["intention", "role_instruction", "focal_method_name"],
            template="""
// Method intention
{intention}
{role_instruction}
Please write a test method for the "{focal_method_name}" with the given Method intention.""")

    def generate(self, focal_class: str, focal_method: str, focal_method_name: str):
        pass