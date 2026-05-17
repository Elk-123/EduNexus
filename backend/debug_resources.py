#!/usr/bin/env python3
"""调试：检查后端返回的资源数据结构"""

import asyncio
import json
from uuid import uuid4
from app.core.database import AsyncSessionLocal
from app.models.factory import GenerationTask, GeneratedResource
from sqlalchemy.future import select

async def debug_resource_structure():
    """调试资源数据结构"""
    async with AsyncSessionLocal() as db:
        # 1. 查找最新的任务
        result = await db.execute(
            select(GenerationTask).order_by(GenerationTask.created_at.desc()).limit(1)
        )
        task = result.scalars().first()

        if not task:
            print("❌ 没有找到任务")
            return

        print(f"📋 任务ID: {task.id}")
        print(f"📋 主题: {task.topic}")
        print(f"📋 状态: {task.status}")
        print(f"📋 智能体状态: {task.agents_status}")

        # 2. 查找该任务的所有资源
        result = await db.execute(
            select(GeneratedResource).where(
                GeneratedResource.task_id == task.id
            ).order_by(GeneratedResource.agent_type)
        )
        resources = result.scalars().all()

        print(f"\n📦 找到 {len(resources)} 个资源:")

        for resource in resources:
            print(f"\n--- {resource.agent_type} ({resource.resource_type}) ---")
            print(f"ID: {resource.id}")
            print(f"状态: {resource.status}")
            print(f"内容预览 (前200字符):")
            content_str = json.dumps(resource.content, ensure_ascii=False, indent=2)
            print(content_str[:200] + "..." if len(content_str) > 200 else content_str)

            # 检查director资源的结构
            if resource.agent_type == "director":
                print("\n🎬 Director 资源详细结构:")
                if "scenes" in resource.content:
                    for i, scene in enumerate(resource.content["scenes"]):
                        print(f"  Scene {i+1}:")
                        print(f"    - scene_number: {scene.get('scene_number')}")
                        print(f"    - title: {scene.get('title')}")
                        print(f"    - visual: {scene.get('visual')[:50]}...")
                        print(f"    - voiceover: {scene.get('voiceover')[:50]}...")
                        print(f"    - duration_seconds: {scene.get('duration_seconds')}")
                else:
                    print("  ❌ 没有 scenes 字段")

if __name__ == "__main__":
    asyncio.run(debug_resource_structure())