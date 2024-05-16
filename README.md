# maLLMu-ng

## Create `config.yaml`

```bash
cat <<EOF >>config.yaml
openai:
  access-token: "<openai-api-token>"
EOF
```

## Run the app

```bash
python3 -m venv .venv && source .venv/bin/activate && python3 -m pip install -r requirements.txt
python3 main.py # only RestAPI interface
python3 main.py --gui # for gradio interface
python3 main.py --help
```

## Compile simple_reverse_shell

`simple_reverse_shell` is as the name states a simple reverse shell,
which can be used for testing purposes.
The application doesn't actually executes the file and just disassambles the 
binary file and gets the `strings` output from it.

It can be used to test the capabilities from maLLMu-ng.

```bash
sudo apt update
sudo apt install gcc
gcc -o simple_reverse_shell e2e/simple_reverse_shell.c
```

### Test with `test_e2e_with_elffile_rev_shell.py`

The whole frontend procedure of `maLLMu-ng` can be see in `test_e2e_with_elffile_rev_shell.py`.
After setting up the application run:

```bash
python3 e2e/test_e2e_with_elffile_rev_shell.py
```

## Development

### Running tests

```bash
python3 -m pip install pytest
pytest aiiocfinder/tests/
```

### Create classdiagram

```bash
pyreverse aiiocfinder/  --output png --ignore $(pwd)/aiiocfinder/tests,$(pwd)/aiiocfinder/iocfinder/tests --colorize
```
