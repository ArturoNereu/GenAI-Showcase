![](images/banner.png)

This is a step-by-step guide on how to create a very basic RAG Application using MongoDB, VoyageAI, and OpenAI.

## Introduction

What we are building in this tutorial, is a RAG system that can recommend games to the users, based on a natural language query and using a custom database of games (from Wikipedia).
While probably any LLM already knows about these games, let's assume our information about them comes from our own resources.

So, for example a user will ask something like:

'Recommend me a game that takes place in space. I like first person shooters.'

The RAG system will interpret the question, search for games that are related, and then format a response for the user:

'Based on the games I found, here are some games I think you're going to like: .....'


### How is this tutorial set up?

The main goal of this guide is that you build the notions on how RAG systems work, so we've prioritized clarity over following best practices.

This sample is divided in two scripts, but the real RAG takes place in `chat.py`. 

The `save_game_collection.py` is a helper script that prepopulates our MongoDB Atlas collection with data.

### Setup

Let's start by setting up our environment. We will be using three packages:

- MongoDB(pymongo): Make sure you get a connection string.
- VoyageAI: Create a free account and generate an API Key.
- OpenAI: Create a free account and generate an API Key.

To install the dependencies, in your terminal use:

```
> !pip install pymongo voyageai openai 
```

That's all you need to setup your environment.

In a real-life scenario, the first part of building a RAG application, is to get yout data. Usually, from PDFs, your database, images, and other resources. Then, you need to make sure you do some cleanup.
In our case, we asume we've done all this already, and we have all of our custom data in our MongoDB collection. 

Run the `save_game_collection.py` script:

```
> python3 save_game_collection.py
```

What we are doing here is dumping a previously generated collection into MongoDB Atlas. [gameDatabase.games.json]().

The structure of the collection is:

```json
{
  "_id": "ObjectId",
  "title": "string",
  "description": "string",
  "image": "string",
  "releaseDate": "string",
  "consoles": ["string"],
  "developers": ["string"],
  "publishers": ["string"],
  "embedding": ["number"]
}
```

The data was fetched from Wikipedia, and the embeddings were generated using VoyageAI, specifically using the `voyage-3` embedding model.

### The RAG

The setup is out of the way, now we can focus on our `chat.py` app.

To run it simply call:

```
> python app.py
```

After a few seconds, the system should give you a response, here's what mine gave me:

```
Sure, based on your interest in shooters set in space, I highly recommend "Halo: Combat Evolved". This classic game from Bungie is a definitive first-person shooter set in a detailed sci-fi world. The game places you in the role of Master Chief, a super-soldier fighting against the alien Covenant in varied space environments. The game has been praised for its engaging story, well-designed combat sequences, and asynchronous multiplayer. Plus, its huge impact on the genre makes it a must-play for space shooter fans.

Though "Fortnite" is a very popular shooter, it is not primarily set in space. However, it does often feature space-themed events and characters. This could add some cosmic flair to your gaming if you're interested. 

Lastly, "Shadow of the Colossus" is a spectacular game, but it doesn't match your request as it's neither a shooter nor set in space. It is a beautiful action-adventure game though, which might be worth exploring if you ever want to try a different genre.

Let me know if you need more information about these games or if you have other preferences!
```

Our RAG implementation is pretty simple, it has a main function with three parts:

#### The Query
```python
user_query = "recommend a game that is a shooter in space"
```
This is the query that the user is asking. As you notice, using natural language. We need to generate an embedding for this, to perform a vector search in our collection. 

This is not the prompt we are sending to the LLM, in fact, at this point we are not using the LLM at all.

#### The Vector Search
```python
games_found = search_games(user_query)
```
Here is where things get more interesting, we are going to perform the actual search. For our example, we want to "compare" how similar is the user's query to the games we have in our collection.

Each document (game) has information such as the developer, publisher, etc. But for our example, we just care about the description. Based on that, we will be able to recommend a game to our users.

The key concept here is the embedding, because that's how we are going to know how "related" are the user query and the games descriptions. 

The embedding we have in our documents, was generated over each game's description. So, now we need to generate an embedding on the user's query:

```python
def generate_embedding(text):
    try:
        result = voyageai_client.embed([text], model="voyage-3") 
        return result.embeddings[0]
    except Exception as e:
        print("Error generating embedding:", e)
        raise
```

This is the exact function, and model, used to generate the embeddings in our game's description. This is very important, as other models will generate different embeddings.

Once we have the embedding, we will use those values to perform a Vector Search in MongoDB Atlas. 

To be able to perform that search, in Atlas, we need to define what it's called a Vector Index, we'll use this to be able to know "how close" is our query from the games description.

This distance is calculated using vector math, and that's the power of the embeddings, they hold semantic meaning.

An index can be defined via the MongoDB Atlas dashboard, or programatically:

```
index_definition = {
    "name": "vector_index",
    "definition": {
        "fields": [
            {
                "type": "vector",
                "path": "embedding",
                "numDimensions": 1024,
                "similarity": "cosine"
            }
        ]
    }
}
collection.create_search_index(**index_definition)
```

A key field is the `numDimensions`, this has to be the same number as the dimensions generated by our embedding model. 

The `similarity` function, is what the index will use to define how "close" or "far" our vectors are from each other.

Now, it is time to perform the search. The full function is in the `chat.py` script, inside the `search_games` function.

But the gist is we perform a search, using our query_embedding. If you're familiar with the MongoDB aggregation pipeline, you can perform more complex filtering, using other fields in your documents.

```python
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
```

#### The Response
```python
llm_response = generate_response(user_query, games_found)
```

At this point, our search has returned some games. They should be related to the original query from the user.

We use the LLM, in this case ChatGPT, to assemble a response. And for that, we have to assemble a prompt.



## Before you go

Now you have the notion and basic knowledge about how RAG apps work, you can go ahead and explore more advanced concepts, implementations, and best practices such as security, observability, and optimization.

Some suggested reading:
- [What is retrieval-augmented generation?](https://www.mongodb.com/resources/basics/artificial-intelligence/retrieval-augmented-generation)
- [MongoDB GenAI Developer](https://learn.mongodb.com/learning-paths/mongodb-genai-developer)
- [AI Learning Hub](https://www.mongodb.com/resources/use-cases/artificial-intelligence)

If you have any question about this guide, feel free to reach out: [@ArturoNereu](https://x.com/ArturoNereu)