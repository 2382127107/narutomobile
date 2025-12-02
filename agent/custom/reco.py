from maa.define import Rect
from maa.agent.agent_server import AgentServer
from maa.custom_recognition import CustomRecognition
from maa.context import Context

from numpy import ndarray, log

from utils.logger import logger


def get_senryoku(context: Context, image: ndarray, roi: list[int]) -> int | None:
    """
    获取战力
    """
    reco_detail = context.run_recognition(
        "GetSenryokuText",
        image,
        {
            "GetSenryokuText": {"roi": roi},
        },
    )

    if reco_detail is None or not reco_detail.hit:
        logger.debug(reco_detail)
        logger.warning("无法读取到战力！")
        return None

    source_text = str(reco_detail.best_result.text)  # type: ignore
    if source_text.endswith("万"):
        text = source_text[:-1]
        text += "0000"
    else:
        text = source_text

    if text.isdigit():
        logger.info(f"读取到战力：{source_text}")
        return int(text)

    logger.warning(f"战力解析错误：{source_text}")
    return None


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
        logger.info("尝试读取我方小队战力...")
        team_senryoku = get_senryoku(context, argv.image, [271, 337, 178, 29])
        if team_senryoku is None:
            return CustomRecognition.AnalyzeResult(
                box=None,
                detail={},
            )

        enemy_roi_list = [
            [843, 236, 100, 30],
            [843, 352, 96, 31],
            [843, 472, 103, 27],
            [843, 589, 97, 29],
        ]

        logger.info("尝试读取敌方小队战力...")
        for idx, roi in enumerate(enemy_roi_list):
            enemySenryoku = get_senryoku(context, argv.image, roi)
            if enemySenryoku is None:
                logger.warning(f"无法读取到敌队{idx + 1}的战力！")
                return CustomRecognition.AnalyzeResult(
                    box=None,
                    detail={},
                )

            if enemySenryoku > team_senryoku:
                logger.warning(
                    f"敌队{idx + 1}的战力 {enemySenryoku // 10000}万 大于小队战力 {team_senryoku // 10000}万！"
                )
                continue

            logger.info(
                f"敌队{idx + 1}的战力 {enemySenryoku // 10000}万 小于小队战力 {team_senryoku // 10000}万！"
            )
            reco_detail = context.run_recognition(
                "point_race_get_chanllenge_button",
                argv.image,
                {
                    "point_race_get_chanllenge_button": {
                        "index": idx,
                    }
                },
            )
            if reco_detail is None or not reco_detail.hit:
                logger.error(f"无法找到敌队{idx + 1}的挑战按钮！")
                return CustomRecognition.AnalyzeResult(
                    box=None,
                    detail={},
                )

            return CustomRecognition.AnalyzeResult(
                box=reco_detail.box,
                detail={},
            )

        logger.info(f"没一个打得过的，溜了溜了。")
        return CustomRecognition.AnalyzeResult(
            box=None,
            detail={},
        )
