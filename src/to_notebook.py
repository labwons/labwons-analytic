from typing import List
import os, secrets, string, json


def generate_id(length=8) -> str:
    alphabet = string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_cell(pys:List):
    files = []
    for _path, _, _files in os.walk(os.path.dirname(__file__)):
        for _file in _files:
            files.append(os.path.join(_path, _file))

    cells = []
    marked = []
    for py in pys:
        py = py.replace("/", os.path.sep)
        path = [file for file in files if file.endswith(py)]
        if len(path) != 1:
            raise FileExistsError(f'{py} Not Exist')
        path = path[0]
        part = path.replace(os.path.dirname(__file__), "")[1:]
        for n, elem in enumerate(part.split(os.path.sep), start=1):
            source = []
            for line in open(path, mode='r', encoding='utf-8').readlines():
                if 'if __name__' in line:
                    break
                source.append(line)
            if elem.endswith('.py'):
                cells.append({
                    "cell_type": "markdown",
                    "id": generate_id(),
                    "metadata": {},
                    "source": [
                        f'{"#" * n} {elem}'
                    ]
                })
                cells.append({
                    "cell_type": "code",
                    "execution_count": "null",
                    "id": generate_id(),
                    "metadata": {},
                    "outputs": {},
                    "source": source
                })
            else:
                if elem in marked:
                    continue
                cells.append({
                    "cell_type": "markdown",
                    "id": generate_id(),
                    "metadata": {},
                    "source": [
                        f'{"#" * n} {elem}'
                    ]
                })
                marked.append(elem)
    return cells

def generate_notebook(pys:List, filename:str):
    context = {
        "cells": generate_cell(pys),
        "metadata": {
            "colab": {
                "provenance": []
            },
            "kernelspec": {
                "display_name": "Python 3 (ipykernel)",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {
                    "name": "ipython",
                    "version": 3
                },
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.12.12"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }
    with open(filename, mode="w", encoding="utf-8") as file:
        file.write(
            json.dumps(context, indent=4)
        )

if __name__ == "__main__":
    pys = [
        "deco.py",
        "logger.py",
        "mailing.py",
        "bithumb/ticker.py",
        "bithumb/market.py",
        "indicator.py",
        "strategy.py",
        "tradingbook.py",
        "master.py"

    ]
    root = os.path.dirname(os.path.dirname(__file__))
    generate_notebook(pys, os.path.join(root, f"bot.ipynb"))