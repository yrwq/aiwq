from urllib.request import urlretrieve
import subprocess
import platform
import asyncio
import psutil    
import stat
import os
from subprocess import Popen, PIPE, STDOUT
try:
    from subprocess import DEVNULL # py3k
except ImportError:
    import os
    DEVNULL = open(os.devnull, 'wb')

ollama_exec_path = "./ollama"
ollama_version = "v0.1.22"
ollama_model = "orca-mini"

urls = {
    "darwin": f"https://github.com/ollama/ollama/releases/download/{ollama_version}/ollama-darwin",
    "linux-x86_64": f"https://github.com/ollama/ollama/releases/download/{ollama_version}/ollama-linux-amd64",
    "linux-arm": f"https://github.com/ollama/ollama/releases/download/{ollama_version}/ollama-linux-arm64"
}

async def check_exec(file_path) -> bool:
    """
    check if a file is executable
    return True if so
    """
    return os.access(file_path, os.X_OK)

async def ollama_download():
    """
    downloads ollama binary for the desired os/arch
    """

    sys_plat = platform.system()
    sys_arch = platform.machine()

    print(f"downloading ollama version {ollama_version}")

    match sys_plat:
        case "Darwin":
            urlretrieve(urls["darwin"], ollama_exec_path)
        case "Linux":
            match sys_arch:
                case "arm64":
                    urlretrieve(urls["linux-arm"], ollama_exec_path)
                case "x86_64":
                    urlretrieve(urls["linux-arm"], ollama_exec_path)
                case _:
                    print("sorry your platform is not supported by ollama")
                    exit(1)
        case _:
            print("sorry your platform is not supported by ollama")
            exit(1)
            

    print("ollama downloaded successfully")

async def ollama_serve():
    p = Popen([ollama_exec_path, "serve"], stdin=PIPE, stdout=DEVNULL, stderr=STDOUT)
    # sleep 1 just in case before pulling/running
    await asyncio.sleep(1)
    
    return p

async def ollama_check_models() -> bool :
    """
    Check if any model is already pulled
    Returns true if a model is already installed
    """
    result = subprocess.run([ollama_exec_path, "list"], stdout=subprocess.PIPE)
    pretty_result = result.stdout.decode("utf-8")

    lines = pretty_result.splitlines()
    if len(lines) != 1 : return True
    else: return False

async def ollama_pull_model(model):
    result = subprocess.run([ollama_exec_path, "pull", model], stdout=subprocess.PIPE)
    pretty_result = result.stdout.decode("utf-8")
    print(pretty_result)

async def ollama_run_model(model):
    p = Popen([ollama_exec_path, "serve"], stdin=PIPE, stdout=DEVNULL, stderr=STDOUT)

async def main():
    # check if ollama executable is available
    ollama_available = os.path.isfile(ollama_exec_path)
    if ollama_available == False:
        # download if not
        await ollama_download()
        # check if its executable
        is_executable = await check_exec(ollama_exec_path)
        # make it executable if not
        if is_executable == False:
            # get current permissions
            st = os.stat(ollama_exec_path)
            # make it executable
            os.chmod(ollama_exec_path, st.st_mode | stat.S_IEXEC)

    # check if ollama is already running
    if "ollama" not in (p.name() for p in psutil.process_iter()):
        await ollama_serve()

    model_installed = await ollama_check_models()

    if model_installed == False:
        await ollama_pull_model(ollama_model)

    await ollama_run_model(ollama_model)

asyncio.run(main())
