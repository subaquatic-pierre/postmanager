# Examples

On this page you will find examples on how to create, update and delete posts with the use of **Flask** as a web server. The server uses standard REST API practices with the following endpoints and methods.

| ROUTE                    | METHOD | DESCRIPTION             |
| ------------------------ | ------ | ----------------------- |
| `/post`                  | GET    | Get all posts           |
| `/post`                  | POST   | Create new post         |
| `/post/<string:post_id>` | GET    | Get single post with ID |
| `/post/<string:post_id>` | PUT    | Update post with ID     |
| `/post/<string:post_id>` | DELETE | Delete post with ID     |

## Setup and Imports

```python title="routes.py"
import json
from flask import request, jsonify, Flask

app = Flask(__name__)

# Create manager instance used for all operations
post_manager = PostManager.setup_local()
```

## List Posts

```python title="routes.py"
@app.route("/post", methods=["GET", "POST"])
def list_post():
    if request.method == "GET":

        # Create empty list
        post_list = []

        # Get post index
        post_meta_data_list = post_manager.index


        # Append each post to post list
        for meta_data in post_meta_data_list:
            post = post_manager.get_by_id(meta_data["id"])

            post_list.append(post)

        return jsonify(post_list)

    ...
    # other code
    ...
```

## Create Post

!!! Media format is DataUrl as returned from
JavaScript FileReader.readAsDataURL()() method
[reference](https://developer.mozilla.org/en-US/docs/Web/API/FileReader/readAsDataURL)

```python title="routes.py"

@app.route("/post", methods=["GET","POST"])
def list_post():
    ...
    # other code
    ...

    elif request.method == "POST":
        # Get data from request
        form_data = json.loads(request.get_data().decode("utf-8"))
        content = form_data.get('content)
        meta_data = {
            'title': form_data.get('title),
            'category' : form_data.get('category'),
            'author': form_data.get('author')
        }

        # Create post
        new_post = post_manager.new_post(meta_data, content)

        # Add media if needed
        media = form_data.get('media')
        for media_name, media_bytes in media.items():
            new_post.add_media(media, media_bytes)

        # Save post
        post_manager.save_post(new_post)

        # Return post json
        return jsonify(new_post.to_json())
```

## Get Single Post

```python title="routes.py"
@main.route("/post/<string:post_id>", methods=["GET", "PUT", "DELETE"])
def single_post(post_id):
    if request.method == "GET":
        # Get post from storage
        post = post_manager.get_by_id(post_id)

        # Return json
        return jsonify(post.to_json())
```

## Update Post

```python title="routes.py"
@main.route("/post/<string:post_id>", methods=["GET", "PUT", "DELETE"])
def single_post(post_id):
    ...
    # other code
    ...

    elif request.method == "PUT":
        # Get post from storage
        post = post_manager.get_by_id(post_id)

        # Get data from request
        form_data = json.loads(request.get_data().decode("utf-8"))
        content = form_data.get('content)
        meta_data = {
            'title': form_data.get('title),
            'category' : form_data.get('category'),
            'author': form_data.get('author')
        }

        # Update post
        post.update_meta_data(meta_data)
        post.update_content(content)

        # Update media if needed
        # Currently any media with the same name is overwritten
        media = form_data.get('media')
        for media_name, media_bytes in media.items():
            new_post.add_media(media, media_bytes)

        # Save post
        post_manager.save_post(post)

        # Return post json
        return jsonify(post.to_json())

```

## Delete Post

```python title="routes.py"
@main.route("/post/<string:post_id>", methods=["GET", "PUT", "DELETE"])
def single_post(post_id):
    ...
    # other code
    ...

    elif request.method == "DELETE":
        post_manager.delete_post(post_id)

        data = {
            "deleted": True,
        }

        return jsonify(data)
```
