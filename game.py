import itertools
import js
import math
import random


class Tile:
    def __init__(self, txt, show_back, clicked):
        self.txt = txt
        self.show_back = show_back
        self.callback = clicked
        self._create_view()
        self.update_view()

    def update_view(self):
        if self.show_back:
            self.view_inner.classList.add("tile-show-back")
        else:
            self.view_inner.classList.remove("tile-show-back")

    def _create_view(self):
        self.view = js.document.createElement("div")
        self.view.classList.add("tile")
        self.view.addEventListener("click", self._callback)
        self.view_inner = js.document.createElement("div")
        self.view_inner.classList.add("tile-inner")
        front = js.document.createElement("div")
        front.classList.add("tile-front")
        back = js.document.createElement("div")
        back.classList.add("tile-back")
        back.innerText = self.txt
        self.view_inner.appendChild(front)
        self.view_inner.appendChild(back)
        self.view.appendChild(self.view_inner)

    def _callback(self, el):
        self.callback(self)


class Stats:
    def __init__(self, tile_count):
        self._tile_count = tile_count
        self._tiles_clicked = 0
        self._incorrect_matches = 0
        self._correct_matches = 0
        # A match is lucky if one of both tiles have not been seen before
        self._lucky_matches = 0
        # Memory matches are ones where both tiles have been seen before
        self._memory_matches = 0
        # Memory failures are when both tiles have been seen before and
        # an incorrect match happens
        self._memory_failures = 0
        self._tiles_seen = set()
        self._create_view()

    def tile_clicked(self):
        self._tiles_clicked += 1
        self._update_view()

    def incorrect_match(self, tile1, tile2):
        self._incorrect_matches += 1
        if tile2 in self._tiles_seen:
            self._memory_failures += 1
        self._tiles_seen.add(tile1)
        self._tiles_seen.add(tile2)
        self._update_view()

    def correct_match(self, tile1, tile2):
        self._correct_matches += 1
        if tile2 in self._tiles_seen:
            self._memory_matches += 1
        else:
            self._lucky_matches += 1
        self._tiles_seen.add(tile1)
        self._tiles_seen.add(tile2)
        self._update_view()

    def _create_view(self):
        self.view = js.document.createElement("div")
        self.view.classList.add("stats")
        self.tiles_clicked_view = self._create_stat()
        self.accuracy_view = self._create_stat()
        self.memory_accuracy_view = self._create_stat()
        self.luck_view = self._create_stat()
        self._update_view()

    def _create_stat(self):
        stat = js.document.createElement("div")
        stat.classList.add("stat")
        self.view.appendChild(stat)
        return stat

    def _update_view(self):
        self.tiles_clicked_view.innerText = f"Tiles Clicked: {self._tiles_clicked}"
        guesses = self._incorrect_matches + self._correct_matches
        accuracy = 0
        if guesses > 0:
            accuracy = 100 * self._correct_matches / guesses
        self.accuracy_view.innerText = f"Accuracy: {accuracy:.0f}%"
        memory_accuracy = 100
        memory_guesses = self._memory_matches + self._memory_failures
        if memory_guesses > 0:
            memory_accuracy = 100 * self._memory_matches / memory_guesses
        self.memory_accuracy_view.innerText = f"Memory Accuracy: {memory_accuracy:.0f}%"
        min_guesses = self._tile_count
        luck = 100 * self._lucky_matches / min_guesses
        self.luck_view.innerText = f"Luck: {luck:.0f}%"


class Board:
    def __init__(self, tile_values, stats):
        tile_values.extend(tile_values)
        random.shuffle(tile_values)
        num_cols = int(math.floor(math.sqrt(len(tile_values))))
        num_rows = int(math.ceil(len(tile_values) / num_cols))
        assert num_cols * num_rows >= len(tile_values)
        self.cols = num_cols
        self.tiles = [
            Tile(value, show_back=False, clicked=self.tile_clicked)
            for value in tile_values
        ]
        self.clicked = []
        self.timeout_set = False
        self.stats = stats
        self._create_view()

    def tile_clicked(self, clicked_tile):
        if clicked_tile.show_back:
            # Don't flip tiles that are already showing the back
            return
        self.stats.tile_clicked()
        clicked_tile.show_back = True
        clicked_tile.update_view()
        if len(self.clicked) == 2:
            # Clear the previously selected non-matching tiles
            for tile in self.clicked:
                tile.show_back = False
                tile.update_view()
            self.clicked = []
            self.clicked.append(clicked_tile)
        elif len(self.clicked) == 1:
            if self.clicked[0].txt == clicked_tile.txt:
                # The selected tile matches the previous selection
                self.clicked[0].show_back = True
                self.clicked[0].update_view()
                self.stats.correct_match(self.clicked[0], clicked_tile)
                self.clicked = []
            else:
                self.clicked.append(clicked_tile)
                self.stats.incorrect_match(self.clicked[0], clicked_tile)
                if not self.timeout_set:
                    js.console.log("setting timeout")
                    js.window.setTimeout(self.timeout_callback, 750)
                    self.timeout_set = True
        else:
            # First tile selected, wait for a second to check for a match
            self.clicked.append(clicked_tile)

    def _create_view(self):
        self.view = js.document.createElement("div")
        self.view.classList.add("board")
        self.view.style.gridTemplateColumns = f"repeat({self.cols}, 250px)"
        for tile in self.tiles:
            self.view.appendChild(tile.view)

    def timeout_callback(self):
        if len(self.clicked) == 2:
            for tile in self.clicked:
                tile.show_back = False
                tile.update_view()
            self.clicked = []
        self.timeout_set = False


tiles = [
    "Apple",
    "Orange",
    "Banana",
    "Kiwi",
    "Peach",
    "Pear",
    "Blueberry",
    "Blackberry",
]

stats = Stats(len(tiles))
board = Board(tiles, stats)
loading_icon = js.document.getElementById("loading-icon")
loading_icon.parentNode.removeChild(loading_icon)
content = js.document.getElementById("content")
content.appendChild(stats.view)
content.appendChild(board.view)
