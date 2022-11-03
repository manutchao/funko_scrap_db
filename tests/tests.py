import sys
import os
sys.path.insert(0, './')
import pytest
import json
from PopScrapper import PopScrapper

pop = PopScrapper()

class TestClass:
    
    usecase_param = [
        ({"foo":"test", "bar":"test2"}, "foo", "test3", {"foo":"test3", "bar":"test2"}),
        ({"foo":"test", "bar":"test2"}, "bar", "test7", {"foo":"test", "bar":"test7"}),
        ({"foo":"test"}, "foo", "test", {"foo":"test"})
    ]
        
    usecase_json = [
        ({'name': 'Freddy Funko'}, "database.json", "w", "4", "utf-8", False, '{\n    "name": "Freddy Funko"\n}', True),
        ({'name': 'Freddy Funko'}, "newdatabase.json", "w", "8", "utf-8", False, '{\n        "name": "Freddy Funko"\n}', True)
    ]
    
    usecase_url = [
        ("http://google.fr", "google.fr", "http", "", "", "", ""),
        ("https://www.google.fr/search?q=meteo", "www.google.fr", "https", "/search", "", "q=meteo", "")
    ]
    
    usecase_url_build = [
        ("http://google.fr", {"meteo":"paris"}, "http://google.fr?meteo=paris"),
        ("https://www.hobbydb.com/marketplaces/hobbydb/subjects/pop-vinyl-series",{"filters[related_to]": "49962","filters[in_collection]": "all"} , "https://www.hobbydb.com/marketplaces/hobbydb/subjects/pop-vinyl-series?filters%5Brelated_to%5D=49962&filters%5Bin_collection%5D=all")
    ]
    
    @pytest.mark.parametrize("param,key, value, expected", usecase_param)
    def test_update_param_url(self, param,key, value, expected):
        assert(PopScrapper.update_param_url(param,key,value) == expected)
    
    @pytest.mark.parametrize("content, name_file, mode, nb_indent, encodage, ascii, expected, file_exist", usecase_json)
    def test_save_as_json(self, content, name_file, mode, nb_indent, encodage, ascii, expected, file_exist, tmp_path):
        path = tmp_path / name_file
        PopScrapper.save_as_json(content, str(path), mode, nb_indent, encodage,ascii)
        assert len(list(tmp_path.iterdir())) == 1
        assert os.path.exists(path) == file_exist
        assert path.read_text() == expected

    @pytest.mark.parametrize("url, netloc, scheme, path, params, query, fragment", usecase_url)
    def test_get_website_url_info(self, url, netloc, scheme, path, params, query, fragment):
        infos = PopScrapper.get_website_url_info(url)
        assert type(infos).__name__ is "ParseResult"
        assert infos.netloc == netloc
        assert infos.scheme == scheme
        assert infos.path == path
        assert infos.params == params
        assert infos.query == query
        assert infos.fragment == fragment

    @pytest.mark.parametrize("url, param, expected", usecase_url_build)
    def test_build_url(self, url, param, expected):
        assert PopScrapper.build_url(url, param) == expected