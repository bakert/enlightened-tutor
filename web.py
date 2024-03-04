import datetime
import re

from fastapi import FastAPI
from nicegui import events, ui
import nicegui

import cards

app = FastAPI()


def init(fastapi_app: FastAPI) -> None:
    @ui.page("/", title="Enlightened Tutor", favicon="🔍")  # type: ignore[misc]
    def home() -> None:
        showing: dict[str, nicegui.elements.card.Card] = {}

        async def search(e: events.ValueChangeEventArguments) -> None:
            await show_card(e.value)

        async def paste(e: events.ValueChangeEventArguments) -> None:
            await show_cards(e.value)

        async def upload(e: events.UploadEventArguments) -> None:
            text = e.content.read().decode("utf-8")
            await show_cards(text)

        async def show_cards(text: str) -> None:
            cards_list = text.splitlines()[0:50]  # Limit rather than fail entirely. Later, pagination.
            for card in cards_list:
                # Strip leading numbers in case this is a decklist or similar
                card = re.sub(r"^\d+\s+", "", card)
                await show_card(card, show_warnings=True)

        async def show_card(card: str, show_warnings: bool = False) -> None:
            c = cards.get_card(card)
            if not c:
                if card and show_warnings:
                    ui.notify(f"Card not found: {card}", type="warning")
                return
            with results:
                if c.name not in showing:
                    card_ui = make_card(c)
                    showing[c.name] = card_ui
                showing[c.name].move(target_index=0)

        with ui.header():
            ui.html("<h1>Enlightened Tutor</h1>").classes("text-3xl")
        with ui.tabs().classes("w-96") as tabs:
            search_tab = ui.tab("Search")
            paste_list_tab = ui.tab("Paste List")
            upload_file_tab = ui.tab("Upload File")
        with ui.tab_panels(tabs, value=search_tab):
            with ui.tab_panel(search_tab):
                cs = cards.get_card_names()
                ui.input(autocomplete=cs, on_change=search).classes("w-96").props("autofocus")
            with ui.tab_panel(paste_list_tab):
                ui.textarea(on_change=paste).classes("w-96")
            with ui.tab_panel(upload_file_tab):
                ui.upload(label="Upload File", auto_upload=True, on_upload=upload)
        results = ui.row()
        with ui.footer():
            ui.link("Tournament results from mtgtop8.com", "https://www.mtgtop8.com/").classes("text-xs text-white")
            ui.link("Cube data from cubecobra.com", "https://cubecobra.com/").classes("text-xs text-white")
            ui.label(f"© {datetime.date.today().year} Thomas David Baker (bakert@gmail.com)").classes("text-xs")

    ui.run_with(
        fastapi_app,
        mount_path="/",
    )


def display_score(score: float) -> int:
    return round(score * 100)


def make_card(c: cards.Card) -> nicegui.elements.card.Card:
    highest = display_score(max(c.playability.values(), default=0))
    with ui.card().classes("w-80") as card_ui:
        ui.image(scryfall_img_url(c.name)).classes("h-32 overflow-hidden")
        with ui.row().classes("w-full"):
            ui.html(f"<h2>{c.name}</h2>").classes("text-xl")
            ui.space()
            ui.html(f"<h2>{highest}</h2>").classes("text-xl")
        for (format_name, format_code), score in c.playability.items():
            with ui.link(target=make_link(format_code, c.name)).classes("w-full no-underline hover:underline"):
                with ui.row():
                    ui.label(f"{format_name}")
                    ui.space()
                    ui.label(f"{display_score(score)}")
                ui.linear_progress(value=score, show_value=False)
        if not c.playability:
            ui.label("Not played in any format")
    return card_ui


def make_link(format_code: str, card: str) -> str:
    if format_code in ["CPOP", "CELO"]:
        return f"https://cubecobra.com/tool/card/{card}"
    return f"https://mtgtop8.com/search?MD_check=1&SB_check=1&format={format_code}&cards={card}"


def scryfall_img_url(card: str) -> str:
    return f"https://api.scryfall.com/cards/named?exact={card}&format=image&version=art_crop"


init(app)
