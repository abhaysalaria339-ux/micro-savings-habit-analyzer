DEFAULT_PAGE_LIMIT = 50
MAX_PAGE_LIMIT = 100
MAX_PAGE_OFFSET = 10_000


def validate_pagination(*, limit: int, offset: int) -> None:
    if limit < 1:
        raise ValueError("Pagination limit must be greater than or equal to 1.")

    if limit > MAX_PAGE_LIMIT:
        raise ValueError(f"Pagination limit must be less than or equal to {MAX_PAGE_LIMIT}.")

    if offset < 0:
        raise ValueError("Pagination offset must be greater than or equal to 0.")

    if offset > MAX_PAGE_OFFSET:
        raise ValueError(f"Pagination offset must be less than or equal to {MAX_PAGE_OFFSET}.")
