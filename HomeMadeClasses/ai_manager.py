
from openai import AsyncOpenAI



class AiManager:
    _openai_client: AsyncOpenAI

    def __init__(self, openai_client):

        self._openai_client = openai_client
        

    async def gen_openai_respons(self,input):


        response = await self._openai_client.responses.create(model="gpt-5",
                                           tools=[{"type": "web_search"}],
                                           input=input)


        sources = ['fake news']
        #for item in response.output:
        #    for content in item.content:
        #        if content.type == "tool_result" and content.tool_type == "web_search":
        #            sources.extend(content.output.get("results", []))

        #text = response.text

        return {"text": response.output_text, "sources": sources}

