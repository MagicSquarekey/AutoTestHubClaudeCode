# -*- coding: utf-8 -*-
"""
元素管理服务 / Element management service
@Function: 提供测试元素的业务逻辑处理 / Provide business logic for test elements
"""

import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.test_element import TestElement
from app.utils.logger import get_logger

logger = get_logger("element_service")


class ElementService:
    """元素管理服务类"""

    def __init__(self, db: Session):
        self.db = db

    def get_element_list(
        self,
        module: Optional[str] = None,
        page_name: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        """@Function: 获取元素列表

        Args:
            module: 模块筛选
            page_name: 页面筛选
            keyword: 关键词搜索
            page: 页码
            page_size: 每页数量

        Returns:
            包含列表和分页信息的字典
        """
        query = self.db.query(TestElement)

        if module:
            query = query.filter(TestElement.module == module)
        if page_name:
            query = query.filter(TestElement.page_name == page_name)
        if keyword:
            query = query.filter(
                or_(
                    TestElement.elem_name.contains(keyword),
                    TestElement.page_name.contains(keyword),
                )
            )

        total = query.count()
        elements = query.order_by(TestElement.update_time.desc()).offset((page - 1) * page_size).limit(page_size).all()

        return {
            "list": [elem.to_dict() for elem in elements],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def get_element_by_id(self, elem_id: int) -> Optional[Dict[str, Any]]:
        """@Function: 根据ID获取元素

        Args:
            elem_id: 元素ID

        Returns:
            元素字典或None
        """
        element = self.db.query(TestElement).filter(TestElement.id == elem_id).first()
        return element.to_dict() if element else None

    def create_element(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """@Function: 创建元素

        Args:
            data: 元素数据

        Returns:
            创建的元素字典
        """
        # 处理定位符
        if isinstance(data.get("locators"), list):
            data["locators"] = json.dumps(data["locators"], ensure_ascii=False)

        element = TestElement(**data)
        self.db.add(element)
        self.db.commit()
        self.db.refresh(element)

        logger.info(f"创建元素成功: {element.elem_name}")
        return element.to_dict()

    def update_element(self, elem_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """@Function: 更新元素

        Args:
            elem_id: 元素ID
            data: 更新数据

        Returns:
            更新后的元素字典或None
        """
        element = self.db.query(TestElement).filter(TestElement.id == elem_id).first()
        if not element:
            return None

        # 处理定位符
        if isinstance(data.get("locators"), list):
            data["locators"] = json.dumps(data["locators"], ensure_ascii=False)

        for key, value in data.items():
            if hasattr(element, key):
                setattr(element, key, value)

        element.update_time = datetime.now()
        self.db.commit()
        self.db.refresh(element)

        logger.info(f"更新元素成功: {element.elem_name}")
        return element.to_dict()

    def delete_element(self, elem_id: int) -> bool:
        """@Function: 删除元素

        Args:
            elem_id: 元素ID

        Returns:
            是否删除成功
        """
        element = self.db.query(TestElement).filter(TestElement.id == elem_id).first()
        if not element:
            return False

        self.db.delete(element)
        self.db.commit()

        logger.info(f"删除元素成功: {element.elem_name}")
        return True

    def batch_delete_elements(self, elem_ids: List[int]) -> int:
        """@Function: 批量删除元素

        Args:
            elem_ids: 元素ID列表

        Returns:
            删除的数量
        """
        count = self.db.query(TestElement).filter(TestElement.id.in_(elem_ids)).delete()
        self.db.commit()

        logger.info(f"批量删除元素成功: {count}个")
        return count

    def health_check(self, elem_ids: Optional[List[int]] = None, platform: str = "web") -> Dict[str, Any]:
        """@Function: 执行元素健康巡检

        Args:
            elem_ids: 元素ID列表，None表示检查所有
            platform: 平台类型

        Returns:
            巡检结果
        """
        query = self.db.query(TestElement)
        if elem_ids:
            query = query.filter(TestElement.id.in_(elem_ids))

        elements = query.all()

        total = len(elements)
        healthy = 0
        unhealthy = 0
        details = []

        for elem in elements:
            # 计算健康度
            total_count = elem.success_count + elem.fail_count
            health_rate = (elem.success_count / total_count * 100) if total_count > 0 else 100

            is_healthy = health_rate >= 80  # 80%以上视为健康
            if is_healthy:
                healthy += 1
            else:
                unhealthy += 1

            details.append({
                "id": elem.id,
                "elem_name": elem.elem_name,
                "health_rate": round(health_rate, 2),
                "is_healthy": is_healthy,
                "success_count": elem.success_count,
                "fail_count": elem.fail_count,
            })

        return {
            "total": total,
            "healthy": healthy,
            "unhealthy": unhealthy,
            "health_rate": round(healthy / total * 100, 2) if total > 0 else 100,
            "details": details,
        }

    def get_page_list(self) -> List[str]:
        """@Function: 获取所有页面列表

        Returns:
            页面名称列表
        """
        pages = self.db.query(TestElement.page_name).distinct().all()
        return [p[0] for p in pages if p[0]]

    def get_module_list(self) -> List[str]:
        """@Function: 获取元素模块列表

        Returns:
            模块名称列表
        """
        modules = self.db.query(TestElement.module).distinct().all()
        return [m[0] for m in modules if m[0]]

    def export_elements(self, elem_ids: List[int]) -> Dict[str, Any]:
        """@Function: 导出元素

        Args:
            elem_ids: 元素ID列表

        Returns:
            导出的元素数据
        """
        elements = self.db.query(TestElement).filter(TestElement.id.in_(elem_ids)).all()

        return {
            "version": "1.0",
            "export_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "count": len(elements),
            "elements": [elem.to_dict() for elem in elements],
        }

    def import_elements(self, elements_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """@Function: 批量导入元素

        Args:
            elements_data: 元素数据列表

        Returns:
            导入结果
        """
        imported_count = 0
        for elem_data in elements_data:
            # 处理定位符
            if isinstance(elem_data.get("locators"), list):
                elem_data["locators"] = json.dumps(elem_data["locators"], ensure_ascii=False)

            # 移除ID
            elem_data.pop("id", None)
            elem_data.pop("create_time", None)
            elem_data.pop("update_time", None)

            element = TestElement(**elem_data)
            self.db.add(element)
            imported_count += 1

        self.db.commit()

        logger.info(f"导入元素成功: {imported_count}个")
        return {"imported_count": imported_count}

    def batch_sync(self, page_name: str, platform: str = "web", device_id: Optional[str] = None) -> Dict[str, Any]:
        """@Function: 从页面批量抓取并同步元素

        Args:
            page_name: 页面名称
            platform: 平台类型
            device_id: 设备ID

        Returns:
            同步结果
        """
        # TODO: 实际实现需要调用驱动抓取页面元素
        # 这里返回模拟结果
        logger.info(f"批量同步元素: {page_name}, 平台: {platform}")

        return {
            "page_name": page_name,
            "platform": platform,
            "new_count": 0,
            "updated_count": 0,
            "unchanged_count": 0,
            "details": [],
        }
