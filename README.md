# Multiple-Command-Execution

- Env setup
  - sudo apt-get install python3-pip
  - pip install termcolor

- Modify all paths to relative test suites location.

- Format of execute command

  ```python3  multi_cmd.py “test” “retry round” “serial number”```
  ```
  Ex:
  python3 multi_cmd.py gsi 3 9089f948
  python3 multi_cmd.py cts 3 9089f948
  ```
- Sample result
![image](https://user-images.githubusercontent.com/99638331/208369341-c75de2cd-6a1f-4bf9-a0b9-f5c711a40fe8.png)
