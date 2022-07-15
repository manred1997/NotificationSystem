import functools
from typing import Callable, Any, Text, Tuple

from utils.constants import (
    HOST_LOCATE,
    TIME_ZONE,
    TIME_OUT,
    GEOGRAPHY,
    PROXIES,
    RETRIES,
    BACKOFF_FACTOR,
    REQUEST_ARGS
)
from service import TrendReq



def agent_must_be_ready(f: Callable[..., Any]) -> Callable[..., Any]:
    """Any Agent method decorated with this will raise if the agent is not ready."""

    @functools.wraps(f)
    def decorated(self, *args: Any, **kwargs: Any) -> Any:
        if not self.is_ready():
            raise Exception(
                "Agent needs to be prepared before usage. You need to set a "
                "processor and a tracker store."
            )
        return f(self, *args, **kwargs)

    return decorated


class Agent(object):
    def __init__(self,
        hl=HOST_LOCATE,
        tz=TIME_ZONE,
        geo=GEOGRAPHY,
        timeout=TIME_OUT,
        proxies=PROXIES,
        retries=RETRIES,
        backoff_factor=BACKOFF_FACTOR,
        requests_args=REQUEST_ARGS,
    ) -> None:
        
        self.pytrend = TrendReq(
            hl=hl,
            tz=tz,
            geo=geo,
            timeout=timeout,
            proxies=proxies,
            retries=retries,
            backoff_factor=backoff_factor,
            requests_args=requests_args
        )
    @classmethod
    def load_agent(cls,
                    hl: Text,
                    tz: int,
                    geo: Text,
                    timeout: Tuple,
                    proxies: Text,
                    retries: int,
                    backoff_factor: int,
                    requests_args=None
        ):
        agent = Agent(
            hl=hl,
            tz=tz,
            geo=geo,
            timeout=timeout,
            proxies=proxies,
            retries=retries,
            backoff_factor=backoff_factor,
            requests_args=requests_args,
        )
        return agent
    
    def is_ready(self) -> bool:
        """Check if all necessary components are instantiated to use agent."""
        return self.pytrend

    @agent_must_be_ready
    async def realtime_trending_searches(self):
        retrieval_result = self.pytrend.realtime_trending_searches()
        return retrieval_result
