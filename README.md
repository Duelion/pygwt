# PyGWT

PyGWT decodes responses produced by the Google Web Toolkit (GWT) RPC system. It reads the raw JavaScript returned by a service and reconstructs the original Java objects using Pydantic models. The project focuses on the services used by the Chilean tax authority, but the parser is generic and can be adapted to other GWT endpoints.

## Features

- **GwtParser** – turns a reversed list of codes into Python objects.
- **Built-in wrappers** – classes like `Long`, `Date`, and `TimeStamp` help interpret GWT's primitive types.
- **Utilities** – tools for splitting raw responses and for base64 encoding/decoding.
- **GwtCodes** – utilities to fetch the permutation tokens and strong names required to craft requests.

## Installation

```bash
pip install pygwt
```

## Basic usage

```python
from pathlib import Path
from pygwt.parser import GwtParser

# load a raw response (see ``tests/gwt_examples`` for samples)
text = Path("sample.txt").read_text()
parser = GwtParser(text)
result = parser.parse()
print(result)
```

To decode custom classes, pass a mapping of Java class names to Pydantic models when creating the parser. See ``tests/conftest.py`` for examples.

## Running the tests

```bash
pytest -q
```

## License

MIT
