from typing import Protocol
from uuid import uuid4

from ficopilot.contracts import (
    CopilotAnswer,
    CopilotEvidence,
    CopilotPlan,
    CopilotRequest,
    CopilotSource,
    CopilotSynthesisDraft,
    DataQuestion,
    DocumentQuestion,
    ResearchRequest,
)
from ficopilot.copilot.evidence import collect_sources
from ficopilot.data_agent.service import DataAgentService
from ficopilot.document_rag.service import DocumentRagService
from ficopilot.research.service import ResearchService


class CopilotPlanner(Protocol):
    def plan(
        self,
        request: CopilotRequest,
        *,
        document_context: str,
        data_context: str,
    ) -> CopilotPlan: ...


class CopilotSynthesisProvider(Protocol):
    def synthesize(
        self,
        *,
        evidence: CopilotEvidence,
        sources: list[CopilotSource],
    ) -> CopilotSynthesisDraft: ...


class CopilotOrchestrator:
    def __init__(
        self,
        *,
        planner: CopilotPlanner,
        synthesis_provider: CopilotSynthesisProvider,
        research_service: ResearchService,
        document_service: DocumentRagService,
        data_service: DataAgentService,
    ) -> None:
        self._planner = planner
        self._synthesis_provider = synthesis_provider
        self._research_service = research_service
        self._document_service = document_service
        self._data_service = data_service

    def gather_evidence(
        self,
        request: CopilotRequest,
    ) -> CopilotEvidence:
        document_context = "No PDF selected."

        if request.document_id is not None:
            record = self._document_service.get_document_record(request.document_id)
            document_context = (
                f"Selected PDF: {record.filename}; page count: {record.page_count}."
            )

        plan = self._planner.plan(
            request,
            document_context=document_context,
            data_context=self._data_service.describe_available_data(),
        )

        trace_id = str(uuid4())
        evidence = CopilotEvidence(
            request=request,
            plan=plan,
            trace_id=trace_id,
        )

        if plan.research_question is not None:
            evidence.research_result = self._research_service.run(
                ResearchRequest(
                    question=plan.research_question,
                    as_of=request.as_of,
                ),
                trace_id=trace_id,
            )

        if plan.document_question is not None:
            if request.document_id is None:
                raise ValueError("Document route requires a selected PDF.")

            evidence.document_result = self._document_service.ask(
                DocumentQuestion(
                    document_id=request.document_id,
                    question=plan.document_question,
                    top_k=10,
                )
            )

        if plan.data_question is not None:
            evidence.data_result = self._data_service.run(
                DataQuestion(question=plan.data_question)
            )

        return evidence

    def run(self, request: CopilotRequest) -> CopilotAnswer:
        evidence = self.gather_evidence(request)

        if evidence.plan.cannot_answer:
            return CopilotAnswer(
                question=request.question,
                answer=(
                    "The available capabilities do not provide enough "
                    "information to answer this question."
                ),
                coverage="insufficient",
                sources=[],
                used_modules=[],
                routing_reason=evidence.plan.routing_reason,
                warnings=[],
                trace_id=evidence.trace_id,
            )

        sources = collect_sources(evidence)

        draft = self._synthesis_provider.synthesize(
            evidence=evidence,
            sources=sources,
        )

        sources_by_id = {source.source_id: source for source in sources}
        cited_sources = [
            sources_by_id[source_id] for source_id in draft.cited_source_ids
        ]

        used_modules = [
            module
            for module, question in (
                ("research", evidence.plan.research_question),
                ("document", evidence.plan.document_question),
                ("data", evidence.plan.data_question),
            )
            if question is not None
        ]

        warnings = list(draft.warnings)

        if evidence.research_result is not None:
            warnings.extend(evidence.research_result.warnings)

        if evidence.document_result is not None:
            warnings.extend(evidence.document_result.warnings)

        if evidence.data_result is not None:
            warnings.extend(evidence.data_result.warnings)

        return CopilotAnswer(
            question=request.question,
            answer=draft.answer,
            coverage=draft.coverage,
            sources=cited_sources,
            used_modules=used_modules,
            routing_reason=evidence.plan.routing_reason,
            warnings=list(dict.fromkeys(warnings)),
            trace_id=evidence.trace_id,
        )
