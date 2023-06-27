# ChatTester
This is an implementation for the paper "No More Manual Tests? Evaluating and Improving ChatGPT for Unit Test Generation" ([arxiv](https://arxiv.org/abs/2305.04207)).

## Usage
```python
from chattester.tester import ChatGPTUnitTestGenerator
generator = ChatGPTUnitTestGenerator("./data/gson", "OPENAI_KEY", "OPENAI_BASE")

from chattester.focal import ProjectUnitTestExtractor
extractor = ProjectUnitTestExtractor("./data/gson")
tests = extractor.get_all_tests()
for test in tests:
    output = generator.generate(test.focal_class, test.focal_method)
```