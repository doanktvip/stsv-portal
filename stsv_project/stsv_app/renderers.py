from rest_framework.renderers import JSONRenderer


class UnifiedJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get("response") if renderer_context else None

        if response and response.status_code >= 400:
            return super().render(data, accepted_media_type, renderer_context)

        if isinstance(data, dict) and "status" in data and "data" in data:
            return super().render(data, accepted_media_type, renderer_context)

        message = "Thành công"
        if isinstance(data, dict) and "message" in data:
            message = data.pop("message")

        wrapped_data = {
            "status": "success",
            "message": message,
            "data": data,
        }

        return super().render(wrapped_data, accepted_media_type, renderer_context)
