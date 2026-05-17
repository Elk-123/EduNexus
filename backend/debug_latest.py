#!/usr/bin/env python3
import asyncio
import os
import sys

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import AsyncSessionLocal
from app.api.deps import get_current_user
from app.models.student import Student
from app.models.factory import GenerationTask
from sqlalchemy.future import select
from app.core.security import create_access_token
from app.core.config import settings

async def debug_latest_endpoint():
    """调试 /latest 端点"""
    # 创建测试用户 token
    user_id = "fa3b273d-84d5-4f3f-a0d6-4626b914f38d"
    token = create_access_token(user_id)
    print(f"Token: {token}")

    # 测试用户认证
    async with AsyncSessionLocal() as db:
        # 获取用户
        user_result = await db.execute(select(Student).where(Student.id == user_id))
        user = user_result.scalars().first()
        print(f"User found: {user is not None}")

        if user:
            # 查看所有任务
            task_result = await db.execute(
                select(GenerationTask).where(
                    GenerationTask.student_id == user.id
                ).order_by(GenerationTask.created_at.desc())
            )
            tasks = task_result.scalars().all()
            print(f"User has {len(tasks)} tasks")

            for task in tasks:
                print(f"  Task ID: {task.id}, Status: {task.status}, Topic: {task.topic}")

            # 尝试获取最新任务
            if tasks:
                latest_task = tasks[0]
                print(f"\nLatest task details:")
                print(f"  ID: {latest_task.id}")
                print(f"  Topic: {latest_task.topic}")
                print(f"  Status: {latest_task.status}")
                print(f"  Agents status: {latest_task.agents_status}")
                print(f"  Created at: {latest_task.created_at}")

                # 构建响应
                from app.schemas.factory import TaskStatusResponse
                response = TaskStatusResponse(
                    id=latest_task.id,
                    topic=latest_task.topic,
                    status=latest_task.status,
                    agents_status=latest_task.agents_status or {},
                    created_at=latest_task.created_at
                )
                print(f"\nResponse: {response}")
                print(f"Response dict: {response.model_dump()}")

if __name__ == "__main__":
    asyncio.run(debug_latest_endpoint())