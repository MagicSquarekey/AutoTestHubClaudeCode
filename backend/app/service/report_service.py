# -*- coding: utf-8 -*-
"""
报告生成服务 / Report generation service
@Function: 提供测试报告的生成、查询、导出功能 / Provide report generation, query, export
"""

import json
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.exec_record import ExecRecord
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger("report")


class ReportService:
    """报告服务类"""

    def __init__(self, db: Session):
        self.db = db

    def get_report_list(self, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """@Function: 获取报告列表

        Args:
            page: 页码
            page_size: 每页数量

        Returns:
            报告列表
        """
        query = self.db.query(ExecRecord).filter(ExecRecord.status == "completed")
        total = query.count()
        records = query.order_by(ExecRecord.exec_time.desc()).offset((page - 1) * page_size).limit(page_size).all()

        return {
            "list": [record.to_dict() for record in records],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def get_report_detail(self, task_id: str) -> Optional[Dict[str, Any]]:
        """@Function: 获取报告详情

        Args:
            task_id: 任务ID

        Returns:
            报告详情
        """
        record = self.db.query(ExecRecord).filter(ExecRecord.task_id == task_id).first()
        if not record:
            return None

        return record.to_dict()

    def generate_html_report(self, task_id: str) -> Optional[str]:
        """@Function: 生成HTML报告

        Args:
            task_id: 任务ID

        Returns:
            报告文件路径
        """
        record = self.db.query(ExecRecord).filter(ExecRecord.task_id == task_id).first()
        if not record:
            return None

        # 生成HTML报告
        report_dir = Path(settings.REPORT_DIR)
        report_dir.mkdir(parents=True, exist_ok=True)

        report_path = report_dir / f"report_{task_id}.html"

        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>测试报告 - {task_id}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .summary {{ background: #f5f5f5; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
        .passed {{ color: #52c41a; }}
        .failed {{ color: #ff4d4f; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background: #fafafa; }}
    </style>
</head>
<body>
    <h1>测试报告</h1>
    <div class="summary">
        <h2>执行概览</h2>
        <p>任务ID: {task_id}</p>
        <p>执行时间: {record.exec_time.strftime('%Y-%m-%d %H:%M:%S') if record.exec_time else 'N/A'}</p>
        <p>用例总数: {record.case_count}</p>
        <p class="passed">通过: {record.pass_count}</p>
        <p class="failed">失败: {record.fail_count}</p>
        <p>通过率: {record.pass_rate}%</p>
        <p>执行耗时: {record.exec_duration}秒</p>
    </div>
</body>
</html>"""

        report_path.write_text(html_content, encoding="utf-8")

        # 更新报告路径
        record.report_path = str(report_path)
        self.db.commit()

        logger.info(f"生成HTML报告: {report_path}")
        return str(report_path)

    def get_step_details(self, task_id: str, case_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """@Function: 获取步骤详情

        Args:
            task_id: 任务ID
            case_id: 用例ID

        Returns:
            步骤详情列表
        """
        # TODO: 从执行引擎获取步骤详情
        return []

    def get_failure_analysis(self, task_id: str) -> Dict[str, Any]:
        """@Function: 获取失败分析

        Args:
            task_id: 任务ID

        Returns:
            失败分析结果
        """
        # TODO: 实现失败分类分析
        return {
            "total_failures": 0,
            "categories": {
                "business_defect": 0,
                "element_failure": 0,
                "environment_issue": 0,
                "case_error": 0,
            },
            "details": [],
        }

    def get_statistics_overview(self) -> Dict[str, Any]:
        """@Function: 获取统计概览

        Returns:
            统计数据
        """
        # 总执行次数
        total_executions = self.db.query(ExecRecord).count()

        # 最近执行
        recent_executions = self.db.query(ExecRecord).order_by(ExecRecord.exec_time.desc()).limit(10).all()

        # 平均通过率
        avg_pass_rate = self.db.query(func.avg(ExecRecord.pass_rate)).scalar() or 0

        # 总用例数
        total_cases = self.db.query(func.sum(ExecRecord.case_count)).scalar() or 0

        return {
            "total_executions": total_executions,
            "total_cases": total_cases,
            "avg_pass_rate": round(float(avg_pass_rate), 2),
            "recent_executions": [r.to_dict() for r in recent_executions],
        }

    def get_statistics_trend(self, days: int = 30) -> Dict[str, Any]:
        """@Function: 获取趋势数据

        Args:
            days: 天数

        Returns:
            趋势数据
        """
        start_date = datetime.now() - timedelta(days=days)

        records = (
            self.db.query(ExecRecord)
            .filter(ExecRecord.exec_time >= start_date)
            .order_by(ExecRecord.exec_time)
            .all()
        )

        # 按日期分组
        trend_data = {}
        for record in records:
            date_str = record.exec_time.strftime("%Y-%m-%d") if record.exec_time else "unknown"
            if date_str not in trend_data:
                trend_data[date_str] = {
                    "date": date_str,
                    "execution_count": 0,
                    "total_cases": 0,
                    "total_passed": 0,
                    "total_failed": 0,
                }
            trend_data[date_str]["execution_count"] += 1
            trend_data[date_str]["total_cases"] += record.case_count
            trend_data[date_str]["total_passed"] += record.pass_count
            trend_data[date_str]["total_failed"] += record.fail_count

        # 计算每日通过率
        for date_str, data in trend_data.items():
            if data["total_cases"] > 0:
                data["pass_rate"] = round(data["total_passed"] / data["total_cases"] * 100, 2)
            else:
                data["pass_rate"] = 0

        return {
            "days": days,
            "trend": list(trend_data.values()),
        }


    def get_case_distribution(self) -> Dict[str, Any]:
        """@Function: 获取用例平台分布

        Returns:
            用例按平台的分布数据
        """
        from app.models.test_case import TestCase

        distribution = (
            self.db.query(TestCase.platform, func.count(TestCase.id))
            .filter(TestCase.status == 1)
            .group_by(TestCase.platform)
            .all()
        )

        platform_names = {
            "web": "Web端",
            "android": "Android端",
            "ios": "iOS端",
            "miniapp": "小程序",
        }

        return {
            "distribution": [
                {"name": platform_names.get(row[0], row[0]), "value": row[1]}
                for row in distribution
            ],
        }

    def export_defect(self, task_id: str, case_id: Optional[int] = None) -> Dict[str, Any]:
        """@Function: 导出缺陷详情

        Args:
            task_id: 任务ID
            case_id: 用例ID

        Returns:
            缺陷详情
        """
        record = self.db.query(ExecRecord).filter(ExecRecord.task_id == task_id).first()
        if not record:
            return {}

        # TODO: 从执行引擎获取失败详情
        return {
            "task_id": task_id,
            "exec_time": record.exec_time.strftime("%Y-%m-%d %H:%M:%S") if record.exec_time else None,
            "platform": record.platform,
            "device_info": record.device_info,
            "failure_details": [],
        }

    def replay_failed_case(self, task_id: str, case_id: int) -> str:
        """@Function: 复现失败用例

        Args:
            task_id: 原任务ID
            case_id: 用例ID

        Returns:
            新任务ID
        """
        from app.service.exec_service import ExecService

        exec_service = ExecService(self.db)
        new_task_id = exec_service.create_task({
            "case_ids": [case_id],
            "platform": "web",
        })

        logger.info(f"创建复现任务: {new_task_id}")
        return new_task_id

