from io import BytesIO
from typing import Annotated
from fastapi import APIRouter, File, HTTPException
from pydantic import BaseModel
import logging

import aiiocfinder.proxy as proxy
import aiiocfinder.log as log
import aiiocfinder.config as config


class ProgrammingModel(BaseModel):
    model: str
    max_tokens: int
    temperature: float
    history: list[dict]


class Router:
    """
    FastAPI router
    """

    config = config.Config("config.yaml")
    proxy = proxy.Proxy()
    _logger = logging.getLogger(__name__)

    def __init__(self):
        log.setup()
        self.router = APIRouter()
        self.router.add_api_route("/setup", self.setup, methods=["POST"])
        self.router.add_api_route("/disassamble", self.disassamble, methods=["POST"])
        self.router.add_api_route("/artifact", self.artifact, methods=["POST"])
        self.router.add_api_route("/analyze", self.analyze, methods=["GET"])
        self.router.add_api_route("/completion", self.completion, methods=["POST"])
        self.router.add_api_route("/yara", self.yara, methods=["GET"])
        self.router.add_api_route("/history", self.history, methods=["GET"])
        self.router.add_api_route("/iocs", self.iocs, methods=["GET"])
        self.router.add_api_route("/summary", self.summary, methods=["GET"])
        self.router.add_api_route("/reset", self.reset, methods=["GET"])
        self._logger.debug(f"Initialized {__name__}")

    @staticmethod
    async def setup(programming_model: ProgrammingModel):
        Router._logger.debug(f"Called setup")
        Router.proxy.setup(
            api_key=Router.config.openaiAccessToken,
            model=programming_model.model,
            temperature=programming_model.temperature,
            max_tokens=programming_model.max_tokens,
            history=programming_model.history,
        )
        return {"status": "success"}

    @staticmethod
    async def disassamble(file: Annotated[bytes, File()]):
        Router._logger.debug(f"Called disassmble")
        f = BytesIO(file)
        dis = Router.proxy.get_disassambler(f)
        return {"assembly": dis.assembly, "strings": dis.strings}

    @staticmethod
    async def artifact(artifact: list[dict]):
        Router._logger.debug(f"Called artifact")
        analyst = Router.proxy.analyst
        for item in artifact:
            analyst.add_artifact(item["type"], item["artifact"])
        return {"status": "success"}

    @staticmethod
    async def analyze():
        Router._logger.debug(f"Called analyze")
        analyst = Router.proxy.analyst
        try:
            analyst.find_iocs()
            return {
                "completions": analyst.history,
                "summary": analyst.summary,
                "iocs": analyst.iocs,
                "yara_rules": analyst.yara_rules,
            }
        except Exception as e:
            Router._logger.error(e)
            raise HTTPException(status_code=500, detail="Server error")

    @staticmethod
    async def completion(message: str):
        Router._logger.debug(f"Called completion")
        analyst = Router.proxy.analyst
        analyst.ask_ai(message)
        return {"completions": analyst.history}

    @staticmethod
    async def history():
        Router._logger.debug(f"Called history")
        analyst = Router.proxy.analyst
        return {"history": analyst.history}

    @staticmethod
    async def summary():
        Router._logger.debug(f"Called summary")
        analyst = Router.proxy.analyst
        return {"summary": analyst.summary}

    @staticmethod
    async def iocs():
        Router._logger.debug(f"Called iocs")
        analyst = Router.proxy.analyst
        return {"iocs": analyst.iocs}

    @staticmethod
    async def yara():
        Router._logger.debug(f"Called yara")
        analyst = Router.proxy.analyst
        return {"yara": analyst.yara_rules}

    @staticmethod
    async def reset():
        Router._logger.debug(f"Called reset")
        Router.proxy.reset_analyst()
        return {"status": "success"}
