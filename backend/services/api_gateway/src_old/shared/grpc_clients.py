import os
import grpc
from typing import Optional

from shared.protos import translation_pb2 as pb2  # type: ignore
from shared.protos import translation_pb2_grpc as pb2_grpc  # type: ignore


class TranslationGrpcClient:
    def __init__(self, host: Optional[str] = None, port: Optional[int] = None):
        host = host or os.getenv("TRANSLATION_SERVICE_HOST", "translation-service")
        port = port or int(os.getenv("TRANSLATION_GRPC_PORT", "9010"))
        self._target = f"{host}:{port}"
        self._channel = grpc.insecure_channel(self._target)
        self._stub = pb2_grpc.TranslationServiceStub(self._channel)

    def translate(self, text: str, target_language: str, source_language: str = "auto", domain: str = ""):
        req = pb2.TranslateRequest(
            text=text, source_language=source_language, target_language=target_language, domain=domain
        )
        return self._stub.Translate(req)

    def detect_language(self, text: str):
        return self._stub.DetectLanguage(pb2.LanguageDetectionRequest(text=text))

    def list_languages(self):
        return self._stub.ListLanguages(pb2.ListLanguagesRequest())
