import re


class Prompt:
    def __init__(self, programming_model):
        self.history = []
        self._programming_model = programming_model
        self.__add_system_to_history(self._programming_model[0])
        self.artifacts = []

    @property
    def tools(self):
        for item in self._programming_model:
            if "artifacts" in item["type"]:
                tools = item["tools"]
        return tools

    @property
    def yara_tools(self):
        for item in self._programming_model:
            if "yara" in item["type"]:
                tools = item
        return tools

    @staticmethod
    def artifact_prompt_placeholder_is_replaced(artifact_prompt):
        if len(re.findall("<[\w ]+>", artifact_prompt)) > 0:
            return False
        return True

    @staticmethod
    def artifact_prompt_placeholder_is_found(artifact_prompt, placeholder):
        if len(re.findall(f"<{placeholder}>", artifact_prompt)) == 1:
            return True
        return False

    def replace_json_placeholders(self, placeholder, artifact):
        for item_i in self._programming_model:
            if "artifacts" in item_i["type"]:
                for item_j in item_i["artifacts"]:
                    if self.artifact_prompt_placeholder_is_found(
                        item_j["prompt_artifact"], placeholder=placeholder
                    ):
                        replace_token = "<%s>" % placeholder
                        item_j["prompt_artifact"] = item_j["prompt_artifact"].replace(
                            replace_token, artifact
                        )
                        self.add_user_to_history(item_j["prompt_artifact"])
                        self.artifacts.append(item_j)

    def __add_system_to_history(self, systeminput):
        self.history.append({"role": "system", "content": systeminput["content"]})

    def add_user_to_history(self, userinput):
        self.history.append({"role": "user", "content": userinput})

    def add_assistant_to_history(self, assistantinput):
        self.history.append({"role": "assistant", "content": assistantinput})

    def add_assistant_function_call_to_history(self, function_name, args):
        self.history.append({
            "role": "assistant",
            "function_call": {"name": function_name, "arguments": args},
            "content": None,
        })

    def summary_prompt(self):
        summary = self._programming_model[-1]
        return summary["content"]
