import json

class JSONMiddleware:
    '''Serialize request body and attach to request object'''

    def __init__(self, api_caller):
        self.call_api = api_caller


    def __call__(self, request, *args, **kwargs):
        if request.body:
            try:
                request.json = json.loads(request.body)
            except Exception as e:
                # Continue if body is not json serializable
                pass
        
        return self.call_api(request, *args, **kwargs)
