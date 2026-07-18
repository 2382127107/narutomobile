import json

from maa.agent.agent_server import AgentServer
from maa.context import Context
from maa.custom_recognition import CustomRecognition
from numpy import ndarray
from utils.logger import logger

from ..utils import get_digit_count


@AgentServer.custom_recognition("FindToChallenge")
class FindToChallenge(CustomRecognition):
    """
    在积分赛中寻找可以挑战的对象
    """

    def analyze(
        self,
        context: Context,
        argv: CustomRecognition.AnalyzeArg,
    ) -> CustomRecognition.AnalyzeResult:
        fource_battle = json.loads(argv.custom_recognition_param).get("fource_battle", False)
        if fource_battle:
            logger.info("当前配置：强制挑战")
        else:
            logger.info("当前配置：非强制挑战")

        logger.info("尝试读取我方小队战力...")
        team_senryoku = self.get_senryoku(context, argv.image, [271, 337, 178, 29])
        if team_senryoku is None:
            return CustomRecognition.AnalyzeResult(
                box=None,
                detail={},
            )

        enemy_rois = [
            [841, 234, 115, 32],
            [841, 352, 113, 32],
            [841, 471, 115, 32],
            [841, 589, 111, 29],
        ]

        logger.info("尝试读取敌方小队战力...")

        enemySenryoku_list = []

        for roi in enemy_rois:
            senryoku = self.get_senryoku(
                context,
                argv.image,
                roi,
                default=1145141919810,  # 一个非常大的数，表示无法挑战
            )
            if senryoku:
                enemySenryoku_list.append(senryoku)
            else:
                logger.warning(f"无法解析战力文本: {enemy_rois.index(roi) + 1}")
                enemySenryoku_list.append(1145141919810)

        min_enemySenryoku = min(enemySenryoku_list)
        idx = enemySenryoku_list.index(min_enemySenryoku)
        logger.info(f"敌队{idx + 1}战力最低：{min_enemySenryoku / 10000}万")

        if (min_enemySenryoku > team_senryoku) and (not fource_battle):
            logger.info("没一个打得过的，溜了溜了。")
            return CustomRecognition.AnalyzeResult(
                box=None,
                detail={},
            )

        logger.info(f"挑战敌队{idx + 1}!")
        targets = [
            [986, 195, 92, 39],
            [987, 312, 92, 39],
            [988, 430, 92, 39],
            [987, 548, 92, 39],
        ]

        return CustomRecognition.AnalyzeResult(
            box=targets[idx],
            detail={},
        )

    def get_senryoku(self, context: Context, image: ndarray, roi: list[int], default=None) -> int | None:
        """
        获取战力
        """
        value, source_text = get_digit_count(context, image, roi, default=default)
        if value is None or source_text is None:
            logger.error(f"无法解析战力 ROI: {roi}")
            return None

        if source_text.endswith("万"):
            value *= 10000
        logger.info(f"读取到战力：{value}")
        return value
