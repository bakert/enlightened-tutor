from fastapi import FastAPI
from nicegui import events, ui

import cards

app = FastAPI()

def init(fastapi_app: FastAPI) -> None:
    @ui.page('/')
    def show():
        async def search(e: events.ValueChangeEventArguments) -> None:
            results.clear()
            response = cards.get_card(e.value)
            print(response)
            if response:
                with results:
                    for format, score in response.playability.items():
                        display_score = round(score * 100)
                        ui.label(f'{display_score} {format}')
                        ui.linear_progress(value=score, show_value=False)

        cs = cards.get_card_names()
        ui.html('<h1>Enlightened Tutor</h1>')
        ui.input('Search', autocomplete=cs, on_change=search)
        results = ui.html('<div></div>')

    ui.run_with(
        fastapi_app,
        mount_path='/',
    )

init(app)
