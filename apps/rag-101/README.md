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

Our RAG implementation is pretty simple, it has a main function with three parts:

```python
user_query = "recommend a game that is a shooter in space"
```

```python
games_found = search_games(user_query)
```

```python
llm_response = generate_response(user_query, games_found)
```

## Before you go

Now you have the notion and basic knowledge about how RAG apps work, you can go ahead and explore more advanced concepts, implementations, and best practices such as security, observability, and optimization.

If you have any question about this guide, feel free to reach out: [@ArturoNereu](https://x.com/ArturoNereu)