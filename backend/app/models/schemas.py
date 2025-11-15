from pydantic import BaseModel
from typing import List, Tuple


class CarBase(BaseModel):
    id: str
    start_node: str
    end_node: str
    current_pos: Tuple[int, int]


class PlanRequest(BaseModel):
    cars: List[CarBase]


class Path(BaseModel):
    car_id: str
    path: List[Tuple[int, int]]
    status: str


class PlanResponse(BaseModel):
    plan_id: str
    paths: List[Path]
