// src/views/LearningPath/types.ts

export interface LearningResource {
    id: string;
    agentName: 'Director' | 'Professor' | 'Hacker' | 'Examiner';
    type: 'video' | 'document' | 'code' | 'quiz';
    title: string;
    description: string;
    status: 'completed' | 'current' | 'locked';
  }
  
  export interface KnowledgeNode {
    id: string;
    label: string;
    x: number;
    y: number;
    type: 'standard' | 'injected'; // injected 表示 AI 动态插入的补全节点
    proficiency: number; // 0-1 掌握度
    status: 'completed' | 'active' | 'pending';
    resources: LearningResource[];
  }
  
  export interface KnowledgeEdge {
    from: string;
    to: string;
    isDynamic?: boolean; // 是否是 AI 规划生成的路径
  }