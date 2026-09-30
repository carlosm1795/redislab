import os
from redisvl.extensions.router import Route, SemanticRouter
from redisvl.utils.vectorize import HFTextVectorizer


REDIS_HOST = "redis-13512.re-cluster1.ps-redislabs.org" 
REDIS_PORT = 13512         
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"

def setup_router():

    genai_route = Route(
        name="GenAI programming topics",
        references=[
            "How do I use LangChain to build an LLM agent?",
            "Write a Python script using RedisVL for vector search.",
            "How to perform retrieval-augmented generation (RAG) with OpenAI API?",
            "Prompt engineering strategies for code generation",
            "Fine-tuning open-source LLMs like Llama on code datasets"
        ],
        distance_threshold=0.70
    )

   
    scifi_route = Route(
        name="Science fiction entertainment",
        references=[
            "What are the best sci-fi movies on Netflix right now?",
            "Who directed the movie Dune and Blade Runner 2049?",
            "Tell me about classic science fiction TV shows like Star Trek or Doctor Who.",
            "Recommendations for cyberpunk and space opera books",
            "Latest news about upcoming sci-fi video games"
        ],
        distance_threshold=0.70
    )

  
    classical_route = Route(
        name="Classical music",
        references=[
            "Who composed Symphony No. 9 in D minor?",
            "What is the difference between a concerto and a sonata?",
            "Listen to Beethoven, Mozart, Bach, and Tchaikovsky compositions",
            "Best recordings of Chopin's piano nocturnes",
            "Famous opera performances and classical orchestra venues"
        ],
        distance_threshold=0.70
    )

    # -----------------------------------------------------------------------
    # 3. Initialize the SemanticRouter
    # -----------------------------------------------------------------------
    print("[+] Initializing Semantic Router and indexing reference embeddings...")
    router = SemanticRouter(
        name="technical-challenge-router",
        vectorizer=HFTextVectorizer(),  # Uses default HuggingFace model (all-MiniLM-L6-v2)
        routes=[genai_route, scifi_route, classical_route],
        redis_url=REDIS_URL,
        overwrite=True  # Overwrites existing router index if rerun
    )
    return router

def main():
    # Setup and load routes into Redis Vector Index
    router = setup_router()
    print("[+] Router initialized successfully!\n")

    # -----------------------------------------------------------------------
    # 4. Test Queries & Send Requests to Best Route
    # -----------------------------------------------------------------------
    test_queries = [
        "How can I set up semantic caching for an LLM application in Python?",
        "What is the plot of Star Wars and Matrix?",
        "Can you recommend some violin concertos composed by Vivaldi?",
        "How to use vector embeddings for similarity search in Redis?",
        "Who wrote the book Neuromancer?"
    ]

    print("==================================================")
    print("           Semantic Router Evaluation             ")
    print("==================================================")

    for query in test_queries:
        # Route query to the best match
        match = router(query)
        
        # Display output showing the name of the route
        route_name = match.name if match and match.name else "No matching route found"
        print(f"Query: \"{query}\"")
        print(f"--> Selected Route: {route_name}\n")

if __name__ == "__main__":
    main()