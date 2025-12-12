from functools import wraps


def constrain(*allowed_args):
    """
    함수의 입력 인자가 1개이고 해당 인자의 가능한 값을 미리 정의

    사용 예시)
        @constrain("ICE", "HEV")
        def developerDB(engineSpec:str) -> None:
            ...

    :param allowed_args:

    :return:
    """
    allowed_set = set(allowed_args)
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            value = args[1] if len(args) > 1 else kwargs.get('value')

            if value not in allowed_set:
                raise ValueError(f"입력한 값: {value}은 입력 가능한 인자: {allowed_args}가 아닙니다")

            return func(*args, **kwargs)
        return wrapper
    return decorator