# How to run unit tests

## 1. Open a bash or powershell terminal. Install coverage if you haven't already
```bash
pip install coverage
```

## 2. Run the following command with coverage.  Results will show you how many tests passed. OK means they all passed.
```bash
coverage run -m unittest discover tests
```

## 3. Run the following to see your code coverage for each production code file
```bash
coverage report
```

## 3. Run the following to write an XML coverage report
```bash
coverage xml
```

## 4. Optional: If you have Coverage Gutters installed, you can use it to parse coverage.xml to visually display code coverage for every Python script

## Troubleshooting

# You may see the following error in your IDE terminal, especially if it is VSCode
- **chromadb import / DLL errors:** If tests fail with an error importing chromadb_rust_bindings or "DLL load failed", ensure `chromadb` is installed in your environment and the Microsoft Visual C++ Redistributable is present (required by the native bindings).

  - Install chromadb in your venv:
    ```bash
    pip install --no-cache-dir chromadb
    ```

  - If you still see DLL load errors on Windows, install the "Microsoft Visual C++ Redistributable for Visual Studio 2015-2022" (x64) from Microsoft and then reinstall `chromadb`.

  - If you prefer to avoid native bindings, consider configuring a remote or HTTP-backed vector store instead of the local Chroma bindings.

