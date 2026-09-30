import sys
import redis

from redisvl.extensions.router import Route, SemanticRouter
from redisvl.utils.vectorize import HFTextVectorizer


# ============================================================
# Redis Configuration
# ============================================================

REDIS_HOST = "redis-11377.re-cluster1.ps-redislabs.org"
REDIS_PORT = 11377

# Challenge allows unauthenticated data access
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"

ROUTER_NAME = "technical-challenge-router"


# ============================================================
# Route Definitions
# ============================================================

def create_routes():
    """
    Define the three semantic routes required by the challenge.
    """

    genai_route = Route(
        name="GenAI programming topics",
        references=[
            "How do I use LangChain to build an LLM agent?",
            "Write a Python script using RedisVL for vector search.",
            "How to perform retrieval-augmented generation with OpenAI API?",
            "Prompt engineering strategies for code generation",
            "Fine-tuning open-source LLMs like Llama on code datasets",
            "How can I create embeddings in Python?",
            "How does semantic caching work?",
            "How can Redis be used as a vector database?",
            "How do I build a chatbot using an LLM?",
            "How does vector similarity search work?"
        ],
        distance_threshold=0.70
    )

    scifi_route = Route(
        name="Science fiction entertainment",
        references=[
            "What are the best science fiction movies?",
            "Who directed Dune and Blade Runner 2049?",
            "Tell me about Star Trek and Doctor Who.",
            "Recommendations for cyberpunk and space opera books",
            "Latest science fiction video games",
            "What is the plot of Star Wars?",
            "Who wrote the book Neuromancer?",
            "Recommend science fiction novels",
            "What happens in The Matrix?",
            "Tell me about futuristic science fiction movies"
        ],
        distance_threshold=0.70
    )

    classical_route = Route(
        name="Classical music",
        references=[
            "Who composed Symphony No. 9 in D minor?",
            "What is the difference between a concerto and a sonata?",
            "Tell me about Beethoven, Mozart, Bach, and Tchaikovsky.",
            "Best recordings of Chopin's piano nocturnes",
            "Famous opera performances and classical orchestras",
            "Recommend violin concertos by Vivaldi",
            "What are Mozart's most famous compositions?",
            "Tell me about Beethoven's symphonies",
            "Recommend classical piano music",
            "Who are famous Baroque composers?"
        ],
        distance_threshold=0.70
    )

    return [
        genai_route,
        scifi_route,
        classical_route
    ]


# ============================================================
# Redis Connection Test
# ============================================================

def test_redis_connection():
    """
    Verify connectivity and the Redis features needed by RedisVL.
    """

    print("\n[+] Testing Redis connection...")

    try:
        client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True
        )

        response = client.ping()

        if response:
            print("[+] Redis connection successful.")

        print(f"    Host: {REDIS_HOST}")
        print(f"    Port: {REDIS_PORT}")

        # Check Search availability
        try:
            client.execute_command("FT._LIST")
            print("[+] Search and Query: Available")
        except redis.exceptions.ResponseError as error:
            print("[-] Search and Query does not appear to be available.")
            print(f"    {error}")
            return False

        # Check JSON availability because RedisVL may use JSON
        try:
            test_key = "semantic-router:json-test"

            client.execute_command(
                "JSON.SET",
                test_key,
                "$",
                '{"test":true}'
            )

            client.delete(test_key)

            print("[+] JSON: Available")

        except redis.exceptions.ResponseError as error:
            print("[-] JSON commands are not available.")
            print(f"    {error}")
            print()
            print(
                "RedisVL requires capabilities that are not enabled "
                "on this database."
            )
            return False

        return True

    except Exception as error:
        print("[-] Unable to connect to Redis.")
        print(f"    {error}")
        return False


# ============================================================
# Semantic Router Setup
# ============================================================

def setup_router():
    """
    Create the RedisVL SemanticRouter and index route references.
    """

    print("\n[+] Initializing Semantic Router...")
    print("[+] Generating embeddings for route references...")

    routes = create_routes()

    try:
        vectorizer = HFTextVectorizer()

        router = SemanticRouter(
            name=ROUTER_NAME,
            vectorizer=vectorizer,
            routes=routes,
            redis_url=REDIS_URL,
            overwrite=True
        )

        print("[+] Semantic Router initialized successfully.")

        return router

    except Exception as error:
        print("\n[-] Failed to initialize Semantic Router.")
        print(f"    {type(error).__name__}: {error}")

        return None


# ============================================================
# Routing
# ============================================================

def route_query(router, query):
    """
    Send a query to the SemanticRouter and print the best route.
    """

    try:
        match = router(query)

        if match and match.name:
            print()
            print("-----------------------------------------------")
            print(f"Query          : {query}")
            print(f"Selected Route : {match.name}")
            print("-----------------------------------------------")

            return match.name

        print()
        print("-----------------------------------------------")
        print(f"Query          : {query}")
        print("Selected Route : No matching route found")
        print("-----------------------------------------------")

        return None

    except Exception as error:
        print(f"\n[-] Error routing query: {error}")
        return None


# ============================================================
# Interactive Query
# ============================================================

def interactive_query(router):
    """
    Allow the user to enter a query manually.
    """

    print("\n===============================================")
    print("             Semantic Routing")
    print("===============================================")

    query = input("\nEnter your query: ").strip()

    if not query:
        print("[-] Query cannot be empty.")
        return

    route_query(router, query)


# ============================================================
# Predefined Tests
# ============================================================

def run_test_queries(router):
    """
    Run predefined queries against the SemanticRouter.
    """

    test_queries = [
        "How can I set up semantic caching for an LLM application in Python?",
        "What is the plot of Star Wars and The Matrix?",
        "Can you recommend some violin concertos composed by Vivaldi?",
        "How do I use vector embeddings for similarity search in Redis?",
        "Who wrote the book Neuromancer?",
        "What are Mozart's most famous compositions?"
    ]

    print("\n===============================================")
    print("        Semantic Router Evaluation")
    print("===============================================")

    for query in test_queries:
        route_query(router, query)


# ============================================================
# Batch Query Mode
# ============================================================

def batch_queries(router):
    """
    Allow multiple queries without returning to the main menu.
    """

    print("\n===============================================")
    print("              Batch Query Mode")
    print("===============================================")

    print("Enter queries one at a time.")
    print("Type 'exit' to return to the main menu.")

    while True:

        query = input("\nQuery: ").strip()

        if query.lower() == "exit":
            break

        if not query:
            continue

        route_query(router, query)


# ============================================================
# Display Routes
# ============================================================

def display_routes():
    """
    Display configured semantic routes and their references.
    """

    routes = create_routes()

    print("\n===============================================")
    print("             Configured Routes")
    print("===============================================")

    for route in routes:

        print(f"\nRoute: {route.name}")
        print(f"Distance Threshold: {route.distance_threshold}")
        print("References:")

        for index, reference in enumerate(
            route.references,
            start=1
        ):
            print(f"  {index}. {reference}")


# ============================================================
# About
# ============================================================

def display_about():
    """
    Explain what the application demonstrates.
    """

    print("""
================================================
        RedisVL Semantic Router Demo
================================================

This application demonstrates semantic routing using
RedisVL and Redis Search and Query.

The application defines three semantic routes:

1. GenAI programming topics
2. Science fiction entertainment
3. Classical music

Each route contains reference sentences.

RedisVL converts these references into vector embeddings
using a Hugging Face text embedding model.

When a query is submitted:

    User Query
        |
        v
    HFTextVectorizer
        |
        v
    Vector Embedding
        |
        v
    Redis Vector Search
        |
        v
    SemanticRouter
        |
        v
    Best Matching Route

The output required by the challenge is the name of the
selected route.
================================================
""")


# ============================================================
# Main Menu
# ============================================================

def display_menu():

    print("""
================================================
       RedisVL Semantic Routing Challenge
================================================

1. Send a query
2. Run predefined test queries
3. Batch query mode
4. Display configured routes
5. Test Redis connection
6. About semantic routing
7. Exit

================================================
""")


# ============================================================
# Main
# ============================================================

def main():

    print("""
================================================
        RedisVL Semantic Router
================================================
""")

    # Test Redis before creating the router
    if not test_redis_connection():

        print("""
[-] Redis validation failed.

Verify that the database was created with:

    - Single shard
    - Single region
    - Search and Query enabled
    - Required RedisVL capabilities

The Semantic Router cannot be initialized until the
required Redis features are available.
""")

        sys.exit(1)

    # Initialize once
    router = setup_router()

    if router is None:
        sys.exit(1)

    while True:

        display_menu()

        choice = input("Select an option (1-7): ").strip()

        if choice == "1":
            interactive_query(router)

        elif choice == "2":
            run_test_queries(router)

        elif choice == "3":
            batch_queries(router)

        elif choice == "4":
            display_routes()

        elif choice == "5":
            test_redis_connection()

        elif choice == "6":
            display_about()

        elif choice == "7":
            print("\nExiting Semantic Router.")
            break

        else:
            print("\n[-] Invalid option. Select a number from 1 to 7.")


if __name__ == "__main__":
    main()