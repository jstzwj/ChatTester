# ChatTester
This is an implementation for the paper "No More Manual Tests? Evaluating and Improving ChatGPT for Unit Test Generation" ([arxiv](https://arxiv.org/abs/2305.04207)).

## Dependency
Java Environment:
* JDK > 17
* Maven

Python Environment:
* Python > 3.9
* Packages in `requirements.txt`

## Usage
```python
from chattester.tester import ChatGPTUnitTestGenerator

generator = ChatGPTUnitTestGenerator(
    project_path="./data/gson",
    openai_api_key="OPENAI-KEY",
    openai_api_base="OPENAI-BASE"
)

from chattester.focal import ProjectUnitTestExtractor
extractor = ProjectUnitTestExtractor("./data/gson")

tests = extractor.get_all_tests()
for test in tests:
    print(test.focal_class.source.path, test.focal_method.declaration)
    gen_test = generator.iterative_generate(test)
```