from fastapi import APIRouter, Depends, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from jinja2 import Template

from api.database import get_db
from api.services import get_moneycontrol_items_and_summary

router = APIRouter(prefix="/playground", tags=["GPT Playground"], include_in_schema=False)


HOME_TEMPLATE = Template(
    """
<html>
<head>
    <title>GPT Playground</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@1/css/pico.classless.min.css" />
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body hx-ext="loading-states">
    <header>
        <h1>Chat Gippity Playground</h1>
        <p>Here you can play around with the GPT-3.5 API by summarizing 3 most recent Moneycontrol articles.</p>
        <p>
        It costs ₹1 everytime you click the button, be considerate!<br/>
        Average response time is 40 seconds, be patient!
        </p>
    </header>
    <main>
        <section>
            <form hx-post="/playground" hx-target="#output">
                <input type="textarea" id="prompt" name="prompt" placeholder="Prompt" value="tldr;">
                <button data-loading-aria-busy>Chat Gippity!</button>
            </form>
        </section>
        <section>
            <div id="output"></div>
        </section>
    </main>
    
    <script src="https://unpkg.com/htmx.org@1.9.6"></script>
    <script src="https://unpkg.com/htmx.org/dist/ext/loading-states.js"></script>
</body>
</html>
"""
)


OUTPUT_TEMPLATE = Template(
    """
{% for item in data %}
<article>
    <header>
        <h4><a href="{{ item.link }}">{{ item.title }}</a></h4>
    </header>
    <details>
        <summary>Article Description</summary>
        <p>{{ item.description }}</p>
    </details>
    <details>
        <summary>Article Content</summary>
        <p>{{ item.content }}</p>
    </details>
    <details>
        <summary>Article Summary from Chat Gippity</summary>
        <p>{{ item.summary | replace("\n", "<br/>") }}</p>
    </details>
</article>
{% endfor %}

<article>
Total cost is ₹{{ data | map(attribute='cost') | sum }}
</article>
"""
)


@router.get("")
def playground():
    return HTMLResponse(HOME_TEMPLATE.render())


@router.post("")
async def playground2(prompt: str = Form(), db: Session = Depends(get_db)):
    data = await get_moneycontrol_items_and_summary(db, prompt, count=3)
    return HTMLResponse(OUTPUT_TEMPLATE.render(data=data))
