#!/usr/bin/env python3
"""Attach date-anchored, explicitly retrospective literature reviews to old reports."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from build_public_data import (
    atomic_json_write,
    public_publication_opportunities,
    public_related_work_review,
)


ROOT = Path(__file__).resolve().parents[1]
RETRIEVED_AT = "2026-09-17"
SEARCH_WINDOW = "主要覆盖2021-09-17至2026-09-17；直接相关的经典基线研究适度向前回溯。"
SOURCES = ["OpenAlex", "学术网页主题检索", "期刊/出版社论文页面与摘要"]


def work(title: str, year: int, doi: str, relation: str) -> dict[str, str]:
    return {
        "title": title,
        "year": str(year),
        "doi": doi,
        "url": f"https://doi.org/{doi}",
        "relation": relation,
    }


def theme(
    title: str,
    related: str,
    increment: str,
    gap: str,
    judgment: str,
    angle: str,
    validation: str,
    risk: str,
    confidence: str,
    works: list[dict[str, str]],
) -> dict[str, Any]:
    return {
        "title": title,
        "related_work_status": [related],
        "today_increment": [increment],
        "research_gap": [gap],
        "secondary_judgment": [judgment],
        "paper_angle": [angle],
        "minimum_validation": [validation],
        "novelty_risk": [risk],
        "confidence": confidence,
        "representative_works": works,
    }


def opportunity(
    title: str,
    gap: str,
    why: str,
    plan: str,
    contribution: str,
    evidence_dois: list[str],
    risk: str,
    article_type: str,
) -> dict[str, Any]:
    return {
        "title": title,
        "research_gap": [gap],
        "why_worth_doing": [why],
        "recommended_work": [plan],
        "paper_contribution": [contribution],
        "daily_evidence_dois": evidence_dois,
        "daily_evidence": ["所列论文均取自对应日期日报；这些是研究判断的锚点，不是外部查新文献。"],
        "main_risks": [risk],
        "article_type": article_type,
    }


REVIEWS: dict[str, dict[str, Any]] = {
    "2026-09-13": {
        "anchor_article_count": 10,
        "search_scope": [
            "液氙 LZ 脉冲形状判别、光子到达时间与波形分类",
            "EJ-315 氘化液闪的中子响应、准单能标定与能谱反演",
            "HPGe 与 UAV/UAS γ 能谱的现场校准、响应建模及计量溯源",
            "卤化物闪烁体的 X 射线成像、空间分辨率与辐照/环境稳定性",
        ],
        "related_works": [
            work("Detector signal characterization with a Bayesian network in XENONnT", 2023, "10.1103/PhysRevD.108.012016", "APS 期刊原文；基于 XENONnT 实测电子反冲数据做波形属性的贝叶斯信号刻画。"),
            work("A machine learning-based methodology for pulse classification in dual-phase xenon time projection chambers", 2022, "10.1140/epjc/s10052-022-10502-x", "Springer 期刊原文；LZ 模拟数据被用作真实数据代理，不能与实测部署结果等同。"),
            work("Response characterization for an EJ315 deuterated organic-liquid scintillation detector for neutron spectroscopy", 2013, "10.1016/j.nima.2013.05.172", "EJ-315 中子响应矩阵与光输出基线；经典工作，超出近五年窗口。"),
            work("Neutron light output function and resolution investigation of the deuterated organic liquid scintillator EJ-315", 2016, "10.1016/j.radmeas.2016.03.009", "ScienceDirect 期刊原文；含飞行时间、PSD 与准单能中子响应研究，属经典基线。"),
            work("Determination of neutron spectrum based on artificial neural network using liquid scintillation detector EJ-301", 2024, "10.1093/rpd/ncae189", "Oxford Academic 期刊原文；ANN 主要以 FLUKA 模拟响应训练，并用 Cf 测量作验证；材料为 EJ-301，并非 EJ-315。"),
            work("Calibration of an airborne γ-ray spectrometer based on an unmanned aerial vehicle using a point source", 2022, "10.1016/j.anucene.2022.109349", "ScienceDirect 期刊原文；覆盖 UAV 点源校准、航高衰减与多项现场影响修正。"),
            work("Spectroscopic performance evaluation and modeling of a low background HPGe detector using GEANT4", 2024, "10.1016/j.nima.2023.168826", "ScienceDirect 期刊原文；以实测峰形、效率等检验低本底 HPGe 的 GEANT4 模型。"),
            work("Ultrastable and flexible glass-ceramic scintillation films with reduced light scattering for efficient X-ray imaging", 2024, "10.1038/s41528-024-00319-x", "Nature 期刊原文；给出柔性玻璃陶瓷闪烁屏的空间分辨率与多种稳定性测试。"),
            work("Efficient X-ray luminescence imaging with ultrastable and eco-friendly copper(I)-iodide cluster microcubes", 2023, "10.1038/s41377-023-01208-0", "Nature 期刊原文；展示 Cu(I)-I 团簇微晶、抗湿/抗 X 射线稳定性与柔性屏应用。"),
        ],
        "themes": [
            theme(
                "液氙波形判别：从分类器转向物理量联合与跨数据验证",
                "双相氙 TPC 已有 XENONnT 实测的贝叶斯波形属性分析，也有用 LZ 模拟数据作代理的机器学习分类流程。",
                "9/13 锚点把光子到达时间尾部特征与电荷/光信息联合；“首次把机器学习用于液氙脉冲分类”不成立。",
                "现有工作间数据集、能区、标签来源与评估指标并不统一；低能区、漂移时间和探测器状态变化下的泛化仍需同一基准检验。",
                "方向有研究空间，但贡献应落在可解释的物理特征、独立实测验证及系统误差，而不是换一个分类算法。",
                "构建 photon-timing 与 S1/S2 互补判别，并在不同校准期/独立运行数据上检验稳定性。",
                "使用真实校准或物理运行数据；留出独立测试集；与传统 cut、贝叶斯方法及现有 ML 同指标对比；报告效率、泄漏率、能区依赖和不确定度。",
                "通用 ML/波形分类新颖性风险高；2022 工作有模拟代理数据边界，不能将模拟精度直接当作实测性能。",
                "中等",
                [work("Detector signal characterization with a Bayesian network in XENONnT", 2023, "10.1103/PhysRevD.108.012016", "实测波形特征分类基线。"), work("A machine learning-based methodology for pulse classification in dual-phase xenon time projection chambers", 2022, "10.1140/epjc/s10052-022-10502-x", "模拟代理数据上的分类流程基线。")],
            ),
            theme(
                "EJ-315 中子响应：紧凑几何、响应矩阵与谱反演",
                "EJ-315 的中子光输出、响应矩阵、TOF 测量与 PSD 已有多年基线；另有 EJ-301 的 ANN 能谱反演，但那是不同闪烁液且训练依赖模拟。",
                "9/13 锚点关注紧凑型 EJ-315 在准单能中子场中的表征，不应将“首次表征 EJ-315”或“首次液闪中子谱反演”作为发文主张。",
                "值得核实的是小体积/不同几何下响应矩阵是否可迁移，以及探测器响应、PSD 误判和谱反演不确定度如何共同影响结果。",
                "更可辩护的增量是紧凑几何下的独立响应校准和测量验证，而不是重复测一条光输出曲线。",
                "建立紧凑 EJ-315 的实测响应矩阵，并与大体积/既有参数模型比较其能量与几何迁移误差。",
                "至少使用多组已知中子能量；报告源能散、TOF/PSD 选择、γ 泄漏、几何效应、响应矩阵协方差和独立谱验证。",
                "2013/2016 已直接研究 EJ-315；EJ-301 ANN 不能当作 EJ-315 的直接验证；须明确与已有曲线/响应矩阵的差异。",
                "中等",
                [work("Response characterization for an EJ315 deuterated organic-liquid scintillation detector for neutron spectroscopy", 2013, "10.1016/j.nima.2013.05.172", "EJ-315 响应矩阵基线；经典工作。"), work("Neutron light output function and resolution investigation of the deuterated organic liquid scintillator EJ-315", 2016, "10.1016/j.radmeas.2016.03.009", "TOF、PSD、光输出和分辨率基线；经典工作。"), work("Determination of neutron spectrum based on artificial neural network using liquid scintillation detector EJ-301", 2024, "10.1093/rpd/ncae189", "相邻的 EJ-301 模拟训练/测量验证方法，不等同于 EJ-315。")],
            ),
            theme(
                "现场 γ 能谱与 HPGe：校准链、环境修正和不确定度传递",
                "UAV γ 谱已有点源校准与航高/本底等修正研究；HPGe 也已有用 GEANT4 对效率和峰形作实验验证的工作。",
                "9/13 锚点同时覆盖地面/UAS 数据分析、HPGe 内部性能检验和中子注量场次级标准化，研究对象是多种测量链而非同一台仪器。",
                "各流程中的点源效率、探测器模型、航高/地形/氡本底修正与量值溯源通常分别处理；跨链路不确定度如何传至活度/注量结论值得补齐。",
                "可形成计量与应用结合的工作，但不可把不同探测器的校准结果简单拼成一个“通用算法”。",
                "围绕同一批标准源或可溯源参考场，对地面谱、UAS 谱与 HPGe 模型做独立交叉核验，并显式传播修正因子不确定度。",
                "给出校准证书/参考值、几何与航高、背景扣除、效率模型残差、重复测量和不确定度预算；说明各仪器链的适用边界。",
                "点源 UAV 校准与 HPGe GEANT4 建模都已有先例；创新应来自具体场景、可复用校准数据或完整不确定度闭环。",
                "中等",
                [work("Calibration of an airborne γ-ray spectrometer based on an unmanned aerial vehicle using a point source", 2022, "10.1016/j.anucene.2022.109349", "UAV 点源校准与现场修正先例。"), work("Spectroscopic performance evaluation and modeling of a low background HPGe detector using GEANT4", 2024, "10.1016/j.nima.2023.168826", "HPGe 实测性能与 GEANT4 响应交叉验证。")],
            ),
            theme(
                "卤化物闪烁体：材料指标之外的成像屏可比性",
                "Cu(I)-I 团簇柔性屏和玻璃陶瓷屏已展示 X 射线成像及稳定性；高分辨材料论文数量多，材料名称或单项光产额不足以证明空白。",
                "9/13 的 Mn 基卤化物、Ag(I) 卤化物、Cs₃Cu₂I₅ 与钙钛矿/类钙钛矿论文把材料设计、薄膜/涂层与 X 射线探测同时推到前台。",
                "论文常用不同厚度、剂量率、光学耦合和成像系统报告光产额、检出限与 lp/mm，跨论文数值无法直接排优劣；长期老化也常不足。",
                "机会在同条件器件级验证、稳定性和应用约束；不宜仅凭某一个新配方或摘要指标主张“首个高分辨闪烁体”。",
                "在统一基板/厚度/光学耦合下比较候选卤化物屏的 MTF、DQE/灵敏度、辐照稳定性与湿热老化。",
                "统一 X 射线谱与剂量、膜厚、探测器和处理链；至少重复制样；报告 MTF、光产额/检出限定义、辐照累计剂量及老化前后变化。",
                "领域拥挤且指标口径分散；缺少严格同条件对照时，跨论文性能排序与材料优越性结论不可靠。",
                "中低",
                [work("Ultrastable and flexible glass-ceramic scintillation films with reduced light scattering for efficient X-ray imaging", 2024, "10.1038/s41528-024-00319-x", "柔性屏高分辨率与环境/辐照稳定性的器件级基线。"), work("Efficient X-ray luminescence imaging with ultrastable and eco-friendly copper(I)-iodide cluster microcubes", 2023, "10.1038/s41377-023-01208-0", "Cu(I)-I 团簇材料、抗湿性及柔性成像屏先例。")],
            ),
        ],
        "opportunity_specs": [
            opportunity("卤化物闪烁屏的同条件成像与老化基准", "多种 9/13 材料论文都报告成像性能，但厚度、剂量和相机链不同，当前难以作公平比较。", "若能给出同条件器件级数据，可把材料新颖性判断转为可复验的工程性能贡献。", "挑选可稳定制备的 2–3 种候选屏，在同基板、厚度与成像链下测 MTF/DQE、灵敏度、湿热与累计剂量漂移。", "形成可复用的材料—屏结构—成像指标比较数据，而非只报告单样品最佳值。", ["10.1002/lpor.71880", "10.1021/acs.inorgchem.6c02724", "10.1002/adfm.78388", "10.1021/acsami.6c09525", "10.1021/acsenergylett.6c01440"], "需要获得可比样品并固定测试链；新材料合成若缺少机理与器件优势，投稿贡献会偏弱。", "材料与成像实验"),
            opportunity("紧凑 EJ-315 的实测响应矩阵迁移与中子谱反演", "已知 EJ-315 响应基线不能自动保证在紧凑体积、不同光收集和实验室几何下仍可直接沿用。", "将材料响应表征推进到小型仪器校准和未知谱验证，应用目标清楚。", "围绕 9/13 紧凑 EJ-315 论文的几何建立多能点实测矩阵；用盲测混合谱检验响应迁移、γ 泄漏与反演不确定度。", "给出紧凑探测器在实际中子谱测量中的可追溯误差边界。", ["10.1088/1748-0221/21/09/p09018"], "EJ-315 光输出和响应矩阵已有直接先例，必须证明新几何/校准/测量条件带来可量化的新能力。", "探测器标定与方法验证"),
            opportunity("液氙 PSD 的跨运行期独立复核", "LZ 新 PSD 特征需与已有 waveform 分类/贝叶斯方法在一致数据划分和物理工作点下比较。", "若在真实独立运行数据上证明更稳健的泄漏—效率权衡，可形成可复核的方法论文。", "固定基线选择与盲测数据；对 photon-time tail、S1/S2、贝叶斯特征和既有 cuts 做消融比较，并按能区/运行期拆分。", "量化额外光子计时信息的独立收益及系统误差对 PSD 的影响。", ["10.1140/epjc/s10052-026-16216-8"], "泛化的波形分类已很拥挤；若只替换分类器或复述 LZ 结果，不足以支撑新颖性。", "实测数据分析"),
            opportunity("UAS/HPGe γ 能谱校准链的场景化不确定度预算", "点源 UAV 校准、HPGe 模拟效率和现场谱修正各有先例，但当它们串入同一个测量结论时误差传递常不透明。", "能把可溯源校准、环境修正和现场验证闭合起来，对污染巡测/原位测量有直接价值。", "用参考源或可溯源测量作地面与 UAS 交叉测试，同时给出 HPGe/谱响应验证、航高和本底修正的逐项不确定度。", "提供一套可审计的现场 γ 谱测量质量控制流程。", ["10.1088/1748-0221/21/09/t09002", "10.14311/ap.2026.66.0421", "10.15392/2319-0612.2026.3068"], "HPGe、UAS γ 谱与中子注量标准装置并非同一系统；研究设计需围绕量值溯源/误差传播，而非声称三种仪器可以直接互校。", "计量与现场方法"),
        ],
        "overall_judgment": "9/13 日报呈现的是四条并行线索，而不是单一研究主题。相对可操作的优先顺序是：先做卤化物屏同条件基准或紧凑 EJ-315 的实测验证；液氙 PSD 与 UAS/HPGe 方向也有论文空间，但都必须用独立数据和完整系统误差区别于既有工作。仅凭本次有限回溯不能判断任何方向“全球首次”。",
        "limitations": [
            "本条为 2026-09-17 执行的历史回溯查新；检索锚点是 9/13 日报收录的 10 篇论文，不是 9/13 当时已经形成的查新结论。",
            "候选/核实计数仅统计页面列出的代表性论文；检索窗口以近五年为主，EJ-315 响应基线额外纳入 2013/2016 年工作；不是穷尽式系统综述。",
            "判断依据以期刊/出版社可见题录和摘要为主；付费全文中的实验细节仍需作者逐篇核验，不能据此断言无先行工作或全球首发。",
        ],
    },
    "2026-09-14": {
        "anchor_article_count": 7,
        "search_scope": [
            "electron-tracking Compton camera 三维反冲电子径迹、图像/波形联合读出与重建",
            "质子治疗提示伽马成像、Compton camera 射程位移与重建算法",
            "GAGG 快响应、辐照耐受、afterglow 与量热器束流测试",
            "Mn/CuI 柔性卤化物闪烁体、9,9-dimethylfluorene 塑闪与低光量读出",
        ],
        "related_works": [
            work("Development of convolutional neural networks for an electron-tracking Compton camera", 2021, "10.1093/ptep/ptab091", "Oxford Academic 期刊原文；包含模拟重建和校准数据验证，既有方法基线。"),
            work("Proton range verification with MACACO II Compton camera enhanced by a neural network for event selection", 2021, "10.1038/s41598-021-88812-5", "Nature 期刊原文；原型束流数据与神经网络事件筛选的质子射程验证先例。"),
            work("Comparison of reconstructed prompt gamma emissions using maximum likelihood estimation and origin ensemble algorithms for a Compton camera system tailored to proton range monitoring", 2023, "10.1016/j.zemedi.2022.04.005", "ScienceDirect 期刊原文；比较 MLEM/SOE，并显式讨论异质靶中的射程相关性。"),
            work("Accurate proton range shift verification by using a two-layer dense-pixel LYSO compton camera prototype", 2024, "10.1016/j.nima.2024.169339", "ScienceDirect 期刊原文；13 MeV 真实质子束原型试验报告 2 mm 量级位移辨识。"),
            work("Irradiation effects on Gd3Al2Ga3O12 scintillators prospective for application in harsh irradiation environments", 2019, "10.1016/j.radphyschem.2019.108365", "ScienceDirect 期刊原文；GAGG 在质子辐照后光学、计时与辐射诱导发光的基线。"),
            work("Performance of a spaghetti calorimeter prototype with tungsten absorber and garnet crystal fibres", 2023, "10.1016/j.nima.2022.167629", "ScienceDirect 期刊原文；GAGG/YAG 晶体纤维量热器有 1–5 GeV 束流测试。"),
            work("Fluorene Derivatives for Efficient Prompt Scintillation in Plastic Scintillators", 2022, "10.1021/acsapm.2c00391", "ACS 期刊原文；已有芴衍生物改性塑料闪烁体，报告高光产额与纳秒级快响应。"),
            work("Development of plastic scintillators containing 9,9-dimethylfluorene for high scintillation light yields", 2026, "10.1016/j.jlumin.2026.121972", "同年近邻研究：同属 PS/9,9-dimethylfluorene 配方方向；网页报告 13,300 photons/MeV 与 1.1–1.4 ns 首分量。"),
            work("Efficient X-ray luminescence imaging with ultrastable and eco-friendly copper(I)-iodide cluster microcubes", 2023, "10.1038/s41377-023-01208-0", "Nature 期刊原文；Cu(I)-I 团簇柔性屏与抗湿/抗 X 射线稳定性基线。"),
            work("Ultrastable and flexible glass-ceramic scintillation films with reduced light scattering for efficient X-ray imaging", 2024, "10.1038/s41528-024-00319-x", "Nature 期刊原文；柔性 X 射线屏的 MTF/空间分辨率与稳定性对照。"),
        ],
        "themes": [
            theme(
                "Compton 成像：径迹重建与质子射程验证要分开比较",
                "ETCC 已有 CNN 重建反冲方向/散射位置的先例；质子治疗方向已有 MACACO II 束流试验及 MLEM/SOE 重建比较，另有 LYSO 相机实束流验证。",
                "9/14 的 ETCC 论文把二维光学图像和一维波形用于模拟条件下的 3D 方向推断；同日报射程论文则是实际质子束下的另一种晶体 Compton 原型。",
                "ETCC 的低能气体径迹重建与治疗用晶体相机在相互作用介质、能区和指标上不同；当前缺口是 ETCC 伪实验到独立真实数据的落差，以及射程系统跨束流/靶材的鲁棒性。",
                "可以围绕“从模拟到真实数据”的证据闭环开展研究；不可把两种装置的角分辨率或射程精度直接横向比较。",
                "先验证 ETCC 光学+波形重建的真实束流可迁移性；另对质子射程相机按束流强度、靶材和重建算法作盲测。",
                "逐项报告真实光学噪声/增益漂移、电子径迹起点和角分辨率；质子相机则报告计数统计、靶材/距离、位移阈值及基线算法。",
                "Compton 相机与质子射程监测均有多篇实测/重建先例；一般性的‘用深度学习提高精度’新颖性风险高。",
                "中等",
                [work("Development of convolutional neural networks for an electron-tracking Compton camera", 2021, "10.1093/ptep/ptab091", "ETCC CNN 重建及校准数据基线。"), work("Proton range verification with MACACO II Compton camera enhanced by a neural network for event selection", 2021, "10.1038/s41598-021-88812-5", "提示伽马与 NN 事件筛选的束流验证先例。"), work("Comparison of reconstructed prompt gamma emissions using maximum likelihood estimation and origin ensemble algorithms for a Compton camera system tailored to proton range monitoring", 2023, "10.1016/j.zemedi.2022.04.005", "异质靶的 MLEM/SOE 重建比较。"), work("Accurate proton range shift verification by using a two-layer dense-pixel LYSO compton camera prototype", 2024, "10.1016/j.nima.2024.169339", "实质子束下 LYSO Compton 相机验证。")],
            ),
            theme(
                "GAGG 快量热：辐照后性能不能只看透过率",
                "已有 GAGG 高质子注量辐照研究，也有含 GAGG 晶体纤维的束流量热器原型；关注点包括诱导吸收、afterglow、快响应与系统时间分辨率。",
                "9/14 的 arXiv 预印本报告共掺杂后有效衰减时间最低约 5.5 ns，并给出高能束流和 1 MGy 辐照相关结果。",
                "还需在同一批样品、同一读出链中把辐照前后光产额、衰减分量、余辉、定时分辨和恢复过程连起来；报告条件应与先行研究可比。",
                "值得做独立复现或应用工况验证，但该日 GAGG 工作是预印本，当前只能视为待同行评议结果。",
                "做剂量/剂量率扫描并测辐照前后余辉和时间分辨，区分材料本征快分量与探测器/电子学时间抖动。",
                "独立样品与批次；注明粒子能量、束流、剂量率、总剂量、恢复时间；同时报告光产额/透过率/afterglow/时间指标和测量系统响应。",
                "GAGG 辐射硬度、快量热和辐照诱导余辉已有研究；若只复述单一剂量的透光率或衰减常数，增量有限。",
                "中低（因锚点为预印本）",
                [work("Irradiation effects on Gd3Al2Ga3O12 scintillators prospective for application in harsh irradiation environments", 2019, "10.1016/j.radphyschem.2019.108365", "质子辐照、计时属性与残余发光的先行基线。"), work("Performance of a spaghetti calorimeter prototype with tungsten absorber and garnet crystal fibres", 2023, "10.1016/j.nima.2022.167629", "GAGG 晶体纤维量热器束流性能先例。")],
            ),
            theme(
                "塑料闪烁体与芴类配方：同日已有高度相似先行线索",
                "2022 年已有氟烯/芴衍生物改性塑闪；当前检索还发现 2026 年同属 PS/9,9-dimethylfluorene 的另一篇近邻研究，报道不同光产额和衰减时间。",
                "9/14 日报的 9,9-dimethylfluorene 配方结果应与这两条工作逐项比较；“首次把芴类加入塑闪”显然不能作为主张。",
                "值得区分的是主体/共掺剂比例、绝对光产额标定、快慢分量、粒子种类依赖、光学衰减和辐照前后性能，而非只比较某一个 photons/MeV 数值。",
                "领域已有直接材料近邻，单纯配方优化的新颖性风险高；若能补足稳定复现的材料物性和探测器级性能，仍可形成增量。",
                "用统一光产额基准和时间分辨装置复配 PS/芴系列，比较 DPO/POPOP、衰减分量及实际 SiPM/PMT 读出表现。",
                "提供完整样品配方/制备、绝对光产额校准、光谱、快慢衰减、样品重复、γ/中子响应与误差；与 2022 和 2026 近邻研究同口径对比。",
                "同年出现高度相似的 9,9-dimethylfluorene 主体研究，优先核对原文配方/发布时间和重叠结果；新颖性风险高。",
                "中等（相似工作已定位；细节仍须读全文）",
                [work("Fluorene Derivatives for Efficient Prompt Scintillation in Plastic Scintillators", 2022, "10.1021/acsapm.2c00391", "芴衍生物提高塑闪光产额的期刊工作。"), work("Development of plastic scintillators containing 9,9-dimethylfluorene for high scintillation light yields", 2026, "10.1016/j.jlumin.2026.121972", "同年 PS/9,9-dimethylfluorene 近邻配方研究，需与日报锚点全文对照。")],
            ),
            theme(
                "柔性卤化物 X 射线闪烁：比较器件而非孤立的材料指标",
                "Cu(I)-I 柔性 X 射线屏和玻璃陶瓷屏已报告空间分辨率及稳定性；材料屏领域已有多种化学路线。",
                "9/14 的 Mn 基材料、铜碘杂化材料各自增加了偏振/温度或自陷激子/柔性成像属性。",
                "不同研究的光产额、检出限、lp/mm 受剂量率、厚度、基底、相机与处理方法共同影响；长期辐照与批次差异常未统一。",
                "可以做有控制的器件级对照或功能耦合研究；仅凭较高摘要数字无法判定材料全面更优。",
                "针对目标应用选取 Mn 与 CuI 柔性屏，在同一成像链下比较空间分辨、响应速度、温度/湿度和 X 射线累计剂量稳定性。",
                "统一屏厚、X 射线条件和相机；测 MTF、剂量响应、余辉/衰减、重复样品，并分别报告偏振、温度等附加功能。",
                "材料体系拥挤、指标口径不一；不同能量转移机制不宜只凭最佳光产额或单幅图像作结论。",
                "中低",
                [work("Efficient X-ray luminescence imaging with ultrastable and eco-friendly copper(I)-iodide cluster microcubes", 2023, "10.1038/s41377-023-01208-0", "Cu(I)-I 柔性屏和稳定性参考。"), work("Ultrastable and flexible glass-ceramic scintillation films with reduced light scattering for efficient X-ray imaging", 2024, "10.1038/s41528-024-00319-x", "柔性高分辨屏与环境/辐照稳定性参考。")],
            ),
        ],
        "opportunity_specs": [
            opportunity("ETCC 光学—波形联合重建的真实数据域验证", "9/14 ETCC 性能主要来自 Geant4/MAGBOLTZ 模拟与伪实验；光学噪声、增益漂移和真实束流径迹会改变重建。", "把模拟改善落实到真实校准/束流数据，是决定方法能否进入成像应用的关键证据。", "冻结模型后采集独立束流数据；按电子能量、漂移和光学条件分层，并与既有 CNN/条带读出和尽可能完整的 3D 参考作盲测。", "给出模拟到实测的性能落差、真实噪声下可达角分辨率与系统适用边界。", ["10.1093/ptep/ptag171"], "需要获得 ETCC 原型与真实校准数据；其他 Compton 相机的指标不可直接充作 ETCC 性能。", "探测器方法验证"),
            opportunity("质子射程 Compton 相机的跨靶材/束流鲁棒性", "已报道 1–2 mm 级位移辨识的原型结果，需要确认在改变束流强度、靶材、探测距离和本底后是否仍成立。", "临床相关条件下的独立复现比再提出一个模拟重建算法更能增加证据价值。", "按预注册的束流强度、靶材与距离矩阵，盲测 Bragg 峰位移；同时对事件筛选、时间门和 MLEM/SOE 选项做消融。", "建立可复用的最低计数、位移阈值和误差预算，说明原型从受控条件到治疗中心的边界。", ["10.1016/j.radphyschem.2026.114447"], "9/14 的日报锚点本身已含治疗中心测试；后续须扩展到独立中心/工况，不能重复原型现有实验。", "束流实验与仪器验证"),
            opportunity("GAGG 超快响应的剂量—余辉—时间分辨联合复现", "共掺杂预印本报告了快响应和高剂量辐照，既有 GAGG 文献提示辐照后的残余发光可能影响高率量热。", "直接测量剂量后余辉和时序恢复，可验证材料指标是否转化成高亮度束流下的量热性能。", "对独立晶体样品作多个剂量率/总剂量点；联测透过率、光产额、衰减曲线、afterglow、能量和时间分辨。", "提供预印本结论的独立实验复核和面向高占空比量热的可用窗口。", ["10.48550/arxiv.2609.10116"], "锚点为尚未正式同行评议的预印本；需获得束流资源并严格量化系统时间抖动。", "材料辐照与束流实验"),
            opportunity("芴类塑闪的绝对光产额与探测器级快响应对照", "日报塑闪配方与 2022 芴衍生物工作、同年 9,9-dimethylfluorene 近邻论文存在明显重叠。", "若新配方在统一校准下同时改善光产额、时间/粒子鉴别或辐照稳定性，仍可能形成清晰的应用增量。", "复配同系列样品，统一绝对光产额参考；测试快慢分量、γ/中子 PSD、SiPM/PMT 光收集及辐照老化。", "把化学组成变化与实用探测器性能建立可复验映射，而非仅对比单一最佳数值。", ["10.1016/j.jlumin.2026.122156", "10.48550/arxiv.2609.08427"], "已经找到高度相似的 2022/2026 塑闪工作；必须先做逐配方、逐指标重叠审查，再决定是否值得立项。", "材料与低光量读出"),
        ],
        "overall_judgment": "9/14 的工作覆盖气体 ETCC、质子治疗 Compton 相机、快闪烁材料和低光量读出，不能合并成一个单一结论。最清晰的投稿机会是把模拟结果推进到独立真实数据/束流验证；塑闪 9,9-dimethylfluorene 路线已发现高度相似的 2022 与 2026 研究，需先做重叠审查，不能以首次使用该分子作主张。",
        "limitations": [
            "本条为 2026-09-17 执行的历史回溯查新；检索锚点是 9/14 日报的 7 篇论文。两篇 arXiv 锚点（GAGG 与 SUBMET）按预印本处理，未标成同行评审论文。",
            "候选/核实计数仅统计页面列出的代表性论文；窗口以近五年为主，GAGG 辐照基线包含 2019 年工作；不等于系统综述。",
            "9,9-dimethylfluorene 近邻研究与日报塑闪论文题材高度重叠；这提示风险，不代表两篇论文的具体配方、投稿时间或数据必然相同，需对照全文/版本记录。",
            "Compton 气体径迹相机和治疗用晶体相机结构、能区与任务不同，引用它们是分别定位方法和应用先例，不作同一性能的直接横比。",
        ],
    },
    "2026-09-15": {
        "anchor_article_count": 6,
        "search_scope": [
            "玻璃微通道板与结构化闪烁屏的串扰、MTF、DQE 和分辨率",
            "钙钛矿单晶/异质结 X 射线直接探测、离子迁移和器件稳定性",
            "STIX 栅格传输率、在轨自标定与太阳硬 X 射线成像校准",
            "核物理符合测量、塑料闪烁体 SiPM 读出与时间分辨率",
        ],
        "related_works": [
            work("Influence of Si wall thickness of CsI(Tl) micro-square-frustums on the performance of the structured CsI(Tl) scintillation screen in X-ray imaging", 2022, "10.1038/s41598-022-12673-9", "Nature 期刊原文；以 MTF、DQE 和光输出研究结构化屏壁厚，部分为模拟优化。"),
            work("A sealed X-ray microchannel plate imager with CsI photocathode to improve quantitative precision of framing camera", 2021, "10.1016/j.nima.2021.165404", "ScienceDirect 期刊原文；MCP X 射线成像器件先例，但结构并非同一种玻璃微通道闪烁屏。"),
            work("Ultrastable and flexible glass-ceramic scintillation films with reduced light scattering for efficient X-ray imaging", 2024, "10.1038/s41528-024-00319-x", "Nature 期刊原文；柔性闪烁屏空间分辨率与稳定性对照。"),
            work("Designer bright and fast CsPbBr3 perovskite nanocrystal scintillators for high-speed X-ray imaging", 2024, "10.1038/s41467-024-53263-9", "Nature 期刊原文；报告快速衰减与高速、高空间分辨 X 射线成像。"),
            work("Suppressed ion migration for high-performance X-ray detectors based on atmosphere-controlled EFG-grown perovskite CsPbBr3 single crystals", 2024, "10.1038/s41566-024-01480-5", "Nature 期刊原文；用受控气氛 EFG 生长降低离子迁移和基线漂移。"),
            work("Stable perovskite single-crystal X-ray imaging detectors with single-photon sensitivity", 2023, "10.1038/s41566-023-01207-y", "Nature 期刊原文；直接 X 射线探测、单光子灵敏度与稳定性先例。"),
            work("First Hard X-Ray Imaging Results by Solar Orbiter STIX", 2022, "10.1007/s11207-022-02029-x", "Springer 期刊原文；STIX 子准直器可见度振幅/相位校准及成像先例。"),
            work("Full system of positron timing counter in MEG II having time resolution below 40 ps with fast plastic scintillator readout by SiPMs", 2020, "10.1016/j.nima.2019.162785", "ScienceDirect 期刊原文；分段塑闪双端 SiPM 的系统级时间分辨率先例。"),
            work("First experimental demonstration of time-resolved X-ray measurements with next-generation fast-timing MCP-PMT", 2019, "10.1016/j.nima.2019.02.057", "ScienceDirect 期刊原文；MCP-PMT/闪烁体硬 X 射线时间分辨测试；与玻璃微通道闪烁屏非同一器件。"),
        ],
        "themes": [
            theme(
                "微结构 X 射线闪烁屏：MTF 提升必须同时看效率和噪声",
                "结构化 CsI(Tl) 屏已用 MTF、DQE 和光输出优化通道/隔墙；MCP X 射线成像器件也有高时间/空间分辨先例，但工作机理和结构并不等同。",
                "9/15 的玻璃微通道板闪烁屏使用银层降低通道串扰，并对银层深度做模拟/实验分析；全深度银层的进一步提升仍是模拟预测。",
                "目前关键空白不是再报一个高 lp/mm，而是量化银层深度、光收集效率、均匀性、DQE、噪声和可制造性之间的联合权衡。",
                "方向具备明确器件工程价值；全深度银层和性能改进在做出实验前应标作预测，不是已验证结果。",
                "制备多个银层深度/通道结构样品，按同一标准源和成像链测 MTF、DQE、透过率、均匀性及剂量响应。",
                "需有标准线对/斜边 MTF、绝对效率或 DQE、样品重复、像素/视野均匀性、光收集损失及辐照后变化；实验数据须覆盖模拟预测区域。",
                "高分辨屏与 MCP 成像均有大量先例；若关键深度只做模拟，或没有效率/DQE 对照，结论和新颖性都会偏弱。",
                "中等",
                [work("Influence of Si wall thickness of CsI(Tl) micro-square-frustums on the performance of the structured CsI(Tl) scintillation screen in X-ray imaging", 2022, "10.1038/s41598-022-12673-9", "结构化闪烁屏的 MTF/DQE/光输出对照，但主要考察 Si 微结构。"), work("A sealed X-ray microchannel plate imager with CsI photocathode to improve quantitative precision of framing camera", 2021, "10.1016/j.nima.2021.165404", "MCP 成像器件比较；与今日玻璃微通道闪烁屏机理不同。"), work("Ultrastable and flexible glass-ceramic scintillation films with reduced light scattering for efficient X-ray imaging", 2024, "10.1038/s41528-024-00319-x", "柔性闪烁屏的成像性能对照。"), work("Designer bright and fast CsPbBr3 perovskite nanocrystal scintillators for high-speed X-ray imaging", 2024, "10.1038/s41467-024-53263-9", "高速闪烁屏对照；须按相同测试条件比较空间分辨率和时间性能。")],
            ),
            theme(
                "钙钛矿直接探测：异质结增益需与离子迁移/器件稳定性一起评估",
                "单晶钙钛矿直接 X 射线探测已有单光子灵敏度与长期稳定性研究；CsPbBr₃ 生长气氛调控也已用于抑制离子迁移和基线漂移。",
                "9/15 的等比例有机-无机混合阳离子单晶异质结报告整流、迁移活化能、灵敏度和未封装稳定性。",
                "不同论文在偏压、能量、剂量定义、晶体厚度、封装和稳定性测试条件上差异很大；需排除界面/电极及设备漂移后再归因于异质结。",
                "“抑制离子迁移”已有先行路线；更可辩护的增量是同晶体/同偏压控制实验中识别异质结的独立贡献，并验证阵列成像。",
                "制备同批单晶对照与异质结器件，在脉冲/长时偏压下跟踪基线、电流、迁移活化能、滞后和成像信噪比。",
                "多个器件与批次、统一剂量/偏压/温湿度、暗电流/基线漂移、长时照射与恢复、像素阵列或标准图像；报告统计区间和器件失效率。",
                "该方向竞争强且高灵敏度数值高度依赖测试定义；只复现单器件峰值或将未封装短期结果外推为长期可靠性会有高风险。",
                "中等",
                [work("Suppressed ion migration for high-performance X-ray detectors based on atmosphere-controlled EFG-grown perovskite CsPbBr3 single crystals", 2024, "10.1038/s41566-024-01480-5", "用生长气氛抑制迁移、漏电和基线漂移的先行策略。"), work("Stable perovskite single-crystal X-ray imaging detectors with single-photon sensitivity", 2023, "10.1038/s41566-023-01207-y", "单晶直接探测灵敏度和器件稳定性基线。")],
            ),
            theme(
                "仪器校准与读出：在轨响应修正、符合门与时间性能各有先例",
                "STIX 已有在轨可见度校准/硬 X 射线成像研究；塑闪-SiPM 系统也已有低于 40 ps 的系统级计时先例。",
                "9/15 同时出现 STIX 栅格传输率自校准、γ-带电粒子符合谱学和塑闪/SiPM 固定靶探测器原型，分别针对成像、核反应选道和定时。",
                "三套仪器不可直接互校；共同的工程缺口是把读出/标定不确定度连到最终能谱、符合峰背比或时间分辨，并做长期漂移验证。",
                "应按具体仪器任务分别建模；跨领域可借鉴校准与不确定度方法，但不能把 STIX 的结果当作实验室 γ-粒子符合系统的性能证据。",
                "固定靶系统可把通道定时、时间游走、温度系数和效率校准一起测；STIX 可独立复核参考像素/照明假设下的传输模型。",
                "提供独立参考源/时间基准、通道间偏差、温漂、符合效率、死时间、峰背比与重复束流数据；STIX 方向需量化参考像素选择和能区适用性。",
                "相关仪器各自有先例；简单重做单个符合峰或复述 STIX 校准流程不足以构成新方法。",
                "中等",
                [work("First Hard X-Ray Imaging Results by Solar Orbiter STIX", 2022, "10.1007/s11207-022-02029-x", "STIX 成像可见度校准先例。"), work("Full system of positron timing counter in MEG II having time resolution below 40 ps with fast plastic scintillator readout by SiPMs", 2020, "10.1016/j.nima.2019.162785", "塑闪-SiPM 系统级计时的高性能基线。"), work("First experimental demonstration of time-resolved X-ray measurements with next-generation fast-timing MCP-PMT", 2019, "10.1016/j.nima.2019.02.057", "MCP-PMT 快 X 射线测试；仅作读出器件相邻先例。")],
            ),
        ],
        "opportunity_specs": [
            opportunity("玻璃微通道闪烁屏的分层银化与成像效率闭环", "9/15 锚点显示全深度银层的 MTF 改善仍由模拟预测，实际制备与光损失还未充分闭环。", "验证“分辨率—效率—均匀性”的折中，能把一个结构方案变成可复用成像器件结论。", "制备多种银层深度样品；同一 X 射线谱下测 MTF、DQE/绝对光输出、串扰、空间均匀性和长期辐照响应。", "确定最佳银化深度及其工艺容差，报告模拟与实测偏差。", ["10.1088/1748-0221/21/09/p09024"], "不得把模拟预测写成实验结果；需避免与结构化 CsI 屏/MCP 成像器件直接作不等价性能横比。", "探测器结构与成像"),
            opportunity("混合阳离子单晶异质结的偏压漂移与阵列级成像复核", "高灵敏度和迁移抑制已有单晶生长/器件先例，日报异质结需要证明界面带来的独立收益。", "同片对照加长时/阵列测量，可把材料器件指标推进到稳定成像证据。", "同批 CsPbBr3 单晶制备异质结与对照器件；统一偏压、剂量和温度，测试迟滞、暗电流、基线漂移、成像信噪比和器件离散性。", "定量分离异质结界面贡献，并给出从单器件到像素阵列的性能保持率。", ["10.1021/acsami.6c14882"], "同领域论文竞争强；单器件高灵敏度数值若无同条件控制、批次统计和阵列图像，创新性不足。", "材料器件与 X 射线成像"),
            opportunity("STIX 在轨自标定的参考像素假设与系统误差独立检验", "栅格透射自标定依赖参考像素照明/通量假设，且新的传输值会改变光子谱归一化。", "独立参考观测和误差传播有助于判断在轨校准改进能否推广到不同耀斑/能区。", "按耀斑照明几何、参考像素选择及子准直器分组重算；与独立观测/近太阳地球对齐事件交叉验证并传播到光子谱。", "给出标定结果对参考像素、能区和观测几何的敏感度以及系统误差界限。", ["10.1007/s11207-026-02739-6"], "该主题日新且主文已提出方法；后续需有独立数据/观测交叉验证，不能只重复原论文拟合。", "空间仪器校准与数据分析"),
            opportunity("固定靶 γ-粒子符合系统的时序、效率和温漂联合标定", "日报一篇给出符合选道，另一篇给出塑闪-SiPM 原型；需要从单一条件演示走向可重复的系统性能。", "对核反应道识别，时间窗、能量阈值和通道温漂共同决定峰背比与有效效率。", "用已知反应/标准时间源测通道时间偏差、时间游走、符合效率、死时间、峰背比和温度漂移，并对不同靶/束流做复测。", "提供可迁移的固定靶符合测量性能预算和校准流程。", ["10.15625/0868-3166/24399", "10.1051/epjconf/202638603007"], "9/15 日报日期按报告记录；其中越南 Communications in Physics 页面目前显示在线日期为 9/16，数据库/时区日期有一天偏差，需以正式卷期元数据核定。", "核物理仪器与符合谱学"),
        ],
        "overall_judgment": "9/15 的论文分属闪烁屏、直接型钙钛矿探测、空间仪器校准和核物理符合读出。最直接的实验机会是把玻璃微通道屏的模拟预测做成量化的 MTF—效率闭环；异质结方向要证明界面独立贡献；其余两条更适合按各自仪器任务做独立校准研究，不能拼成一个统一性能结论。",
        "limitations": [
            "本条为 2026-09-17 执行的历史回溯查新；检索锚点严格使用 9/15 日报中的 6 篇论文。出版社公开日期与日报日界线可能相差一天：Communications in Physics 当前页面显示该篇 γ-粒子符合论文于 9/16 上线，故网站日报归属与出版社在线日期应分别理解。",
            "候选/核实计数仅统计页面列出的代表性论文；窗口以近五年为主，部分 MCP/SiPM 仪器基线略早；不是穷尽式系统综述。",
            "MCP X 射线成像器件与玻璃微通道闪烁屏、STIX 空间校准与固定靶符合仪器结构不同；引用用于界定相邻方法和先例，不表示可直接横向比较。",
            "判断以出版社/期刊题录及摘要为主；对高灵敏度、检出限和长期稳定性需回到全文核对偏压、剂量定义、厚度、样品统计和完整测试条件。",
        ],
    },
}


def apply_backfill(report_date: str, spec: dict[str, Any]) -> None:
    path = ROOT / "data" / "reports" / f"{report_date}.json"
    with path.open("r", encoding="utf-8") as handle:
        report = json.load(handle)
    if report.get("date") != report_date:
        raise ValueError(f"date mismatch in {path}")
    articles = report.get("articles")
    if not isinstance(articles, list) or len(articles) != spec["anchor_article_count"]:
        raise ValueError(f"expected {spec['anchor_article_count']} anchors for {report_date}")
    article_by_doi = {
        str(article.get("doi", "")).strip().lower(): article
        for article in articles
        if isinstance(article, dict) and article.get("doi")
    }

    related = {
        "status": "evidence_reviewed",
        "review_type": "historical_backfill",
        "reviewed_at": RETRIEVED_AT,
        "searched_at": RETRIEVED_AT,
        "search_window": SEARCH_WINDOW,
        "search_scope": spec["search_scope"],
        "anchor_article_count": spec["anchor_article_count"],
        "candidate_count": len(spec["related_works"]),
        "verified_count": len(spec["related_works"]),
        "searched_sources": SOURCES,
        "limitations": spec["limitations"],
        "themes": spec["themes"],
    }

    opportunity_items: list[dict[str, Any]] = []
    for item in spec["opportunity_specs"]:
        evidence = []
        opportunity_data = {key: value for key, value in item.items() if key != "daily_evidence_dois"}
        for doi in item["daily_evidence_dois"]:
            source = article_by_doi.get(doi.lower())
            if source is None:
                raise ValueError(f"daily evidence DOI {doi} not found in {report_date}")
            evidence.append({
                "title": source.get("title", ""),
                "year": str(source.get("publication_date", ""))[:4],
                "doi": source.get("doi", ""),
                "url": source.get("url", "") or f"https://doi.org/{doi}",
                "relation": "本期日报中的研究锚点",
            })
        opportunity_items.append({**opportunity_data, "evidence_papers": evidence})

    publication = {
        "status": "evidence_reviewed",
        "review_type": "historical_backfill",
        "reviewed_at": RETRIEVED_AT,
        "searched_at": RETRIEVED_AT,
        "anchor_article_count": spec["anchor_article_count"],
        "overall_judgment": spec["overall_judgment"],
        "opportunities": opportunity_items,
    }

    # Fail closed: every opportunity must cite only papers in this day's report.
    for item in opportunity_items:
        evidence_dois = {paper["doi"].lower() for paper in item["evidence_papers"]}
        if not evidence_dois or not evidence_dois.issubset(article_by_doi):
            raise ValueError(f"opportunity evidence is not anchored to {report_date}")

    report["schema_version"] = 2
    report["related_work_review"] = related
    report["publication_opportunities"] = publication
    atomic_json_write(path, report)
    with path.open("r", encoding="utf-8") as handle:
        written = json.load(handle)
    safe_related = public_related_work_review(written.get("related_work_review"))
    safe_publication = public_publication_opportunities(written.get("publication_opportunities"))
    surfaced_count = sum(len(item["representative_works"]) for item in safe_related["themes"])
    if safe_related.get("review_type") != "historical_backfill" or surfaced_count != len(spec["related_works"]):
        raise ValueError(f"public related-work payload failed validation for {report_date}")
    if safe_publication.get("review_type") != "historical_backfill" or len(safe_publication.get("opportunities", [])) != len(opportunity_items):
        raise ValueError(f"public opportunity payload failed validation for {report_date}")
    print(f"{report_date}: {len(articles)} daily anchors, {len(related['themes'])} themes, {len(spec['related_works'])} checked related papers, {len(opportunity_items)} publication directions")


def main() -> None:
    for report_date, spec in REVIEWS.items():
        apply_backfill(report_date, spec)
    index_path = ROOT / "data" / "index.json"
    with index_path.open("r", encoding="utf-8") as handle:
        index = json.load(handle)
    index["updated_at"] = datetime.now(timezone.utc).isoformat()
    atomic_json_write(index_path, index)


if __name__ == "__main__":
    main()
