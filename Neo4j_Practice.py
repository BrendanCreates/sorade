import dotenv
import os
from neo4j import GraphDatabase

# After creating an Aura instance @ Neo4j this file is donloaded that has the connection info to the database as env variables
load_status = dotenv.load_dotenv("Neo4j-3d14dd11-Created-2026-01-11.txt")
if load_status is False:
    raise RuntimeError('Environment variables not loaded.')
 
# Neo4j Secrets
URI = os.getenv("NEO4J_URI")
AUTH = (os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
DB_NAME = os.getenv("NEO4J_DATABASE")

# Create Driver object to access database, this does not actually establish a connection
# Don't need a driver.close() call because the with statement auto closes the connection after the indentation
with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
    print("Connection established.")

    # Basic node deletion query example
    """
    # in MATCH (p:Person) the parenthesis represent a Node, the p is the variable name we give to the node, Person is label
    # the {name: $name} part is  afilter which tells the database to only find Person nodes with name property matching a value
    # the dollar sign represents a parameter which pass in later
    # DELETE p tells the database to remove the node named p, DETACH auto cuts all connections first since node cannot be deleted if its still has lines branching out
    # driver.execute_query returns a summary object and it contains counters which gives a log of changes (creations, deletions, etc)
    records, summary, keys = driver.execute_query(
        \"\"\" 
        MATCH (p:Person {name: $name})
        DETACH DELETE p
        \"\\",
        name = "Alice",    
        database_ = DB_NAME,                                 
    )
    print("\nFirst counter:")
    print(f"Query counters: {summary.counters}.")
    """

    # Deleting multiple nodes with one query
    delete_names = ["Alice", "David"]

    records, summary, keys = driver.execute_query(
        """
        MATCH (p:Person)
        WHERE p.name IN $names
        DETACH DELETE p
        """,
        names = delete_names,
        database_ = DB_NAME,
    )
    print("\nSecond counter:")
    print(f"Query counters: {summary.counters}.")


    # Create two nodes and a relationship between them using the Cypher clause CREATE
    # Cypher query
    # MERGE is better than CREATE because CREATE always makes a new node even if identical exists
    # Since the nodes already exists the code prints that 0 nodes were created
    summary = driver.execute_query(""" 
        MERGE (a:Person {name: $name})
        MERGE (b:Person {name: $friendName})
        MERGE (a)-[:KNOWS]->(b)                     
        """,
        name="Alice", friendName="David", # Query parameters as keyword arguments
        database_=DB_NAME, # Database to run the query on
    ).summary
    print("Created {nodes_created} nodes in {time} ms.".format(
        nodes_created=summary.counters.nodes_created,
        time=summary.result_available_after
    ))

    # Reading from the database
    
    records, summary, keys = driver.execute_query(
        """
        MATCH (p:Person)-[:KNOWS]->(:Person)
        RETURN p.name AS name
        """,
        database_ = DB_NAME,
    )

    # Loop through results
    for record in records:
        print(record.data()) # get record as a dict
    
    # Summary information
    print("The query '{query}' returned {records_count} records in {time} ms.".format(
        query = summary.query, records_count = len(records), time = summary.result_available_after
    ))



