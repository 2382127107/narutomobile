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

        # 监听任务停止信号以提前终止任务
        # 相当于用户按下了“停止”按钮
        if context.tasker.stopping:
            logger.info("Task is stopping, exiting MyAction111 early.")
            return CustomAction.RunResult(success=False)

        # 执行自定义任务
        # ...

        return CustomAction.RunResult(success=True)
