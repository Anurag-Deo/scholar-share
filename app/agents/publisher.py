from app.agents.base_agent import BaseAgent


class PublisherAgent(BaseAgent):
    def __init__(self):
        super().__init__("Publisher", model_type="light")
