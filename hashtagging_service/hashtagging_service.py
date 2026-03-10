import grpc
from concurrent import futures
import os

from google import genai

import hashtagging_pb2
import hashtagging_pb2_grpc

# Configure Gemini
client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
MODEL = "gemini-2.0-flash"

def generate_hashtag(post_content):
    try:

        PROMPT = f'''You will be given some content of a social media post, and you must generate some hashtags for that post based on the given data. you must only output the hashtags as a string {post_content} '''
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=PROMPT,
        )
        if response.text is None:
            return "#bskypost"
        return response.text.strip()
    except Exception:
        return "#bskypost"
    

class HashtagServiceServicer(hashtagging_pb2_grpc.HashtagServiceServicer):
    def GetHashtag(self, request, context):
        hashtag = generate_hashtag(request.post_content)
        return hashtagging_pb2.HashtagResponse(hashtag=hashtag)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    hashtagging_pb2_grpc.add_HashtagServiceServicer_to_server(
        HashtagServiceServicer(), server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
