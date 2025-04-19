from datetime import datetime, timedelta
from typing import Optional, Callable, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import Session
from enum import Enum
import functools
import asyncio
from ..db.models import CircuitBreakerState
from ..core.config import get_settings

settings = get_settings()

class CircuitState(str, Enum):
    CLOSED = "closed"  # Normal operation, requests allowed
    OPEN = "open"      # Circuit is open, requests are not allowed
    HALF_OPEN = "half_open"  # Testing if the service is back online

class CircuitBreaker:
    def __init__(self, provider_name: str, db: AsyncSession, 
                 failure_threshold: int = 5, 
                 recovery_timeout: int = 60):
        self.provider_name = provider_name
        self.db = db
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout  # seconds
    
    async def _get_or_create_state(self) -> CircuitBreakerState:
        stmt = select(CircuitBreakerState).where(
            CircuitBreakerState.provider_name == self.provider_name
        )
        result = await self.db.execute(stmt)
        state = result.scalars().first()
        
        if not state:
            state = CircuitBreakerState(
                provider_name=self.provider_name,
                failure_count=0,
                state=CircuitState.CLOSED
            )
            self.db.add(state)
            await self.db.commit()
            await self.db.refresh(state)
        
        return state
    
    async def _update_state(self, state: CircuitBreakerState):
        await self.db.commit()
        await self.db.refresh(state)
    
    async def _record_failure(self, state: CircuitBreakerState):
        state.failure_count += 1
        state.last_failure_time = datetime.utcnow()
        
        # Open the circuit if failures exceed threshold
        if state.failure_count >= self.failure_threshold and state.state != CircuitState.OPEN:
            state.state = CircuitState.OPEN
            state.last_state_change = datetime.utcnow()
        
        await self._update_state(state)
    
    async def _record_success(self, state: CircuitBreakerState):
        if state.state == CircuitState.HALF_OPEN:
            # If success in half-open state, close the circuit
            state.state = CircuitState.CLOSED
            state.failure_count = 0
            state.last_state_change = datetime.utcnow()
            await self._update_state(state)
    
    async def is_open(self) -> bool:
        state = await self._get_or_create_state()
        
        # If circuit is open but recovery timeout has elapsed, 
        # transition to half-open
        if state.state == CircuitState.OPEN:
            timeout_threshold = datetime.utcnow() - timedelta(seconds=self.recovery_timeout)
            if state.last_state_change and state.last_state_change < timeout_threshold:
                state.state = CircuitState.HALF_OPEN
                state.last_state_change = datetime.utcnow()
                await self._update_state(state)
        
        return state.state == CircuitState.OPEN
    
    async def record_failure(self):
        state = await self._get_or_create_state()
        await self._record_failure(state)
    
    async def record_success(self):
        state = await self._get_or_create_state()
        await self._record_success(state)

# Circuit breaker decorator
def circuit_breaker(method):
    @functools.wraps(method)
    async def wrapper(self, *args, **kwargs):
        # Check if the circuit is open
        is_open = await self.circuit_breaker.is_open()
        if is_open:
            raise Exception(f"Circuit is open for provider {self.provider_name}")
        
        try:
            result = await method(self, *args, **kwargs)
            await self.circuit_breaker.record_success()
            return result
        except Exception as e:
            await self.circuit_breaker.record_failure()
            raise e
            
    return wrapper 