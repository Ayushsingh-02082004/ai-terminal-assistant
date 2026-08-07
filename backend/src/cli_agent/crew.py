import os
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from cli_agent.tools import shell_tool, file_tool, code_tool, git_tool

@CrewBase
class CLIAgentCrew:
    """CLIAgentCrew crew containing the Router and Executor agents"""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def get_llm(self):
        """
        Determines and configures the LLM provider based on environment variables.
        Supports Ollama Cloud endpoints using CrewAI's LLM class.
        """
        from crewai import LLM
        
        api_key = os.getenv("OLLAMA_API_KEY")
        model_name = os.getenv("OLLAMA_MODEL_NAME", "gemma4:31b-cloud")
        base_url = os.getenv("OLLAMA_API_BASE") or "https://ollama.com/v1"

        if not api_key:
            return None

        # CrewAI LLM needs a provider prefix. If not present (e.g. gemma4:31b-cloud),
        # we prefix it with openai/ so it routes via the custom base_url using the OpenAI protocol
        if not ("/" in model_name):
            model_name = f"openai/{model_name}"
            
        return LLM(
            model=model_name,
            api_key=api_key,
            base_url=base_url
        )

    @agent
    def router_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['router_agent'],
            llm=self.get_llm(),
            verbose=True
        )

    @agent
    def executor_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['executor_agent'],
            tools=[shell_tool, file_tool, code_tool, git_tool],
            llm=self.get_llm(),
            verbose=True
        )

    @task
    def routing_task(self) -> Task:
        return Task(
            config=self.tasks_config['routing_task'],
            agent=self.router_agent()
        )

    @task
    def execution_task(self) -> Task:
        return Task(
            config=self.tasks_config['execution_task'],
            agent=self.executor_agent()
        )

    @crew
    def crew(self) -> Crew:
        """Creates the CLIAgentCrew crew"""
        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks,   # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True
        )
