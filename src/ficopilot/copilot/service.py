from typing import Protocol
from uuid import uuid4

from ficopilot.contracts import (
    CopilotEvidence,
    CopilotPlan,
    CopilotRequest,
    DataQuestion,
    DocumentQuestion,
    ResearchRequest,
)
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


class CopilotOrchestrator:
    def __init__(
        self,
        *,
        planner: CopilotPlanner,
        research_service: ResearchService,
        document_service: DocumentRagService,
        data_service: DataAgentService,
    ) -> None:
        self._planner = planner
        self._research_service = research_service
        self._document_service = document_service
        self._data_service = data_service

    def run(self, request: CopilotRequest) -> CopilotEvidence:
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
