# maLLMu-ng

## Create `config.yaml`

```bash
cat <<EOF >>config.yaml
openai:
  access-token: "<api-token>"
EOF
```

## Compile test code

```bash
sudo apt update
sudo apt install gcc
gcc -o hello hello.c
```

## Install python environment

```bash
# install requirements in virtual environment
python3 -m venv .venv && source .venv/bin/activate && python3 -m pip install -r requirements.txt
# run gradio
gradio chatapp.py
uvicorn testapi:app --reload --port 8080
pyreverse aiiocfinder/  --output png --ignore $(pwd)/aiiocfinder/tests,$(pwd)/aiiocfinder/iocfinder/tests --colorize
```
