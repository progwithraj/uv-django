from ninja import NinjaAPI
from .schemas import IndexSchema, IndexResponse

api = NinjaAPI(title="Core API", version="1.0.0")

@api.get("/index", tags=["Index"])
def index(request, val):
    return {"message":f"Hello Ninja API World {val}"}

@api.get("/index2", response=IndexResponse, tags=["Index"])
def index2(request, data: IndexSchema):
    return IndexResponse(message=f"Hello Ninja API World {data.val2}")

