import pytest
from datahub.products import Products


def test_get_product():
    product = Products().get(198)
    assert product is not None


def test_get_product_invalid_id():
    id = -5
    p = Products()
    product = p.get(id)
    assert product is None


def test_get_all():
    p = Products()
    all_products = p.get_all()
    n = len(all_products)
    assert n > 1


def test_get_all_filter():
    p = Products()
    all_products = p.get_all(lon_min=-10, lon_max=0, lat_min=40, lat_max=50)
    n = len(all_products)
    assert n > 1


def test_get_all_filter_partial():
    p = Products()
    with pytest.raises(Exception):
        p.get_all(lon_min=-10, lon_max=0, lat_max=50)


def test_get_variables():
    p = Products()
    product = p.get(198)
    variables = p.get_variables(product)
    n = len(variables)
    assert n == 3


def test_get_variables_no_product():
    invalid_product = {}
    p = Products()
    with pytest.raises(Exception):
        p.get_variables(invalid_product)


def test_filter_name():
    match = Products().filter(name="datahubTests")
    assert match[0].id == 198


def test_filter_name_partial():
    match = Products().filter(name="datahub")
    assert match[0].id == 198


def test_filter_name_ko():
    match = Products().filter(name="datahub_ko")
    assert len(match) == 0


def test_filter_alias():
    match = Products().filter(alias="Cantabrico")

    assert len(match) > 0


def test_filter_alias_partial():
    match = Products().filter(alias="Cantab")
    assert len(match) > 1


def test_filter_alias_ko():
    match = Products().filter(alias="test_ko")

    assert len(match) == 0
