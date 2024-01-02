# Donder Hiroba API

This module provides a wrapper for the donderhiroba.jp API. The API are reverse-engineered from the official website.

**This project is not affiliated with donderhiroba.jp or BANDAI NAMCO in any way.**

## What can it do?

### Static Scripts

- Get the list of charts

### Active Scripts

- Get the score of a specific player (given the player ID) on a specific chart
- Get the favorite songs of a specific player (given the player ID)

This project is originally built for a Discord bot where players can check their scores. You can build your own parser and send other requests without worrying about expired cookies.

## Development Roadmap

| Status | Feature                                      | Date / Planned Date |
| ------ | -------------------------------------------- | ------------------- |
| ✅      | Kept-alive session                           | 2024.01             |
| ✅      | Get the list of charts                       | 2023 Q4             |
| ✅      | Get the score of a specific player           | 2024.01             |
| ❌      | Get the favorite songs of a player           | 2024.01             |
| ❌      | API endpoint server for score query          | 2024.02             |

## Installation

Clone / download the repository, then run:

```bash
pip install -U -r requirements.txt
```

If this is the first time you install [Playwright](https://github.com/microsoft/playwright), please run:

```bash
playwright install # or python3 -m playwright install
```

## Usage

You can check the block after `if __name__ == "__main__:` line in `taiko.py` and other files for some idea of how it works. This library is not intended for non-developers (for now). Given enough maintenance, this project may receive user-friendlier features in the future.

You can start with `specimen/song_list.json` & `specimen/config.json` by moving both files to the root of the project, and experiment around (maybe try `python3 taiko.py`?)

## License

I am not certain about the license to use, so I used [GPLv3](LICENSE) for now.