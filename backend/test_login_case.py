# -*- coding: utf-8 -*-
"""
测试登录用例执行
@Function: 直接执行登录用例，验证用例步骤是否正确
"""

import asyncio
import json
import sqlite3
import sys
import os
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.driver.web_driver import WebDriver
from plugins.keywords.web_keywords import execute_keyword


async def get_test_case(case_id: int):
    """从数据库获取测试用例"""
    conn = sqlite3.connect('data/autotest.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, case_name, steps FROM test_case WHERE id = ?', (case_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return {
            'id': result[0],
            'case_name': result[1],
            'steps': json.loads(result[2]) if result[2] else []
        }
    return None


async def execute_test_case(case_id: int):
    """执行测试用例"""
    # 获取用例
    case = await get_test_case(case_id)
    if not case:
        print(f"错误：找不到用例 ID={case_id}")
        return

    print(f"\n{'='*60}")
    print(f"执行用例: {case['case_name']}")
    print(f"步骤数: {len(case['steps'])}")
    print(f"{'='*60}\n")

    # 初始化 WebDriver
    driver = WebDriver(headless=False)
    try:
        await driver.launch()

        # 执行每个步骤
        results = []
        for i, step in enumerate(case['steps'], 1):
            print(f"\n步骤 {i}/{len(case['steps'])}: {step.get('name', step['keyword'])}")
            print(f"  关键字: {step['keyword']}")
            print(f"  参数: {json.dumps(step.get('params', {}), ensure_ascii=False)}")

            # 跳过禁用的步骤
            if step.get('disabled', False):
                print(f"  状态: 已跳过(禁用)")
                results.append({
                    'step': i,
                    'keyword': step['keyword'],
                    'success': True,
                    'message': '已跳过',
                    'duration': 0
                })
                continue

            # 执行步骤
            start_time = datetime.now()
            try:
                result = await execute_keyword(
                    driver,
                    step['keyword'],
                    step.get('params', {}),
                    timeout=step.get('timeout', 30) * 1000
                )
                duration = (datetime.now() - start_time).total_seconds()

                if result['success']:
                    print(f"  状态: 成功 [OK]")
                    print(f"  耗时: {duration:.2f}秒")
                    if result.get('data'):
                        print(f"  返回值: {result['data']}")
                else:
                    print(f"  状态: 失败 [FAIL]")
                    print(f"  错误: {result['message']}")

                results.append({
                    'step': i,
                    'keyword': step['keyword'],
                    'success': result['success'],
                    'message': result['message'],
                    'duration': duration
                })

                # 如果失败且策略是停止，则终止
                if not result['success'] and step.get('on_error') == 'stop':
                    print(f"\n错误：步骤 {i} 失败，终止执行")
                    break

            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                print(f"  状态: 异常 [ERROR]")
                print(f"  错误: {str(e)}")
                results.append({
                    'step': i,
                    'keyword': step['keyword'],
                    'success': False,
                    'message': str(e),
                    'duration': duration
                })

                if step.get('on_error') == 'stop':
                    print(f"\n错误：步骤 {i} 异常，终止执行")
                    break

        # 打印执行摘要
        print(f"\n{'='*60}")
        print("执行摘要")
        print(f"{'='*60}")
        total = len(results)
        success = sum(1 for r in results if r['success'])
        failed = total - success
        total_time = sum(r['duration'] for r in results)

        print(f"总步骤数: {total}")
        print(f"成功: {success}")
        print(f"失败: {failed}")
        print(f"总耗时: {total_time:.2f}秒")
        print(f"通过率: {success/total*100:.1f}%")

        if failed > 0:
            print(f"\n失败步骤:")
            for r in results:
                if not r['success']:
                    print(f"  步骤 {r['step']} ({r['keyword']}): {r['message']}")

        return results

    finally:
        await driver.close()


async def main():
    """主函数"""
    print("开始执行登录用例测试...")
    results = await execute_test_case(1)

    if results:
        # 保存结果到文件
        report = {
            'case_id': 1,
            'execute_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'results': results
        }

        report_file = f"data/reports/test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs(os.path.dirname(report_file), exist_ok=True)
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n测试报告已保存: {report_file}")


if __name__ == '__main__':
    asyncio.run(main())
