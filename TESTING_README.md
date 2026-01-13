# How to run unit tests

## 1. Open a bash or powershell terminal

## 2. Run the following command with coverage.  Results will show you how many tests passed. OK means they all passed.
```bash
coverage run -m unittest discover tests
```

## 3. Run the following to write an XML coverage report
```bash
coverage xml
```

## 4. Optional: If you have Coverage Gutters installed, you can use it to parse coverage.xml to visually display code coverage for every Python script