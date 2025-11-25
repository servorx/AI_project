from qdrant_client import QdrantClient

qdrant_client = QdrantClient(
    url="https://23be0c2c-b716-47b6-8757-42c2c431183e.us-east-1-1.aws.cloud.qdrant.io:6333", 
    api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.jNd6MbM8RThYBWfCeL7mlLPOk4J-01Pp-oMbA_UqsNA",
)

print(qdrant_client.get_collections())