from rest_framework.renderers import JSONRenderer

class CustomJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        status_code = renderer_context['response'].status_code
        response = {
            'status': True,
            'message': 'Success',
            'data': data,
            'error_number': 0
        }

        if not str(status_code).startswith('2'):
            response['status'] = False
            response['data'] = None
            response['error_number'] = status_code
            
            # Handle standard DRF error format {'detail': '...'} or validation errors
            if isinstance(data, dict):
                if 'detail' in data:
                    response['message'] = data['detail']
                else:
                    response['message'] = 'Validation Error'
                    response['data'] = data # Return field errors in data
            elif isinstance(data, list):
                response['message'] = 'Validation Error'
                response['data'] = data
            else:
                 response['message'] = str(data)

        return super().render(response, accepted_media_type, renderer_context)
