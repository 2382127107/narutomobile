from maa.agent.agent_server import AgentServer
from maa.context import Context
from maa.custom_action import CustomAction


# 画饼
@AgentServer.custom_action("Fight")
class Fight(CustomAction):
    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> CustomAction.RunResult:
        return CustomAction.RunResult(success=False)
