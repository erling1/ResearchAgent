
#fastpi
from fastapi import Depends, FastAPI, WebSocket, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

#needed packages
from contextlib import asynccontextmanager
from typing import AsyncGenerator   # <-- missing import
import logging 
import os 
import dataclasses
from openai import AsyncOpenAI
from azure.cosmos import CosmosClient, exceptions
from azure.cosmos.container import ContainerProxy
import asyncio
import time  # <-- should be grouped here, not repeated later

#own classes 
from HomeMadeClasses.ai_manager import AiManager
from HomeMadeClasses.web_search import WebSearch





OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
COSMOS_URI = os.getenv("COSMOS_URI") 
COSMOS_KEY = os.getenv("COSMOS_KEY")
WEB_SEARCH_API_KEY = os.getenv("WEB_SEARCH_API_KEY")

ai_manager: AiManager
openai_client: AsyncOpenAI
azure_cosmos_db_client: CosmosClient
web_search_client: WebSearch
container: ContainerProxy


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    global ai_manager
    global openai_client
    global azure_cosmos_db_client
    global web_search_client
    global container

    
    openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    ai_manager = AiManager(openai_client=openai_client)
    azure_cosmos_db_client = CosmosClient(COSMOS_URI, 
                                          credential=COSMOS_KEY
                                          )
    database = azure_cosmos_db_client.get_database_client("database1")
    

    container = database.get_container_client("container1")

    web_search_client = WebSearch(api_key=WEB_SEARCH_API_KEY)


app = FastAPI()

security = HTTPBearer()

logging.basicConfig(level=logging.INFO)

app.mount("/frontpage/pages", StaticFiles(directory="frontpage/pages"),name="pages")

@app.middleware("http")
async def add_process_header(request: Request, call_next):
    
    try:

        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        logging.info(f"Request process time: {process_time}")
    except:

        logging.info(f"Exception occured in middleware connection check: {Exception}")
    
    return response


@dataclasses.dataclass
class User:
    email: str 


class HTTPAuthorizer:
    
    def __init__(self, allow_static_keys: bool = False):
        self.allow_static_keys = allow_static_keys
        self._static_key = "research agent"
        


    async def __call__(self, request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):

        try:

            if os.getenv("DEV_MODE") == "true":
                return User("devmode@mail.com")

            
            oauth_user = await self._authenticate_oauth(request)
            if oauth_user:
                return User(email=oauth_user)

            if not credentials:
                raise Exception("No auth provided")

            user_email = await self._authenticate_header(credentials)

            return User(email=user_email)


        except Exception as e:
            raise HTTPException(status_code=401,detail=str(e))
            

    async def _authenticate_oauth_proxy(self, request):

        headers = request.headers
        
        try:
            user_email = headers["X-Auth-Request-Email"]
            return user_email

        except:
            logging.info(f"No oauth in header")
            return None

    
    async def _authenticate_header(self, header: HTTPAuthorizationCredentials):

        try:

            if header.scheme != "Bearer":
                raise Exception("Should be Bearer Scheme")

            if (token := header.credentials).startswith(self._static_key):
                username, password = tuple(token[len(self._static_key):].split(" "))


            expected_password = os.getenv(f"STATIC_KEY_{username.upper()}")
            if not expected_password:
                raise Exception("Static Key not set")

            if expected_password != password:
                raise Exception(f"Static key does not match expected static key")

            return username

        except:
            logging.info(f"Authentication failed")
        

            


@app.get("/api/pythonnews")
async def get_latest_pythonnews_endpoint(user: User = Depends(HTTPAuthorizer)):

    python_news_queries = [
    "site:python.org python 3.13 3.14 release features updates 2024 2025",
    "site:peps.python.org PEP accepted implemented 2024 2025",
    "site:blog.python.org python updates news announcements",
    
    # Python experts and thought leaders
    "Raymond Hettinger python tips insights 2024 2025",
    "Brett Cannon python core developer updates 2024 2025",
    "Tim Peters python zen updates insights 2024 2025",
    "David Beazley python performance concurrency 2024 2025",
    
    # Community and discussion platforms
    "site:realpython.com python latest features tutorials 2024 2025",
    "site:news.ycombinator.com python language updates 2024 2025",
    "site:lobste.rs python programming language news 2024",
    
    # Technical publications and blogs
    "python weekly newsletter latest edition 2024 2025",
    "python insider blog updates core development 2024 2025",
    
    # Performance and cool features
    "python async asyncio new features updates 2024 2025",
    "python packaging uv updates 2024 2025",
    "python pattern matching structural pattern matching examples",
    
    # Conference talks and presentations
    "PyCon 2024 2025 python keynote talks important updates",
    "EuroPython 2024 python conference highlights news",
    "Python language summit 2024 2025 discussions decisions"
]

    
    tasks = [web_search_client.search_web(query) for query in python_news_queries]

    search_results = await asyncio.gather(*tasks)

    with open("pythonnews_prompt.txt", "r") as file:
            python_prompt = file.read()

    results_text = "\n\n".join(
        f"- {r.get('title')}\n  {r.get('link')}\n  {r.get('snippet')}"
        for r in search_results
    )

    
    
    full_prompt = f"{python_prompt}\n\nHere are the search results:\n\n{results_text}"

    #returns just the text format 
    response = ai_manager.gen_openai_response(full_prompt)

    return response


@app.get("/api/githubtrending")
async def get_githubtrending_endpoint(user: User = Depends(HTTPAuthorizer)):
    pass



