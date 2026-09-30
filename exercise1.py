import redis


SOURCE_HOST = "redis-12000.re-cluster1.ps-redislabs.org" 
SOURCE_PORT = 12000                  

REPLICA_HOST = "redis-16250.re-cluster1.ps-redislabs.org" 
REPLICA_PORT = 16250                

KEY_NAME = "numbers_list"

def main():
    # 1. Connect to source-db and insert values 1 to 100
    print("Connecting to source-db...")
    source_client = redis.Redis(host=SOURCE_HOST, port=SOURCE_PORT, decode_responses=True)

    # Clean up key if it already exists from a previous run
    source_client.delete(KEY_NAME)

    # Push values 1 to 100 onto a Redis List (RPUSH preserves 1..100 order)
    values = [str(i) for i in range(1, 101)]
    source_client.rpush(KEY_NAME, *values)
    print(f"Successfully inserted values 1-100 into '{KEY_NAME}' on source-db.")

    # 2. Connect to replica-db and read values in reverse order
    print("\nConnecting to replica-db...")
    replica_client = redis.Redis(host=REPLICA_HOST, port=REPLICA_PORT, decode_responses=True)

    # Read the list in reverse using LRANGE with negative indices, or fetching all and reversing
    # LRANGE with indices 0 to -1 fetches all items in inserted order [1..100]
    items = replica_client.lrange(KEY_NAME, 0, -1)

    print("\nPrinting values in reverse order (100 down to 1) from replica-db:")
    for value in reversed(items):
        print(value)

if __name__ == "__main__":
    main()