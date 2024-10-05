# coding: utf-8
from ..str_converters import to_camel_case, to_snake_case


def test_snake_case():
    assert to_snake_case("") == ""
    assert to_snake_case("snakesOnAPlane") == "snakes_on_a_plane"
    assert to_snake_case("SnakesOnAPlane") == "snakes_on_a_plane"
    assert to_snake_case("SnakesOnA_Plane") == "snakes_on_a__plane"
    assert to_snake_case("snakes_on_a_plane") == "snakes_on_a_plane"
    assert to_snake_case("snakes_on_a__plane") == "snakes_on_a__plane"
    assert to_snake_case("IPhoneHysteria") == "i_phone_hysteria"
    assert to_snake_case("iPhoneHysteria") == "i_phone_hysteria"
    assert to_snake_case("_IPhoneHysteria") == "__i_phone_hysteria"
    assert to_snake_case("_File__") == "__file__"
    assert to_snake_case("potato01") == "potato01"
    assert to_camel_case("a") == "a"
    assert to_snake_case("A") == "a"
    assert to_snake_case("_A") == "__a"
    assert to_snake_case("_A0") == "__a0"
    assert to_snake_case("AAA") == "a_a_a"


def test_camel_case():
    assert to_camel_case("") == ""
    assert to_camel_case("snakesOnAPlane") == "snakesOnAPlane"
    assert to_camel_case("snakesOn_a_plane") == "snakesOnAPlane"
    assert to_camel_case("snakes_On_a_plane") == "snakesOnAPlane"
    assert to_camel_case("snakes_on_a_plane") == "snakesOnAPlane"
    assert to_camel_case("snakes_on_a__plane") == "snakesOnA_Plane"
    assert to_camel_case("i_phone_hysteria") == "iPhoneHysteria"
    assert to_camel_case("_i_phone_hysteria") == "IPhoneHysteria"
    assert to_camel_case("__i_phone_hysteria") == "_IPhoneHysteria"
    assert to_camel_case("field_i18n") == "fieldI18n"
    assert to_camel_case("__file__") == "_File__"
    assert to_camel_case("potato01") == "potato01"
    assert to_camel_case("potato_0_1") == "potato01"
    assert to_camel_case("a") == "a"
    assert to_camel_case("A") == "A"
    assert to_camel_case("_a") == "A"
    assert to_camel_case("__a") == "_A"
    assert to_camel_case("__a0") == "_A0"
    assert to_camel_case("a_a_a") == "aAA"
