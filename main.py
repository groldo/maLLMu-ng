import os
import sys
import requests
import argparse
import gradio as gr
import pandas as pd
import urllib.parse
import json
from multiprocessing import Process

import uvicorn
from aiiocfinder.router import Router
from fastapi import FastAPI


app = FastAPI()
router = Router()
app.include_router(router.router)

url = "http://127.0.0.1:8000/"

def upload_code(myfile):
    files = {"file": open(myfile, "rb")}
    endpoint = urllib.parse.urljoin(url, "disassamble")
    r = requests.post(endpoint, files=files)
    text_section = "\n".join(r.json()["assembly"][".text"])
    strings = "\n".join(r.json()["strings"])
    return {code: text_section, found_strings: strings}


def analyze_code(code, strings, model):
    endpoint = urllib.parse.urljoin(url, "setup")
    model = json.loads(model) 
    r = requests.post(endpoint, json=model)
    data = [
        {
            "type": "code",
            "artifact": code,
        },
        {
            "type": "strings",
            "artifact": strings
        },
    ]
    endpoint = urllib.parse.urljoin(url, "artifact")
    r = requests.post(endpoint, json=data)
    if r.status_code != 200:
        print(r.status_code)
        r.raise_for_status()
    endpoint = urllib.parse.urljoin(url, "analyze")
    r = requests.get(endpoint)
    if r.status_code != 200:
        print(r.status_code)
        r.raise_for_status()
    conversation = r.json()["completions"]
    history = parse_mallmu_dict_to_list(conversation)
    df = pd.DataFrame(r.json()["iocs"])
    yara = r.json()["yara_rules"]
    summary = r.json()["summary"]
    return history, df, "\n\n".join(yara), summary


def completion_create(message):
    endpoint = urllib.parse.urljoin(url, "completion")
    data = {"message": message}
    r = requests.post(endpoint, params=data)
    conversation = r.json()["completions"]
    history = parse_mallmu_dict_to_list(conversation)
    return history


def parse_mallmu_dict_to_list(completion_dict):
    history = []
    dialog = []
    for i, item in enumerate(completion_dict):
        match item["role"]:
            case "system":
                dialog.append(item["content"])
                dialog.append("")
                history.append(dialog)
                dialog = []
            case "user":
                if i > 0 and completion_dict[i-1]["role"] == "user":
                    # check if last item was a also an user item
                    # then close the last dialog and create a new dialog
                    dialog.append("")
                    history.append(dialog)
                    dialog = []
                dialog.append(item["content"])
            case "assistant":
                if i > 0 and completion_dict[i-1]["role"] == "assistant" and len(completion_dict[i-1]) == 2:
                    dialog.append("")
                if item["content"]:
                    dialog.append(item["content"])
                else: 
                    dialog.append(item["function_call"]["arguments"])
                history.append(dialog)
                dialog = []
    return history

def load_model_config(file):
    file = os.path.join("config", file)
    with open(file, "r") as f:
        model = json.load(f)
    model = json.dumps(model, indent=2)
    return model

def get_predefined_model_config():
    config_dir = os.path.join("config")
    files = [f for f in os.listdir(config_dir) 
                    if os.path.isfile(os.path.join(config_dir, f))]
    return files

with gr.Blocks(theme=gr.themes.Monochrome()) as demo:
    gr.Markdown("""
    # maLLMu
    """)
    with gr.Row():
        with gr.Column(scale=1):
            with gr.Group():
                upload = gr.UploadButton("1. Click to upload a file")
                model_config = gr.Dropdown(
                    get_predefined_model_config(),
                    label="2. Choose a model config",
                    info="Config files for maLLMu",
                )
                analyze = gr.Button("3. Analyze code")
                with gr.Tab("Code"):
                    with gr.Accordion("Expand Code"):
                        code = gr.Code(label="code")
                with gr.Tab("Strings"):
                    with gr.Accordion("Expand Strings"):
                        found_strings = gr.Code(label="strings")
        with gr.Column(scale=2):
            with gr.Tab("Chatbot"):
                with gr.Group():
                    chatbot = gr.Chatbot()
                    msg = gr.Textbox(show_label=False, placeholder="Message ...")
                    gr.Examples(
                        examples=[["What does the code do?"],
                                  ["Create an executive summary"],
                                  ["How can this be mitigated?"]],
                        inputs=[msg],
                        outputs=[chatbot],
                        fn=completion_create,
                        cache_examples=False,
                        run_on_click=True,
                    )
            with gr.Tab("IOCs"):
                df = gr.Dataframe()
            with gr.Tab("Yara rules"):
                yara = gr.Textbox(label="", placeholder="yara rules", lines=20, interactive=False, show_copy_button=True)
            with gr.Tab("Summary"):
                summary = gr.Textbox(label="", placeholder="Summary", lines=20)
            with gr.Tab("Configuration"):
                model = gr.Textbox(label="", placeholder="Model config", lines=20)

    msg.submit(completion_create, inputs=[msg], outputs=[chatbot])

    upload.upload(upload_code, inputs=[upload], outputs=[code, found_strings])

    analyze.click(
        analyze_code, inputs=[code, found_strings, model], outputs=[chatbot, df, yara, summary]
    )

    model_config.input(load_model_config, [model_config], [model])

if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog="maLLMu", description="Malware Analysis")
    parser.add_argument(
        "--reload", action="store_true", default=False, help="relaod uvicorn on save"
    )
    parser.add_argument(
        "--gui", action="store_true", default=False, help="start gradio gui"
    )
    args = parser.parse_args()
    try:
        uvicorn_log_config = uvicorn.config.LOGGING_CONFIG
        uvicorn_log_config["disable_existing_loggers"] = False
        del uvicorn_log_config["loggers"]
        mydict = {
            "app": "main:app",
            "host": "0.0.0.0",
            "port": 8000,
            "reload": args.reload,
            "log_config": uvicorn_log_config,
        }
        threads = []
        if args.gui:
            threads.append(Process(target=demo.launch))
        threads.append(Process(target=uvicorn.run, kwargs=mydict))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        print("KeyboardInterrupt received, shutdown ...")
        for thread in threads:
            thread.terminate()
        for thread in threads:
            thread.join()
        sys.exit(0)
