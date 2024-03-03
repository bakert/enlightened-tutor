import datetime
import re

from fastapi import FastAPI
from nicegui import events, ui

import cards

app = FastAPI()

def init(fastapi_app: FastAPI) -> None:
    @ui.page('/', title='Enlightened Tutor', favicon='🔍')
    def home():
        async def search(e: events.ValueChangeEventArguments) -> None:
            await show_card(e.value)

        async def paste(e: events.ValueChangeEventArguments) -> None:
            await show_cards(e.value)

        async def upload(e: events.UploadEventArguments) -> None:
            text = e.content.read().decode('utf-8')
            await show_cards(text)

        async def show_cards(text: str) -> None:
            cards_list = text.splitlines()
            for card in cards_list:
                card = re.sub(r'^\d+\s+', '', card) # Strip leading numbers in case this is a decklist or similar
                await show_card(card)

        async def show_card(card: str) -> None:
            c = cards.get_card(card)
            if not c:
                return
            with results:
                with ui.card():
                    ui.label(c.name)
                    for format, score in c.playability.items():
                        display_score = round(score * 100)
                        ui.label(f'{display_score} {format}')
                        ui.linear_progress(value=score, show_value=False)
                    if not c.playability:
                        ui.label('Not played in any format')

        with ui.header():
            ui.html('<h1>Enlightened Tutor</h1>').classes('text-3xl')
        with ui.tabs().classes('w-96') as tabs:
            search_tab = ui.tab('Search')
            paste_list_tab = ui.tab('Paste List')
            upload_file_tab = ui.tab('Upload File')
        with ui.tab_panels(tabs, value=search_tab):
            with ui.tab_panel(search_tab):
                cs = cards.get_card_names()
                ui.input(autocomplete=cs, on_change=search).classes('w-96')
            with ui.tab_panel(paste_list_tab):
                ui.textarea(on_change=paste ).classes('w-96')
            with ui.tab_panel(upload_file_tab):
                ui.upload(label='Upload File', auto_upload=True, on_upload=upload)
        results = ui.grid(columns=4)
        with ui.footer():
            ui.label(f'© {datetime.date.today().year} Thomas David Baker (bakert@gmail.com)').classes('text-xs')

    ui.run_with(
        fastapi_app,
        mount_path='/',
    )

init(app)
