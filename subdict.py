def subdict(dictionary, namespace):
    return {k[len(namespace)+1:]: v for k, v in dictionary.items() if k.startswith(f"{namespace}_")}
