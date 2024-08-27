def subdict(dict, namespace):
    return {k[len(namespace)+1:]: v for k, v in dict.items() if k.startswith(f"{namespace}_")}
