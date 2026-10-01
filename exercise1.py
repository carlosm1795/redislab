import redis

SOURCE_HOST = "redis-12000.re-cluster1.ps-redislabs.org" 
SOURCE_PORT = 12000                  

REPLICA_HOST = "redis-16250.re-cluster1.ps-redislabs.org" 
REPLICA_PORT = 16250                

def main():
    # 1. Connect to source-db
    print("Connecting to source-db...")
    source_client = redis.Redis(host=SOURCE_HOST, port=SOURCE_PORT, decode_responses=True)

    # Optional: Clear existing keys first to start fresh
    source_client.flushdb()


    print("Inserting 100 individual keys into source-db...")
    for i in range(1, 101):
        source_client.set(i, i)

    # 3. Confirm 100 keys exist in source-db
    key_count = source_client.dbsize()
    print(f"\n[+] Total key count in source-db: {key_count}")

    if key_count == 100:
        print("    Confirmation SUCCESSFUL: Exactly 100 keys exist in source-db!")
    else:
        print(f"    Warning: Found {key_count} keys instead of 100.")

    # 4. Connect to replica-db and read/print in reverse order
    print("\nConnecting to replica-db...")
    replica_client = redis.Redis(host=REPLICA_HOST, port=REPLICA_PORT, decode_responses=True)

    print("\nPrinting 100 keys in reverse order from replica-db:")
    for i in range(100, 0, -1):
        value = replica_client.get(f"number_{i}")
        print(f"{i}: {value}")

if __name__ == "__main__":
    main()