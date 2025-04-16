#pip3 install pymongo
#pip3 install openai

import os
import openai
from pymongo import MongoClient

# Initialize OpenAI and MongoDB clients
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
mongodb_client = MongoClient(os.getenv("MONGODB_URI"))

# === Generate Embedding ===
# This function takes a string (the game's description or our query) and generates the embedding vector.
# We use OpenAI's text embedding, but you can replace it with other embedding model.
def generate_embedding(text):
    try:
        response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print("Error generating embedding:", e)
        raise

# === Search games in the MongoDB collection ===
# Search function using MongoDB Atlas Vector Search. We limit to the three most relevant results
def search_games(query, limit=3):

    try:
        print("Connected to MongoDB")
        db = mongodb_client["gameDatabase"]
        collection = db["games"]

        print(f"Generating embedding for query: \"{query}\"")
        query_embedding = generate_embedding(query)

        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_index",
                    "queryVector": query_embedding,
                    "path": "embedding",
                    "numCandidates": 100,
                    "limit": limit
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "title": 1,
                    "description": 1,
                    "publishers": 1,
                    "developers": 1,
                    "consoles": 1,
                    "releaseDate": 1,
                    "image": 1,
                    "score": { "$meta": "vectorSearchScore" }
                }
            }
        ]

        results = list(collection.aggregate(pipeline))
        return results

    except Exception as e:
        print("Error searching games:", e)
        raise

    finally:
        mongodb_client.close()
        print("MongoDB connection closed")

# === Use our LLM to generate a response ===
# Given the user query and the games we found, we use the LLM to provide a useful response
def generate_response(query, search_results):
    if not search_results:
        return "I couldn't find any games matching your criteria in our database."

    # Format the search results into readable blocks
    game_details = "\n---\n".join([
        f"""Title: {game.get('title')}
        Description: {game.get('description', '')[:200]}...
        Developers: {', '.join(game.get('developers', [])) if isinstance(game.get('developers'), list) else game.get('developers')}
        Publishers: {', '.join(game.get('publishers', [])) if isinstance(game.get('publishers'), list) else game.get('publishers')}
        Platforms: {', '.join(game.get('consoles', [])) if isinstance(game.get('consoles'), list) else game.get('consoles')}
        Release Date: {game.get('releaseDate')}
        """ for game in search_results
    ])

    # This is the prompt. The request we send to the LLM. Here you can craft how you want it to respond, act, and think.
    # For example, if the context was more serious, we could ask the LLM to be more formal.
    prompt =    f"""
                A user asked: "{query}"
                Based on this query, I found the following games in my database:
                {game_details}
                Please provide a helpful recommendation response that addresses the user's query. Highlight why these games match what they're looking for, focusing on relevant aspects such as genre, setting, gameplay elements, etc. Keep your response conversational and engaging.
                """

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                { "role": "system", "content": "You are a helpful AI assistant that specializes in video game recommendations." },
                { "role": "user", "content": prompt }
            ]
        )
        return response.choices[0].message.content

    except Exception as e:
        print("Error generating GPT response:", e)
        fallback_titles = ", ".join([g.get("title") for g in search_results])
        return f'Based on your query "{query}", I found these games that might interest you: {fallback_titles}'

# === Entry point for our chat ===
# Try modifying the user_query to get other recommended games
if __name__ == "__main__":
    user_query = "recommend a game that is a shooter in space"
    games_found = search_games(user_query)
    llm_response = generate_response(user_query, games_found)
    print(llm_response)