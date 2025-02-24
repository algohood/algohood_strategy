import importlib.util
import os
from algoAgent.models import *
from algoUtils.consoleUtil import ConsoleOutput
from langgraph.graph import StateGraph, MessagesState, START, END, add_messages
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, AnyMessage
from langgraph.types import Command
from typing import Annotated, Dict, Optional

def update_plan(_origin: Dict[str, str], _new: Dict[str, str]):
    _origin.update(_new)
    return _origin

class TeamState(MessagesState):
    coder_messages: Annotated[list[AnyMessage], add_messages]
    draft: Annotated[Dict[str, str], update_plan]
    plan_name: Optional[str]
    plan_content: Optional[str]
    code_content: Optional[str]

class IdeaTeam:
    @staticmethod
    def load_prompt(_file_name: str):
        spec = importlib.util.find_spec('algoStrategy')
        package_path = spec.submodule_search_locations[0].replace('\\', '/').replace('Strategy', 'Agent')
        file_path = os.path.join(package_path, 'algoPrompts/{}.md'.format(_file_name))
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件{file_path}不存在")
        
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    
    @classmethod
    def planner(cls, _context: TeamState):
        adj_messages = []
        for msg in _context["messages"]:
            if msg.name == "planner":
                adj_messages.append(msg)
            else:
                adj_messages.append(HumanMessage(content=msg.content, name="user"))

        messages = [
            SystemMessage(content=cls.load_prompt("monoSignalPlanner")),
            *adj_messages
        ]  
        content_str = ConsoleOutput.console_for_stream("planner", silicon_deepseek_r1.stream(messages))
        draft = ConsoleOutput.extract_markdown_files(content_str)

        if draft:
            return {"draft": draft, "messages": AIMessage(content=content_str, name="planner")}
        else:
            return {"messages": AIMessage(content=content_str, name="planner")}
    
    @classmethod
    def checker(cls, _context: TeamState):
        if not _context["draft"]:
            print("draft is empty")
            return Command(goto="plan_feedback")
        
        messages = [
            SystemMessage(content=cls.load_prompt("algoChecker")),
            HumanMessage(content=_context["messages"][-1].content, name="user")
        ]
        content_str = ConsoleOutput.console_for_stream("checker", silicon_deepseek_v3.stream(messages))
        return {"messages": HumanMessage(content=content_str, name="user")}
    
    @classmethod
    def coder(cls, _context: TeamState):
        if not _context["plan_name"]:
            print("plan is empty")
            return Command(goto="plan_feedback")
        
        messages = [
            SystemMessage(content=cls.load_prompt("signalCoder")),
            HumanMessage(content=_context["plan_content"], name="user"),
            *_context["coder_messages"]
        ]
        content_str = ConsoleOutput.console_for_stream("coder", silicon_deepseek_v3.stream(messages))
        python_scripts = ConsoleOutput.extract_python_scripts(content_str)
        if python_scripts:
            return {"code_content": python_scripts, "coder_messages": AIMessage(content=content_str, name="coder")}
        else:
            print("python scripts is empty", end="\n")
    
    @staticmethod
    def plan_feedback(_context: TeamState):
        invoke_str = "'check' for auditing plan, 'save' for saving plan, otherwise input your feedback of the plan: \n"
        msg = ConsoleOutput.console_for_input("user", invoke_str)
        if msg.content == "check":
            goto = "checker"
            update = None

        elif msg.content == "save":
            goto = "save_plan"
            update = None

        else:
            goto = "planner"
            update = {"messages": msg} if msg.content else None

        return Command(
            update=update,
            goto=goto
        )
    
    @staticmethod
    def coder_feedback(_context: TeamState):
        invoke_str = "'save' for saving code, otherwise input your feedback of the python script: \n"
        msg = ConsoleOutput.console_for_input("user", invoke_str)
        if msg.content == "save":
            goto = "save_code"
            update = None
        else:
            goto = "coder"
            update = {"coder_messages": msg} if msg.content else None

        return Command(
            update=update,
            goto=goto
        )
    
    @staticmethod
    def save_plan(_context: TeamState):
        spec = importlib.util.find_spec('algoStrategy')
        package_path = spec.submodule_search_locations[0].replace('\\', '/').replace('Strategy', 'Docs')
        folder_path = os.path.join(package_path, 'algoSignals')
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        file_names = list(_context["draft"].keys())
        file_name = input(f"请选择要保存的文件名: {file_names} \n")
        if file_name not in file_names:
            print(f"文件{file_name}不存在")
            return Command(goto="save_plan")
        
        content = _context["draft"][file_name]
        file_name = file_name.split("_")[0]
        with open(os.path.join(folder_path, file_name + ".md"), "w", encoding="utf-8") as f:
            f.write(content)
            print(f"文件{file_name}已保存")

        return {"plan_name": file_name, "plan_content": content}

    @staticmethod
    def save_code(_context: TeamState):
        spec = importlib.util.find_spec('algoStrategy')
        package_path = spec.submodule_search_locations[0].replace('\\', '/')
        folder_path = os.path.join(package_path, 'algoSignals')
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        if not _context.get('code_content'):
            print("code is empty")
            return Command(goto="coder_feedback")

        file_name = _context['plan_name'] + ".py"
        content = _context['code_content']
        with open(os.path.join(folder_path, file_name), "w", encoding="utf-8") as f:
            f.write(content)
            print(f"文件{file_name}已保存")

    @classmethod
    def start_process(cls):
        # create graph
        graph = StateGraph(TeamState)
        
        # add nodes
        graph.add_node("planner", cls.planner)
        graph.add_node("checker", cls.checker)
        graph.add_node("plan_feedback", cls.plan_feedback)
        graph.add_node("save_plan", cls.save_plan)

        graph.add_node("coder", cls.coder)
        graph.add_node("coder_feedback", cls.coder_feedback)
        graph.add_node("save_code", cls.save_code)

        # add edges
        graph.add_edge(START, "planner")
        graph.add_edge("planner", "plan_feedback")
        graph.add_edge("checker", "plan_feedback")

        graph.add_edge("save_plan", 'coder')
        graph.add_edge('coder', 'coder_feedback')
        graph.add_edge('save_code', END)

        workerflow = graph.compile()
        workerflow.invoke({"messages": HumanMessage(content="来几个信号", name="user")})


if __name__ == "__main__":
    IdeaTeam.start_process()
