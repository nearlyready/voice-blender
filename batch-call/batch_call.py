import openpyxl
import csv
import subprocess


def extract_arg_dicts_from_xlsx(xlsx_path):
    """
    Extract argument dictionaries from an Excel file.
    
    Args:
        xlsx_path (str): The file path to the Excel (.xlsx) file containing parameter data.
                         The file should have parameter names in the first row as headers,
                         with each subsequent row representing a set of parameters.
    
    Returns:
        list: A list of dictionaries, where each dictionary contains parameter names as keys
              and their values from the Excel file.
    """
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

def extract_arg_dicts_from_csv(csv_path):
    """
    Extract argument dictionaries from a CSV file.
    
    Args:
        csv_path (str): The file path to the CSV file containing parameter data.
                        The file should have parameter names in the first row as headers,
                        with each subsequent row representing a set of parameters.
    
    Returns:
        list: A list of dictionaries, where each dictionary contains parameter names as keys
              and their values from the CSV file.
    """
    arg_dicts = []
    with open(csv_path, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            arg_dicts.append(row)
    return arg_dicts
#--------

def cli_call(base_cmd, arg_dict):
    """
    Run a command-line tool with parameters from a dictionary.
    
    Args:
        base_cmd (list): Base command to run as a list of strings.
                         Example: ["python", "tools/infer_cli.py"]
        arg_dict (dict): Dictionary of parameter names and values to be passed to the command.
                         Keys are parameter names (without '--' prefix) and values are the parameter values.
                         Example: {"input": "file.wav", "output": "result.wav"}
                         If a value is None, the parameter will be skipped.
    
    Returns:
        None: The function runs the command but does not return any value.
              The command output will be displayed in the console.
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
    Run the same CLI command multiple times with different parameters.
    
    Args:
        base_cmd (list): Base command to run as a list of strings.
                         Example: ["python", "tools/infer_cli.py"]
        arg_dicts (list): A list of dictionaries, where each dictionary contains parameter names as keys
                          and their values to be passed to the command for each separate call.
                          Example: [{"input": "file1.wav"}, {"input": "file2.wav"}]
    
    Returns:
        None: The function runs the commands but does not return any value.
              The command outputs will be displayed in the console.
    """
    for params in arg_dicts:
        cli_call(base_cmd, params)

def batch_call(f, arg_dicts):
    """
    Call a function multiple times with different parameters and collect the results.
    
    Args:
        f (callable): The function to call repeatedly. 
                      This function should accept keyword arguments that match the keys in arg_dicts.
        arg_dicts (list): A list of dictionaries, where each dictionary contains parameter names as keys
                          and their values to be passed to the function for each separate call.
                          Example: [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
    
    Returns:
        list: A list containing the return values from each function call.
              The results are in the same order as the input arg_dicts.
    """
    results = []
    for kwargs in arg_dicts:
        print(f"Calling {f.__name__} with arguments: {kwargs}")
        results.append(f(**kwargs))  # unpack dict into arguments
    return results

# -------

def batch_cli_call_from_xlsx(base_cmd, xlsx_path):
    """
    Run a CLI command multiple times with parameters from an Excel file.
    
    Args:
        base_cmd (list): Base command to run as a list of strings.
                         Example: ["python", "tools/infer_cli.py"]
        xlsx_path (str): The file path to the Excel (.xlsx) file containing parameter data.
                         The file should have parameter names in the first row as headers,
                         with each subsequent row representing a set of parameters.
    
    Returns:
        None: The function runs the commands but does not return any value.
              The command outputs will be displayed in the console.
    """
    arg_dicts = extract_arg_dicts_from_xlsx(xlsx_path)
    return batch_cli_call(base_cmd, arg_dicts)

def batch_call_from_xlsx(f, xlsx_path):
    """
    Call a function multiple times with parameters from an Excel file and collect the results.
    
    Args:
        f (callable): The function to call repeatedly.
                      This function should accept keyword arguments that match the column headers in the Excel file.
        xlsx_path (str): The file path to the Excel (.xlsx) file containing parameter data.
                         The file should have parameter names in the first row as headers,
                         with each subsequent row representing a set of parameters.
    
    Returns:
        list: A list containing the return values from each function call.
              The results are in the same order as the rows in the Excel file.
    """
    arg_dicts = extract_arg_dicts_from_xlsx(xlsx_path)
    return batch_call(f, arg_dicts)

def batch_cli_call_from_csv(base_cmd, csv_path):
    """
    Run a CLI command multiple times with parameters from a CSV file.
    
    Args:
        base_cmd (list): Base command to run as a list of strings.
                         Example: ["python", "tools/infer_cli.py"]
        csv_path (str): The file path to the CSV file containing parameter data.
                        The file should have parameter names in the first row as headers,
                        with each subsequent row representing a set of parameters.
    
    Returns:
        None: The function runs the commands but does not return any value.
              The command outputs will be displayed in the console.
    """
    arg_dicts = extract_arg_dicts_from_csv(csv_path)
    return batch_cli_call(base_cmd, arg_dicts)

def batch_call_from_csv(f, csv_path):
    """
    Call a function multiple times with parameters from a CSV file and collect the results.
    
    Args:
        f (callable): The function to call repeatedly.
                      This function should accept keyword arguments that match the column headers in the CSV file.
        csv_path (str): The file path to the CSV file containing parameter data.
                        The file should have parameter names in the first row as headers,
                        with each subsequent row representing a set of parameters.
    
    Returns:
        list: A list containing the return values from each function call.
              The results are in the same order as the rows in the CSV file.
    """
    arg_dicts = extract_arg_dicts_from_csv(csv_path)
    return batch_call(f, arg_dicts)

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

