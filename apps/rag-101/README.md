![](images/banner.png)

This is a step-by-step guide on how to create a very basic RAG Application using MongoDB, VoyageAI, and OpenAI.


This sample is divided in two scripts, but the real RAG takes place in `chat.py`. The `save_game_collection.py` is a helper script that prepopulates our MongoDB Atlas collection with data.

Let's start by setting up our environment. 

```
> !pip install pymongo openai
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

The data was fetched from Wikipedia, and the embeddings were generated using [TODO].

```python
[TODO]
```

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

If you have any question about this guide, feel free to reach out: [@ArturoNereu](https://x.com/ArturoNereu)