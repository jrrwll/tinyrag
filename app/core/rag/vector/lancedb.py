


"""

all-MiniLM-L6-v2
all-MiniLM-L12-v2
nomic-embed-text-v1
multilingual-e5-small



knowledge 知识库



POST http://localhost:3001/api/workspace/new
{"name":"tuke","onboardingComplete":true}

POST http://localhost:3000/api/v1/users/user/settings/update
{"ui":{"version":"0.6.18","models":["qwen3:4b"]}}



uv add sentence-transformers

"""
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

# huggingface-cli download sentence-transformers/all-MiniLM-L6-v2 --local-dir ./all-MiniLM-L6-v2
model = SentenceTransformer('/path/to/all-MiniLM-L6-v2')

embeddings = model.encode("sentences")
