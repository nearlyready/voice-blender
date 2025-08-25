import openpyxl

def batch_call(f, arg_dicts):
    results = []
    for kwargs in arg_dicts:
        print(f"Calling {f.__name__} with arguments: {kwargs}")
        results.append(f(**kwargs))  # unpack dict into arguments
    return results


def batch_call_from_xlsx(f, xlsx_path):
    arg_dicts = extract_arg_dicts_from_xlsx(xlsx_path)

    # Call the batch_call function with the list of dictionaries
    return batch_call(f, arg_dicts)


import subprocess

def cli_call(base_cmd, arg_dict):
    """
    Run a command-line tool with parameters from a dictionary.
    - base_cmd: list, e.g. ["python", "tools/infer_cli.py"]
    - arg_dict: dict of {param_name: value}
    """
    cmd = list(base_cmd)  # copy base
    for k, v in arg_dict.items():
        if v is None:  
            continue  # skip empty args
        # prepend '--' for flags (skip if already starts with '-')
        if not str(k).startswith("-"):
            cmd.append(f"--{k}")
        else:
            cmd.append(str(k))
        cmd.append(str(v))  # ensure value is string
    
    print(f"Running command: {' '.join(cmd)}")
    # Run the command
    subprocess.run(cmd, check=True)

def batch_cli_call(base_cmd, arg_dicts):
    """
    Run the same CLI multiple times with different parameters.
    """
    for params in arg_dicts:
        cli_call(base_cmd, params)



def extract_arg_dicts_from_xlsx(xlsx_path):
    # Load the workbook and select the active worksheet
    workbook = openpyxl.load_workbook(xlsx_path)
    sheet = workbook.active

    # Read the header row to get parameter names
    headers = [cell.value for cell in sheet[1]]
    arg_dicts = []
    for row in sheet.iter_rows(min_row=2, values_only=True):
        kwargs = {headers[i]: value for i, value in enumerate(row)}
        arg_dicts.append(kwargs)

    return arg_dicts


def batch_cli_call_from_xlsx(base_cmd, xlsx_path):
    """
    Run the same CLI multiple times with different parameters from an XLSX file.
    """
    arg_dicts = extract_arg_dicts_from_xlsx(xlsx_path)
    batch_cli_call(base_cmd, arg_dicts)


if __name__ == "__main__":
    # Example usage
    # def example_function(a, b, c):
    #     return a + b + c

    # arg_dicts = [
    #     {"a": 1, "b": 2, "c": 3},
    #     {"a": 4, "b": 5, "c": 6},
    #     {"a": 7, "b": 8, "c": 9},
    # ]

    # results = batch_call(example_function, arg_dicts)
    # print("Batch call results:", results)

    # xlsx_path = "tests/batch_call/test.xlsx"
    # xlsx_results = batch_call_from_xlsx(example_function, xlsx_path)
    # print("Batch call results from XLSX:", xlsx_results)

    # base_cmd = ["echo"]

    # jobs = [
    #     {"message": "Hello World"},
    #     {"message": "RunPod CLI test"},
    # ]

    # batch_cli_call(base_cmd, jobs)

    # cli_xlsx_path = "tests/batch_call/cli_test.xlsx"
    # batch_cli_call_from_xlsx(base_cmd, cli_xlsx_path)

    import inference
    import batch_inference
    xlsx_path = "inference_jobs_blends.xlsx"
    xlsx_results = batch_call_from_xlsx(batch_inference.run_pipeline, xlsx_path)
    print("Batch call results from XLSX:", xlsx_results)

    # import blending
    # xlsx_path = "blending_jobs.xlsx"
    # xlsx_results = batch_call_from_xlsx(blending.run_pipeline, xlsx_path)
    # print("Batch call results from XLSX:", xlsx_results)