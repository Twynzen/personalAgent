"""REST API endpoints"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import psutil

from sendell.agent.memory import get_memory
from sendell.agent.prompts import get_system_prompt
from sendell.vscode import VSCodeMonitor

router = APIRouter()


# Models
class Fact(BaseModel):
    fact: str
    category: str = "general"


class PromptUpdate(BaseModel):
    prompt: str


# ==================== FACTS ====================

@router.get("/facts")
async def get_facts():
    """Get all facts from memory"""
    memory = get_memory()
    return {"facts": memory.get_facts()}


@router.post("/facts")
async def add_fact(fact: Fact):
    """Add a new fact"""
    memory = get_memory()
    memory.add_fact(fact.fact, fact.category)
    return {"success": True, "fact": fact}


@router.delete("/facts/{index}")
async def delete_fact(index: int):
    """Delete a fact by index"""
    memory = get_memory()
    memory.remove_fact(index)
    return {"success": True}


# ==================== PROMPTS ====================

@router.get("/prompts")
async def get_prompt():
    """Get current system prompt"""
    return {"prompt": get_system_prompt()}


@router.post("/prompts")
async def update_prompt(data: PromptUpdate):
    """Update system prompt (TODO: implement save)"""
    # TODO: Save to prompts.py
    return {"success": True, "prompt": data.prompt}


# ==================== TOOLS ====================

@router.get("/tools")
async def get_tools():
    """Get list of available tools"""
    from sendell.agent.core import get_agent

    try:
        agent = get_agent()
        tools_info = []

        for tool in agent.tools:
            tools_info.append({
                "name": tool.name if hasattr(tool, 'name') else str(tool),
                "description": tool.description if hasattr(tool, 'description') else "No description"
            })

        return {"tools": tools_info}
    except Exception as e:
        return {"tools": []}


# ==================== PROJECTS (snapshot) ====================

@router.get("/projects")
async def get_projects():
    """Get current VS Code projects (snapshot)"""
    monitor = VSCodeMonitor()
    instances = monitor.find_vscode_instances()

    projects = []
    for inst in instances:
        projects.append({
            "pid": inst.pid,
            "name": inst.name,
            "workspace_name": inst.workspace.workspace_name,
            "workspace_path": inst.workspace.workspace_path,
            "workspace_type": inst.workspace.workspace_type,
        })

    return {"projects": projects}


# ==================== METRICS (snapshot) ====================

@router.get("/metrics")
async def get_metrics():
    """Get system metrics (snapshot)"""
    return {
        "cpu": psutil.cpu_percent(interval=0),
        "ram": psutil.virtual_memory().percent,
        "terminals": len(VSCodeMonitor().find_vscode_instances())
    }
