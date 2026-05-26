import importlib
import pkgutil
import langchain

def find_class_in_package(package, class_name):
    for loader, module_name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, class_name):
                return module_name
        except ImportError:
            continue
    return None

if __name__ == "__main__":
    found_at = find_class_in_package(langchain, "AgentExecutor")
    if found_at:
        print(f"Found at: {found_at}")
    else:
        print("Not found in langchain")
