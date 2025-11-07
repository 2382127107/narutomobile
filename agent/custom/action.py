from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context

from utils.logger import logger

@AgentServer.custom_action("MyAction111")
class MyAction111(CustomAction):

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> CustomAction.RunResult:

        logger.info("MyAction111 is running!")

        return CustomAction.RunResult(success=True)
