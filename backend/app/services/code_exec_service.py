"""
Restricted Python code execution against a loaded dataset.

SECURITY NOTE: This executes user-provided Python. It is sandboxed by:
  - stripping dangerous builtins (open, __import__, exec, eval, compile, etc.)
  - only exposing pandas/numpy/sklearn + the dataset as `df`
  - capturing stdout instead of allowing arbitrary I/O
  - running with a wall-clock timeout in a subprocess-free (single process)
    context suitable for a trusted/internal deployment.
For a public multi-tenant deployment, run this inside a fully isolated
container/gVisor/firecracker sandbox instead of in-process exec().
"""
import io
import contextlib
import multiprocessing
import traceback
import pandas as pd
import numpy as np

SAFE_BUILTINS = {
    "len": len, "range": range, "min": min, "max": max, "sum": sum,
    "sorted": sorted, "list": list, "dict": dict, "set": set, "tuple": tuple,
    "str": str, "int": int, "float": float, "bool": bool, "round": round,
    "enumerate": enumerate, "zip": zip, "map": map, "filter": filter,
    "abs": abs, "print": print, "type": type, "isinstance": isinstance,
}


def _worker(code: str, df_json: str, queue):
    try:
        df = pd.read_json(io.StringIO(df_json), orient="split")
        local_vars = {"df": df, "pd": pd, "np": np}
        try:
            from sklearn import preprocessing, cluster, decomposition, linear_model
            local_vars["preprocessing"] = preprocessing
            local_vars["cluster"] = cluster
            local_vars["decomposition"] = decomposition
            local_vars["linear_model"] = linear_model
        except Exception:
            pass

        stdout_buf = io.StringIO()
        with contextlib.redirect_stdout(stdout_buf):
            exec(code, {"__builtins__": SAFE_BUILTINS}, local_vars)

        result_df = local_vars.get("result")
        output = {
            "stdout": stdout_buf.getvalue(),
            "error": None,
            "result_preview": None,
            "result_shape": None,
        }
        if isinstance(result_df, pd.DataFrame):
            output["result_preview"] = result_df.head(200).to_dict(orient="records")
            output["result_shape"] = list(result_df.shape)
            output["result_columns"] = [str(c) for c in result_df.columns]
        elif result_df is not None:
            output["result_preview"] = str(result_df)
        queue.put(output)
    except Exception:
        queue.put({"stdout": "", "error": traceback.format_exc(), "result_preview": None, "result_shape": None})


def run_code(df: pd.DataFrame, code: str, timeout: int = 8) -> dict:
    df_json = df.to_json(orient="split")
    ctx = multiprocessing.get_context("spawn")
    queue = ctx.Queue()
    p = ctx.Process(target=_worker, args=(code, df_json, queue))
    p.start()
    p.join(timeout)
    if p.is_alive():
        p.terminate()
        p.join()
        return {"stdout": "", "error": f"Execution timed out after {timeout}s", "result_preview": None, "result_shape": None}
    if not queue.empty():
        return queue.get()
    return {"stdout": "", "error": "No output produced (process exited unexpectedly)", "result_preview": None, "result_shape": None}
