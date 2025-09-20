import asyncio
import logging
import os
from concurrent import futures

import grpc
import sys

# Ensure generated proto modules can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "shared", "protos")))

from engines.phi3_enhanced_coordinator import (
    Phi3EnhancedTranslationCoordinator as TranslationCoordinator,
)

# Generated after compiling protos (paths assume package under shared)
import translation_pb2 as pb2  # type: ignore
import translation_pb2_grpc as pb2_grpc  # type: ignore


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class TranslationServiceGrpc(pb2_grpc.TranslationServiceServicer):
    def __init__(self, coordinator: TranslationCoordinator):
        self.coordinator = coordinator

    async def _translate_async(self, request: pb2.TranslateRequest) -> pb2.TranslateResponse:
        result = await self.coordinator.translate(
            text=request.text,
            source_language=request.source_language or "auto",
            target_language=request.target_language,
            domain=request.domain or None,
        )
        return pb2.TranslateResponse(
            translated_text=result.translated_text,
            source_language=result.source_language,
            target_language=result.target_language,
            confidence_score=float(result.confidence_score),
            engine=result.engine,
            processing_time_ms=int(getattr(result, "processing_time_ms", 0)),
            cache_hit=bool(getattr(result, "cache_hit", False)),
        )

    async def _detect_language_async(self, request: pb2.LanguageDetectionRequest) -> pb2.LanguageDetectionResponse:
        detected_lang = await self.coordinator.detect_language(request.text)
        return pb2.LanguageDetectionResponse(detected_language=detected_lang, confidence=0.8)

    def Translate(self, request, context):
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(self._translate_async(request))
        finally:
            loop.close()

    def DetectLanguage(self, request, context):
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(self._detect_language_async(request))
        finally:
            loop.close()

    def ListLanguages(self, request, context):
        languages = self.coordinator.get_supported_languages()
        indian_languages = [
            "hi",
            "bn",
            "ta",
            "te",
            "ml",
            "kn",
            "gu",
            "or",
            "pa",
            "as",
            "mr",
            "ur",
            "ne",
            "sd",
            "kok",
            "mai",
            "sat",
            "doi",
            "mni",
            "brx",
            "bh",
        ]
        return pb2.ListLanguagesResponse(supported_languages=languages, indian_languages=indian_languages)


async def _init_coordinator() -> TranslationCoordinator:
    coord = TranslationCoordinator()
    await coord.initialize()
    return coord


def serve():
    port = int(os.getenv("TRANSLATION_GRPC_PORT", "9010"))
    logger.info(f"Starting Translation gRPC server on 0.0.0.0:{port}")

    loop = asyncio.get_event_loop()
    coordinator = loop.run_until_complete(_init_coordinator())

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_TranslationServiceServicer_to_server(TranslationServiceGrpc(coordinator), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
