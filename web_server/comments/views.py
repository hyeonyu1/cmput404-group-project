from django.http import JsonResponse
from comments.models import Comment
from social_distribution.utils.endpoint_utils import Endpoint, Handler


def delete_single_comment(request, comment_id):
    def delete_handler(request):
        output = {
            "query": "deleteComment"
        }
        try:
            Comment.objects.filter(id=comment_id).delete()
        except Exception as e:
            output['message'] = "Unable to delete comment"
            output['error'] = str(e)
            return JsonResponse(output)
        output['message'] = "Comment deleted"
        return JsonResponse(output)

    return Endpoint(request, None, [
            Handler("DELETE", "application/json", delete_handler)
            ]).resolve()

