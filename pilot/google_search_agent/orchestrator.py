# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
from typing import AsyncGenerator, Optional
from typing_extensions import override

from google.adk.agents import BaseAgent, LoopAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

logger = logging.getLogger(__name__)


class MasterWorkflowAgent(BaseAgent):
    """A custom orchestrator agent that implements a Draft -> Critique -> Refine loop."""

    researcher_agent: BaseAgent
    critique_and_refine_loop: LoopAgent
    summarizer_agent: BaseAgent

    model_config = {"arbitrary_types_allowed": True}

    def __init__(
        self,
        name: str,
        researcher_agent: BaseAgent,
        critique_and_refine_loop: LoopAgent,
        summarizer_agent: BaseAgent,
        before_agent_callback: Optional[callable] = None,
        after_agent_callback: Optional[callable] = None,
    ):
        sub_agents_list = [
            researcher_agent,
            critique_and_refine_loop,
            summarizer_agent,
        ]

        super().__init__(
            name=name,
            researcher_agent=researcher_agent,
            critique_and_refine_loop=critique_and_refine_loop,
            summarizer_agent=summarizer_agent,
            sub_agents=sub_agents_list,
            before_agent_callback=before_agent_callback,
            after_agent_callback=after_agent_callback,
        )

    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        logger.info(f"[{self.name}] Starting master workflow.")

        # 1. Draft Step: Run the ResearcherAgent
        logger.info(f"[{self.name}] Running ResearcherAgent to draft an answer...")
        async for event in self.researcher_agent.run_async(ctx):
            yield event

        # Check if a draft was actually produced
        if "draft_answer" not in ctx.session.state or not ctx.session.state["draft_answer"]:
            logger.error(f"[{self.name}] ResearcherAgent failed to produce a draft. Aborting workflow.")
            # Here you would yield a user-facing error message
            return
        logger.info(f"[{self.name}] Draft produced. Moving to critique.")


        # 2. Critique and Refine Step: Run the Loop
        logger.info(f"[{self.name}] Running CritiqueAndRefineLoop...")
        async for event in self.critique_and_refine_loop.run_async(ctx):
            yield event
        logger.info(f"[{self.name}] Critique loop finished. Moving to summarization.")

        # 3. Finalize Step: Run the Summarizer Agent
        logger.info(f"[{self.name}] Running SessionSummarizerAgent to finalize...")
        async for event in self.summarizer_agent.run_async(ctx):
            yield event

        logger.info(f"[{self.name}] Master workflow finished.")
