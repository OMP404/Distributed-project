
Tests comprise of basic tests for the main app and playing window with pythons pytest module.

Majority of the tests are checking for the responses status code, responses data containing a certain string, or both.
A few tests test the inner functions such as creating the deck of cards or the unique code for creating rooms.
A larger scale testing of the software wasn't done due to the service being run on our personal devices, where the limit would be simply how much traffic our device(s)' could handle.

All of the tests run successfully for the current version of the code.

To run the tests, while in the main directory:
1. make sure the requirements.txt has been installed using:
```
pip install -r requirements.txt
```

2. and then to run the tests:
```
pytest tests\tests.py
```

This should give a percentage of successful tests ran and problems with possibly unsuccessful tests.