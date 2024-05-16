import urllib.parse
import requests
import utils

url = "http://127.0.0.1:8000"

# compile file
utils.compile_c_code("simple_reverse_shell.c", "simple_reverse_shell")

# disassamble file
files = {"file": open("./e2e/simple_reverse_shell", "rb")}
endpoint = urllib.parse.urljoin(url, "disassamble")
r = requests.post(endpoint, files=files)
assembly = r.json()["assembly"]
strings = r.json()["strings"]

# setup analysis engine
endpoint = urllib.parse.urljoin(url, "setup")
programming_model = utils.load_test_json("aiiocfinder/tests/elffile.json")
## adjust model
model = "gpt-3.5-turbo-0125"
programming_model["model"] = model
r = requests.post(endpoint, json=programming_model)

# setup artifacts
data = [
    {
        "type": "code",
        "artifact": "\n".join(assembly[".text"]),
    },
    {
        "type": "strings",
        "artifact": "\n".join(strings),
    },
]
endpoint = urllib.parse.urljoin(url, "artifact")
r = requests.post(endpoint, json=data)

# call analyze
endpoint = urllib.parse.urljoin(url, "analyze")
r = requests.get(endpoint)
print(r.content)

# call completion
#endpoint = urllib.parse.urljoin(url, "completion")
#data = {"message": "What does the instruction in line 34 in the text section do?"}
#r = requests.post(endpoint, params=data)

endpoint = urllib.parse.urljoin(url, "yara")
r = requests.get(endpoint)

# reset engine
#endpoint = urllib.parse.urljoin(url, "reset")
#r = requests.get(endpoint, json=programming_model)
