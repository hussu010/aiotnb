:orphan:

.. _logging_setup:

Setting Up Logging
==================
Example:

.. code:: python

    import logging

    logging.basicConfig(level=logging.INFO)

    @lru_cache(maxsize=None)
    def has_exactly_one_list_item(toc: str) -> bool:
        """Check if the toc has exactly one list item."""
        assert toc

        soup = BeautifulSoup(toc, "html.parser")
        if len(soup.find_all("li")) == 1:
            return True

        return False