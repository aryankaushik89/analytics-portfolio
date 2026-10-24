"""Execute the learning notebook in a fresh Python namespace."""

import ast
import base64
import contextlib
import io
from pathlib import Path

import nbformat


def execute_code(source, namespace):
    tree = ast.parse(source)
    final_expression = None
    if tree.body and isinstance(tree.body[-1], ast.Expr):
        final_expression = ast.Expression(tree.body.pop().value)
    stdout = io.StringIO()
    outputs = []
    with contextlib.redirect_stdout(stdout):
        if tree.body:
            exec(compile(tree, "<notebook>", "exec"), namespace)
        value = eval(compile(final_expression, "<notebook>", "eval"), namespace) if final_expression else None
    if stdout.getvalue():
        outputs.append(nbformat.v4.new_output("stream", name="stdout", text=stdout.getvalue()))
    if value is not None:
        data = {"text/plain": repr(value)}
        if hasattr(value, "_repr_html_"):
            data["text/html"] = value._repr_html_()
        outputs.append(nbformat.v4.new_output("execute_result", data=data))
    plt = namespace.get("plt")
    if plt is not None:
        for number in plt.get_fignums():
            figure = plt.figure(number)
            image = io.BytesIO()
            figure.savefig(image, format="png", dpi=120, bbox_inches="tight")
            outputs.append(nbformat.v4.new_output("display_data", data={"image/png": base64.b64encode(image.getvalue()).decode("ascii")}))
        plt.close("all")
    return outputs


def main():
    notebook_path = Path(__file__).resolve().parents[1] / "notebooks" / "ask_your_metrics.ipynb"
    notebook = nbformat.read(notebook_path, as_version=4)
    namespace = {"__name__": "__main__"}
    count = 0
    for cell in notebook.cells:
        if cell.cell_type != "code":
            continue
        count += 1
        cell.execution_count = count
        cell.outputs = execute_code(cell.source, namespace)
    notebook.metadata["execution"] = {"method": "Fresh direct Python namespace; no external Jupyter kernel", "code_cells": count}
    nbformat.write(notebook, notebook_path)
    print(f"Executed {count} code cells in {notebook_path}")


if __name__ == "__main__":
    main()
