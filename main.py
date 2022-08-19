import itertools

from pathlib import Path
from typing import List, Tuple, Sequence

import click

from pydub import AudioSegment
from pydub.playback import play


def validate_sources(ctx, param, sources: Sequence[Tuple[Path, str]]):
    validated_sources = []

    for source in sources:
        path, cycle_str = source
        cycle_num_strs = cycle_str.split("-")

        try:
            cycle = tuple(int(s) for s in cycle_num_strs)
            validated_sources.append((path, cycle))
        except ValueError:
            raise click.BadParameter("format must be 'A-B-C-...-Z'")

    return validated_sources


@click.command()
@click.option(
    "--source", "sources", type=(Path, str), multiple=True, callback=validate_sources
)
@click.option('--test', is_flag=True)
def main(sources: List[Tuple[Path, str]], test: bool):
    feeds = []

    for path, cycle in sources:
        # Read each source directory path, and harvest all files inside it.
        subpaths = set(path.iterdir())

        cycle_iter = itertools.cycle(cycle)

        feeds.append((subpaths, cycle_iter))

    # List out subpaths according to the cycle rules.
    while True:
        any_processed = False

        for subpath_set, cycle_iter in feeds:
            n = next(cycle_iter)

            if not subpath_set:
                continue

            for _ in range(n):
                try:
                    subpath = subpath_set.pop()
                    any_processed = True
                    print(subpath)

                    song = AudioSegment.from_file(subpath)
                    if test:
                        FIVE_SECS = 5000
                        song = song[:FIVE_SECS]

                    play(song)
                except KeyError:
                    # Set is now empty.
                    break

        if not any_processed:
            break


if __name__ == "__main__":
    main()
